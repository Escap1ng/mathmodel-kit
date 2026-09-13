#!/usr/bin/env python3
"""strip_invisible.py — Layer A 不可见 Unicode / 零宽字符清理器（论文交付门禁）。

字符集与保护逻辑移植自 guillaumemeyer/watermarks-remover 的 Layer A
（service/scripts/text_unicode.py）：零宽家族（ZWSP/ZWNJ/ZWJ/WJ/ZWNBSP）、
bidi 与格式控制、tag 字符（U+E0001–U+E007F）、变体选择符、非字符、
保留不可见字符与私用区。默认对中文/拉丁学术文本全部剥离，
仅保留 CJK 表意文字后的 IVD（表意文字变体选择符 U+FE00–U+FE0F / U+E0100+）
作为合法正字保护（与 Layer A 同源规则）。

支持格式：
  .docx                          zip 内全部 XML part：文本节点 + 数字字符引用实体
  .pdf                           ToUnicode 映射定位隐形码 → 内容流 hex 清理 + 元数据清理
  .tex / .bib / .md / .txt 等    文本级清理（含文件头 BOM）

用法：
  python strip_invisible.py FILE...                 # 只检测，发现即退出 1
  python strip_invisible.py --clean FILE...         # 就地清理（默认留 .bak），清理后复检
  python strip_invisible.py --clean --no-backup ...

退出码：0=全部干净；1=存在（或清理后残留）不可见字符；2=用法/依赖错误。
PDF 模式需要 PyMuPDF（pip install pymupdf）；tex/docx 模式仅用标准库。
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
import zipfile
from collections import Counter
from pathlib import Path

# ---------- Layer A 字符集（源自 watermarks-remover text_unicode.py） ----------


def _ranges(*pairs: tuple[int, int]) -> frozenset[int]:
    return frozenset(c for lo, hi in pairs for c in range(lo, hi + 1))


STRIP_CODEPOINTS = frozenset(
    {
        0x00AD,  # soft hyphen
        0x034F,  # combining grapheme joiner
        0x061C,  # Arabic letter mark
        0x115F, 0x1160, 0x3164, 0xFFA0,  # Hangul fillers
        0x17B4, 0x17B5,  # Khmer inherent vowels
        0x180B, 0x180C, 0x180D, 0x180E, 0x180F,  # Mongolian FVS / MVS
        0x200B, 0x200C, 0x200D,  # ZWSP / ZWNJ / ZWJ
        0x200E, 0x200F,  # LRM / RLM
        0x202A, 0x202B, 0x202C, 0x202D, 0x202E,  # bidi embeddings / overrides
        0x2060, 0x2061, 0x2062, 0x2063, 0x2064,  # word joiner / invisible operators
        0x2066, 0x2067, 0x2068, 0x2069,  # bidi isolates
        0x206A, 0x206B, 0x206C, 0x206D, 0x206E, 0x206F,
        0xFEFF,  # BOM / ZWNBSP
        0xFFF9, 0xFFFA, 0xFFFB,  # interlinear annotation
    }
    | _ranges((0xFE00, 0xFE0F))  # variation selectors 1–16
)

VS_SUPPLEMENT = _ranges((0xE0100, 0xE01EF))  # VS17–VS256
TAG_CHARS = _ranges((0xE0001, 0xE007F))  # tag 字符（隐写载体）
RESERVED_IGNORABLE = (
    frozenset({0x2065, 0xE0000})
    | _ranges((0xFFF0, 0xFFF8), (0xE0080, 0xE00FF), (0xE01F0, 0xE0FFF))
)
PRIVATE_USE = _ranges((0xE000, 0xF8FF), (0xF0000, 0xFFFFD), (0x100000, 0x10FFFD))


def _is_noncharacter(cp: int) -> bool:
    return 0xFDD0 <= cp <= 0xFDEF or (cp & 0xFFFE) == 0xFFFE


def is_cjk_ideograph(cp: int) -> bool:
    return (
        0x3400 <= cp <= 0x4DBF
        or 0x4E00 <= cp <= 0x9FFF
        or 0xF900 <= cp <= 0xFAFF
        or 0x20000 <= cp <= 0x323AF
    )


def is_invisible(cp: int, prev_cp: int | None = None) -> bool:
    """判定码位是否为应剥离的不可见字符（含 CJK IVD 保护）。"""
    if prev_cp is not None and is_cjk_ideograph(prev_cp):
        if 0xFE00 <= cp <= 0xFE0F or cp in VS_SUPPLEMENT:
            return False  # CJK 异体字标注，合法正字
    return bool(
        cp in STRIP_CODEPOINTS
        or cp in VS_SUPPLEMENT
        or cp in TAG_CHARS
        or cp in RESERVED_IGNORABLE
        or cp in PRIVATE_USE
        or _is_noncharacter(cp)
    )


def scan(text: str) -> Counter:
    """统计文本中的不可见码位。"""
    hits: Counter = Counter()
    prev: int | None = None
    for ch in text:
        cp = ord(ch)
        if is_invisible(cp, prev):
            hits[cp] += 1
            continue
        prev = cp
    return hits


def clean_str(text: str) -> tuple[str, Counter]:
    out: list[str] = []
    hits: Counter = Counter()
    prev: int | None = None
    for ch in text:
        cp = ord(ch)
        if is_invisible(cp, prev):
            hits[cp] += 1
            continue  # 被剥离字符不作为后续 IVD 保护上下文
        out.append(ch)
        prev = cp
    return "".join(out), hits


# ---------- DOCX（zip 内全部 XML part） ----------

_XML_ENTITY_RE = re.compile(r"&#([xX])([0-9A-Fa-f]+);|&#(0|[1-9][0-9]*);")
_TAG_SPLIT_RE = re.compile(r"(<[^>]*>)")


def _strip_entities(text: str, hits: Counter) -> str:
    """删除数字字符引用形式的不可见字符（&#8203; / &#x200b;）。

    实体解码后失去前文上下文，无法做 IVD 保护；中文学术论文不使用
    实体形式的变体选择符，直接剥离是安全的。
    """

    def repl(m: re.Match) -> str:
        cp = int(m.group(2), 16) if m.group(1) else int(m.group(3))
        if is_invisible(cp):
            hits[cp] += 1
            return ""
        return m.group(0)

    return _XML_ENTITY_RE.sub(repl, text)


def _strip_tag_texts(text: str, hits: Counter) -> str:
    """只清理标签之间的文本节点，不动属性与结构。"""
    parts = _TAG_SPLIT_RE.split(text)
    for i, seg in enumerate(parts):
        if i % 2 == 0 and seg:  # 偶数段为标签外文本
            cleaned, h = clean_str(seg)
            if h:
                hits.update(h)
                parts[i] = cleaned
    return "".join(parts)


# 正文相关 part：只有这些位置承载文档正文/元数据文本，才做检测与清理。
# fontTable.xml / styles.xml 等内部含符号字体合法 PUA 字符（如 U+F0B7），
# 属 Word 字体映射约定，一律不碰，避免误伤。
_BODY_PART_RE = re.compile(
    r"^(?:word/(?:document|footnotes|endnotes|comments|(?:header|footer)\d*)\.xml"
    r"|docProps/(?:core|app|custom)\.xml)$"
)


def _clean_docx_bytes(data: bytes, hits: Counter) -> bytes | None:
    """清理单个 XML part 字节；返回 None 表示无变化。"""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return None
    before = sum(hits.values())
    text = _strip_entities(text, hits)
    text = _strip_tag_texts(text, hits)
    return text.encode("utf-8") if sum(hits.values()) > before else None


def process_docx(path: Path, do_clean: bool, backup: bool) -> Counter:
    hits: Counter = Counter()
    with zipfile.ZipFile(path) as zf:
        entries = [(info, zf.read(info.filename)) for info in zf.infolist()]
    changed = False
    rebuilt: list[tuple[zipfile.ZipInfo, bytes]] = []
    for info, data in entries:
        if _BODY_PART_RE.match(info.filename):
            local: Counter = Counter()
            new = _clean_docx_bytes(data, local)
            if local:
                hits.update(local)
            if new is not None:
                changed = True
                rebuilt.append((info, new))
            else:
                rebuilt.append((info, data))
        else:
            rebuilt.append((info, data))
    if do_clean and changed:
        if backup:
            _backup(path)
        tmp = path.with_suffix(path.suffix + ".tmp")
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
            for info, data in rebuilt:
                zf.writestr(info, data)
        tmp.replace(path)
        return _scan_docx(path)  # 复检：只报告正文残留
    return hits


def _scan_docx(path: Path) -> Counter:
    """只扫描正文相关 part 的标签外文本（与清理范围一致，避免字体表 PUA 误报）。"""
    hits: Counter = Counter()
    with zipfile.ZipFile(path) as zf:
        for info in zf.infolist():
            if not _BODY_PART_RE.match(info.filename):
                continue
            try:
                text = zf.read(info.filename).decode("utf-8")
            except UnicodeDecodeError:
                continue
            for i, seg in enumerate(_TAG_SPLIT_RE.split(text)):
                if i % 2 == 0:
                    hits.update(scan(seg))
    return hits


# ---------- 纯文本 / LaTeX ----------


def process_text(path: Path, do_clean: bool, backup: bool) -> Counter:
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    hits = scan(text)
    if has_bom:  # 文件头 BOM 即 U+FEFF，属剥离对象
        hits[0xFEFF] += 1
    if hits and do_clean:
        cleaned, _ = clean_str(text)
        if backup:
            _backup(path)
        path.write_bytes(cleaned.encode("utf-8"))  # UTF-8 无需 BOM，不写回
        return Counter()  # cleaned 按构造必干净（BOM 已被 utf-8-sig 剥离）
    return hits


# ---------- PDF ----------

_HEX_STRING_RE = re.compile(rb"<([0-9A-Fa-f\s]*)>")
_BFCHAR_BLOCK_RE = re.compile(r"beginbfchar\s*(.*?)\s*endbfchar", re.S)
_BFRANGE_BLOCK_RE = re.compile(r"beginbfrange\s*(.*?)\s*endbfrange", re.S)
_HEX_PAIR_RE = re.compile(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>")
_BFRANGE_FIXED_RE = re.compile(
    rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>(?!\s*\[)"
)


def _import_fitz():
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("ERROR: PDF 模式需要 PyMuPDF：pip install pymupdf", file=sys.stderr)
        sys.exit(2)
    return fitz


def _dst_invisible(dst_hex: bytes) -> bool:
    digits = dst_hex.decode("ascii")
    if len(digits) % 4:
        return False
    hi = int(digits[:4], 16)
    cp = hi
    if 0xD800 <= hi <= 0xDBFF and len(digits) >= 8:  # UTF-16 代理对
        cp = 0x10000 + ((hi - 0xD800) << 10) + (int(digits[4:8], 16) - 0xDC00)
    return is_invisible(cp)


def _tounicode_invisible_codes(doc) -> set[int]:
    """遍历字体 ToUnicode CMap，收集映射到不可见 Unicode 的 2 字节码位。"""
    codes: set[int] = set()
    for xref in range(1, doc.xref_length()):
        try:
            obj = doc.xref_object(xref, compressed=True)
        except Exception:
            continue
        if "/Font" not in obj and "/Type0" not in obj:
            continue
        m = re.search(r"/ToUnicode\s+(\d+)\s+0\s+R", obj)
        if not m:
            continue
        try:
            cmap = doc.xref_stream(int(m.group(1))).decode("latin-1", errors="replace")
        except Exception:
            continue
        for block in _BFCHAR_BLOCK_RE.findall(cmap):
            for src, dst in _HEX_PAIR_RE.findall(block.encode("latin-1")):
                if _dst_invisible(dst) and len(src) == 4:
                    codes.add(int(src, 16))
        for block in _BFRANGE_BLOCK_RE.findall(cmap):
            for lo, hi, dst0 in _BFRANGE_FIXED_RE.findall(block.encode("latin-1")):
                lo_i, hi_i = int(lo, 16), int(hi, 16)
                if len(lo) == 4 and hi_i - lo_i <= 65535 and _dst_invisible(dst0):
                    codes.update(range(lo_i, hi_i + 1))
    return {c for c in codes if 0 < c <= 0xFFFF}


def _metadata_hits(doc) -> Counter:
    hits: Counter = Counter()
    for value in (doc.metadata or {}).values():
        if isinstance(value, str):
            hits.update(scan(value))
    return hits


def process_pdf(path: Path, do_clean: bool, backup: bool) -> Counter:
    fitz = _import_fitz()
    doc = fitz.open(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    need_clean = False
    try:
        hits: Counter = Counter()
        for page in doc:
            hits.update(scan(page.get_text()))
        hits.update(_metadata_hits(doc))

        # 内容流层：按 ToUnicode 映射清理 hex 串中的隐形码（捕获 get_text 漏检情形）
        codes = _tounicode_invisible_codes(doc)
        stream_hit = False
        if codes:
            code_hex = {f"{c:04X}" for c in codes}

            for page in doc:
                for xref in page.get_contents():
                    try:
                        stream = doc.xref_stream(xref)
                    except Exception:
                        continue

                    def repl(m: re.Match, _codes=code_hex) -> bytes:
                        nonlocal stream_hit
                        digits = re.sub(rb"\s", b"", m.group(1)).decode("ascii").upper()
                        if len(digits) % 2:
                            return m.group(0)
                        units = [digits[i : i + 2] for i in range(0, len(digits), 2)]
                        kept: list[str] = []
                        i, removed = 0, False
                        while i < len(units):
                            if (
                                i + 1 < len(units)
                                and units[i] + units[i + 1] in _codes
                            ):
                                removed = True
                                i += 2
                                continue
                            kept.append(units[i])
                            i += 1
                        if not removed:
                            return m.group(0)
                        stream_hit = True
                        return b"<" + "".join(kept).encode("ascii") + b">"

                    new = _HEX_STRING_RE.sub(repl, stream)
                    if do_clean and new != stream:
                        doc.update_stream(xref, new)

        if stream_hit and not hits:
            # 内容流发现隐形码但文本抽取未命中（无 ToUnicode 反查等情形）：
            # 记为非字符类命中，确保 check 模式不误报干净
            hits[0xFFFE] += 1

        need_clean = do_clean and (bool(hits) or stream_hit)
        if need_clean:
            if backup:
                _backup(path)
            meta = dict(doc.metadata or {})
            for k, v in list(meta.items()):
                if isinstance(v, str) and scan(v):
                    meta[k] = clean_str(v)[0]
            doc.set_metadata(meta)
            doc.save(tmp, garbage=3, deflate=True)
    finally:
        if not doc.is_closed:
            doc.close()
    if need_clean:
        tmp.replace(path)  # 关闭文档句柄后再替换（Windows 文件占用）
        residual = process_pdf_check_only(path)
        return residual if residual else Counter()
    return hits


def process_pdf_check_only(path: Path) -> Counter:
    fitz = _import_fitz()
    doc = fitz.open(path)
    try:
        hits: Counter = Counter()
        for page in doc:
            hits.update(scan(page.get_text()))
        hits.update(_metadata_hits(doc))
        codes = _tounicode_invisible_codes(doc)
        if codes:
            code_hex = {f"{c:04X}" for c in codes}
            for page in doc:
                for xref in page.get_contents():
                    try:
                        stream = doc.xref_stream(xref)
                    except Exception:
                        continue
                    for m in _HEX_STRING_RE.finditer(stream):
                        digits = re.sub(rb"\s", b"", m.group(1)).decode("ascii").upper()
                        if len(digits) % 2:
                            continue
                        units = [digits[i : i + 2] for i in range(0, len(digits), 2)]
                        for i in range(0, len(units) - 1):
                            if units[i] + units[i + 1] in code_hex:
                                hits[0xFFFE] += 1
                                return hits
        return hits
    finally:
        if not doc.is_closed:
            doc.close()


# ---------- CLI ----------


def _backup(path: Path) -> None:
    bak = path.with_name(path.name + ".bak")
    if not bak.exists():  # 保留最初原件（与 Layer A 的 .bak 约定一致）
        shutil.copy2(path, bak)


def dispatch(path: Path, do_clean: bool, backup: bool) -> Counter:
    suffix = path.suffix.lower()
    if suffix == ".docx":
        return process_docx(path, do_clean, backup)
    if suffix == ".pdf":
        return process_pdf(path, do_clean, backup)
    return process_text(path, do_clean, backup)


def fmt_hits(hits: Counter) -> str:
    parts = []
    for cp, n in sorted(hits.items()):
        label = "内容流隐形码" if cp == 0xFFFE else f"U+{cp:04X}"
        parts.append(f"{label}×{n}")
    return ", ".join(parts)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="+", help="待处理文件（.tex/.docx/.pdf/纯文本）")
    ap.add_argument("--clean", action="store_true", help="就地清理（默认留 .bak）；缺省为只检测")
    ap.add_argument("--no-backup", action="store_true", help="清理时不留 .bak")
    args = ap.parse_args()
    backup = not args.no_backup

    dirty = 0
    for raw in args.paths:
        path = Path(raw)
        if not path.is_file():
            print(f"[missing] {path}", file=sys.stderr)
            dirty += 1
            continue
        hits = dispatch(path, args.clean, backup)
        if hits:
            dirty += 1
            action = "CLEANED-RESIDUAL" if args.clean else "FOUND"
            print(f"[{action}] {path}: {fmt_hits(hits)}")
        else:
            print(f"[clean] {path}")
    return 1 if dirty else 0


if __name__ == "__main__":
    raise SystemExit(main())
