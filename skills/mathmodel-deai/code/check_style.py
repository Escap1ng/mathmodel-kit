#!/usr/bin/env python3
"""check_style.py — 去 AI 痕迹检查器（降 AI 技能的第二道表述级关卡：结构级）。

    python3 code/check_style.py paper/paper.tex            # 只报不改，命中即退出 1
    python3 code/check_style.py paper/*.tex --json         # 机器可读输出（含风险等级）
    python3 code/check_style.py --list-metrics             # 查看指标与阈值

`check_phrasing.py` 管「词汇与句式」，本脚本管「句子、段落、数据」的结构节奏，覆盖：
  M1 long-passive        过长被动句（>25 字且含被动标记）——须拆分
  M2 repeated-opening    句式重复（连续 ≥4 句同一开头）——同类表述连续不超过 3 次
  M3 transition-density  过渡词密度（每段 >2 个）——每段过渡词不超过 2 个
  M4 sentence-rhythm     长短句比例（长句占比偏离 1:2）——仅在句数 ≥12 时统计
  M5 paragraph-rhythm    相邻段落字数差异（<20%）——仅在合格段落 ≥4 时统计
  M6 decimal-precision   结果小数位（>4 位）——统一保留 2-4 位

统计类指标（M4/M5）在样本过小时自动跳过，避免对短文本误报。列表项、表格行、编号分点
（「假设 X」「（1）」「①」「步骤 X」等）、清单块的换行续行与 README 类 HTML 区块均不参与统计——
清单类同形开头是格式要求，不是句式单调。退出码 0 通过 / 1 有命中 / 2 用法或环境错误。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TEXT_SUFFIXES = {".tex", ".md", ".txt", ".bib", ".typ"}

LONG_SENTENCE = 25          # 长句阈值（字）
MIN_SENTENCE = 8            # 过短的分句不计入节奏统计
MIN_PARAGRAPH = 60          # 参与段落节奏统计的最小段长（字）
MIN_RHYTHM_SENTENCES = 12   # 长短句比例统计的最少句数
MIN_RHYTHM_PARAGRAPHS = 4   # 相邻段落节奏统计的最少合格段数
RHYTHM_BAND = (0.20, 0.50)  # 长句占比合理区间（目标 1:2）
PARA_DIFF_MIN = 0.20        # 相邻段落字数差异下限
MAX_DECIMALS = 4            # 结果小数位上限

TRANSITIONS = [
    "首先", "其次", "再次", "再者", "最后", "此外", "另外", "然而", "因此", "所以",
    "综上所述", "总而言之", "总的来说", "总体而言", "整体而言", "值得注意的是",
    "需要指出的是", "另一方面", "与此同时", "同时", "进而", "由此可见", "由此可知",
    "在此基础上", "更进一步", "更一般地", "与之相对", "简而言之", "不得不说",
]

PASSIVE_RE = re.compile(r"被|受到|为[^。；！？\n]{1,8}所")
CJK_RE = re.compile(r"[\u3400-\u9fff]")
LATIN_RE = re.compile(r"[A-Za-z0-9]+")
DECIMAL_RE = re.compile(r"\d+\.(\d+)")
INLINE_CODE_RE = re.compile(r"`[^`]*`")
TEX_COMMENT_RE = re.compile(r"(?<!\\)%.*$")
MATH_INLINE_RE = re.compile(r"\$[^$]*\$")
TEX_CMD_RE = re.compile(r"\\[a-zA-Z@]+\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})?")
SECTION_RE = re.compile(
    r"^\s*(?:#+|\\section\b|\\subsection\b|\\subsubsection\b|\\chapter\b|\\paragraph\b)")
# 列表项、编号分点与表格行按边界处理（本检查器面向论文正文的连续叙述段，清单类文本不参与统计）
# 编号分点必须排除：章节结构规范要求「假设 X」分点列出、符号说明用三线表，
# 这类同形开头是格式要求而非句式单调（与 mathmodel-score 的章节契约保持一致）。
LIST_RE = re.compile(r"^\s*(?:[-*+]\s|\d+[.)]\s|\|)")
ENUM_RE = re.compile(
    r"^\s*(?:假设\s*[0-9０-９一二三四五六七八九十]+"
    r"|[（(]\s*[0-9０-９]+\s*[)）]"
    r"|\[\s*[0-9０-９]+\s*\]"          # 参考文献条目 [1] 属清单，不计入行文节奏
    r"|[①②③④⑤⑥⑦⑧⑨⑩]"
    r"|步骤\s*[0-9０-９]+"
    r"|第\s*[0-9０-９一二三四五六七八九十]+\s*步"
    r"|(?:Step|step)\s*\d+)"
)


def is_list_like(line: str) -> bool:
    """是否为清单类行（列表项、表格行或编号分点）。"""
    return bool(LIST_RE.match(line) or ENUM_RE.match(line))


HTML_OPEN_RE = re.compile(r"^\s*<[a-zA-Z]")
HTML_CLOSE_RE = re.compile(r"</(?:p|div|h[1-6]|table|ul|ol|blockquote|details|summary)>\s*$")

MSG = {
    "zh": {
        "no_files": "没有可检查的文件",
        "skip": "跳过非文本文件：{path}",
        "hit": "{path}:{line} [{metric}] {text}",
        "detail": "    → {fix}",
        "summary": "检查 {files} 个文件，结构级命中 {hits} 处；AI 痕迹风险：{risk}",
        "summary_ok": "检查 {files} 个文件，未命中任何结构级痕迹（风险：低）",
        "risk": "低",
        "list_header": "结构级指标（{count} 项）",
    },
    "en": {
        "no_files": "No files to check",
        "skip": "Skipping non-text file: {path}",
        "hit": "{path}:{line} [{metric}] {text}",
        "detail": "    → {fix}",
        "summary": "Checked {files} file(s); {hits} structural hit(s); AI-slop risk: {risk}",
        "summary_ok": "Checked {files} file(s); no structural AI-slop patterns (risk: low)",
        "risk": "low",
        "list_header": "Structural metrics ({count})",
    },
}

METRICS = [
    {"id": "long-passive", "severity": "high", "label": "过长被动句",
     "why": "超过 25 字的被动句读起来费劲，是机器行文的典型特征",
     "fix": "拆成 2-3 个短句，主动语态优先（「本文以…为约束求解」替代「…被…所…」）"},
    {"id": "repeated-opening", "severity": "medium", "label": "句式重复",
     "why": "连续 4 句以上用同一开头，句式单调、缺乏长短变化",
     "fix": "改写开头，让相邻句子以不同成分起句（数据、结论、方法交替）"},
    {"id": "transition-density", "severity": "medium", "label": "过渡词过密",
     "why": "同一段落过渡词超过 2 个，靠连接词堆砌行文",
     "fix": "每段过渡词不超过 2 个，删除后信息量不变的过渡词直接去掉"},
    {"id": "sentence-rhythm", "severity": "low", "label": "长短句比例失衡",
     "why": "长句占比偏离 1:2（长:短），读起来或喘不过气或过于零碎",
     "fix": "拆分过长句、合并过短句，使长句占比落在 20%-50%"},
    {"id": "paragraph-rhythm", "severity": "low", "label": "段落节奏单一",
     "why": "相邻段落字数接近（差异 <20%），呈机械等长的模板感",
     "fix": "按内容需要拉开段落长短，重点段落展开、次要内容从简"},
    {"id": "decimal-precision", "severity": "low", "label": "小数位超标",
     "why": "结果小数位超过 4 位，未按数据类型统一保留 2-4 位",
     "fix": "统一保留 2-4 位小数，并在关键数据后补误差范围（如 ±X%）"},
]


def token_len(text: str) -> int:
    """字数：CJK 逐字计 1，连续拉丁/数字串计 1，忽略空白与标点。"""
    return len(CJK_RE.findall(text)) + len(LATIN_RE.findall(text))


def strip_markup(line: str) -> str:
    """去掉 LaTeX 命令、行内公式、注释与行内代码，只留自然语言。"""
    s = TEX_COMMENT_RE.sub("", line)
    s = INLINE_CODE_RE.sub(" ", s)
    s = MATH_INLINE_RE.sub(" ", s)
    s = TEX_CMD_RE.sub(" ", s)
    return s.replace("{", " ").replace("}", " ")


def iter_paragraphs(lines: list[tuple[int, str]]):
    """按空行/标题/清单切段：标题、清单块（含其换行续行）与 HTML 区块不计入段落。"""
    buf: list[tuple[int, str]] = []
    in_list = False
    in_html = False
    for lineno, raw in lines:
        if not raw.strip():
            in_list = False
            if buf:
                yield buf
                buf = []
            continue
        if HTML_OPEN_RE.match(raw):
            in_html = True
        if in_html:
            if HTML_CLOSE_RE.search(raw):
                in_html = False
            continue
        if SECTION_RE.match(raw) or is_list_like(raw):
            in_list = True
            if buf:
                yield buf
                buf = []
            continue
        if in_list:
            # 清单块的换行续行（markdown 软换行 / 手工折行）同属清单，不按正文统计
            continue
        buf.append((lineno, raw))
    if buf:
        yield buf


def split_sentences(text: str, line_of: list[int]):
    """切句，产出 (sentence, start_line)；只认以句末标点结束的完整句，过滤碎片。"""
    out = []
    for match in re.finditer(r"[^。！？!?\n]+[。！？!?]", text):
        sent = match.group(0).strip()
        if token_len(sent) >= MIN_SENTENCE:
            out.append((sent, line_of[match.start()]))
    return out


def _paragraph_text(para: list[tuple[int, str]]):
    parts: list[str] = []
    line_of: list[int] = []
    for lineno, raw in para:
        stripped = strip_markup(raw)
        parts.append(stripped)
        line_of.extend([lineno] * len(stripped))
        parts.append(" ")
        line_of.append(lineno)
    return "".join(parts), line_of


def check_file(path: Path) -> tuple[list[dict], int]:
    try:
        raw = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return [], 0

    in_fence = False
    lines: list[tuple[int, str]] = []
    for lineno, line in enumerate(raw.splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append((lineno, line))

    hits: list[dict] = []
    total_chars = 0
    all_sentences: list[tuple[str, int]] = []
    para_info: list[tuple[int, int]] = []

    for para in iter_paragraphs(lines):
        text, line_of = _paragraph_text(para)
        sentences = split_sentences(text, line_of)
        all_sentences.extend(sentences)
        length = token_len(text)
        total_chars += length
        if length >= MIN_PARAGRAPH:
            para_info.append((para[0][0], length))

        # M1 过长被动句
        for sent, line in sentences:
            if token_len(sent) > LONG_SENTENCE and PASSIVE_RE.search(sent):
                hits.append({"metric": "long-passive", "line": line, "text": sent,
                             "fix": METRICS[0]["fix"]})
        # M2 句式重复（连续 ≥4 句同一开头）
        opens = ["".join(CJK_RE.findall(s.replace(" ", ""))[:2]) for s, _ in sentences]
        run = 1
        for i in range(1, len(sentences)):
            if opens[i] and opens[i] == opens[i - 1]:
                run += 1
                if run > 3:
                    hits.append({"metric": "repeated-opening", "line": sentences[i][1],
                                 "text": sentences[i][0], "fix": METRICS[1]["fix"]})
            else:
                run = 1
        # M3 过渡词密度（每段 >2）
        count = sum(text.count(word) for word in TRANSITIONS)
        if count > 2:
            hits.append({"metric": "transition-density", "line": para[0][0],
                         "text": f"本段过渡词 {count} 个", "fix": METRICS[2]["fix"]})

    # M6 小数位（在原始行上统计，含公式内的数值）
    for lineno, line in lines:
        if SECTION_RE.match(line) or is_list_like(line):
            continue
        for match in DECIMAL_RE.finditer(TEX_COMMENT_RE.sub("", line)):
            if len(match.group(1)) > MAX_DECIMALS:
                hits.append({"metric": "decimal-precision", "line": lineno,
                             "text": match.group(0), "fix": METRICS[5]["fix"]})

    # M4 长短句比例（句数足够时）
    if len(all_sentences) >= MIN_RHYTHM_SENTENCES:
        long_n = sum(1 for s, _ in all_sentences if token_len(s) > LONG_SENTENCE)
        ratio = long_n / len(all_sentences)
        if not RHYTHM_BAND[0] <= ratio <= RHYTHM_BAND[1]:
            hits.append({"metric": "sentence-rhythm", "line": all_sentences[0][1],
                         "text": f"长句占比 {ratio:.0%}（目标约 33%）", "fix": METRICS[3]["fix"]})

    # M5 相邻段落字数差异（合格段落足够时）
    if len(para_info) >= MIN_RHYTHM_PARAGRAPHS:
        for (_, prev), (line, cur) in zip(para_info, para_info[1:]):
            diff = abs(prev - cur) / max(prev, cur)
            if diff < PARA_DIFF_MIN:
                hits.append({"metric": "paragraph-rhythm", "line": line,
                             "text": f"相邻段落字数差异 {diff:.0%}（下限 20%）",
                             "fix": METRICS[4]["fix"]})

    return hits, total_chars


def risk_level(hits: list[dict], chars: int) -> str:
    weights = {"high": 3.0, "medium": 1.0, "low": 0.5}
    score = sum(weights.get(h["severity"], 1.0) for h in hits)
    highs = sum(1 for h in hits if h["severity"] == "high")
    density = score / max(chars / 1000.0, 1.0)
    if density >= 6 or highs >= 8:
        return "极高"
    if density >= 3 or highs >= 4:
        return "高"
    if hits:
        return "中"
    return "低"


def main() -> None:
    parser = argparse.ArgumentParser(description="Check sentence/paragraph structure for AI-slop patterns.")
    parser.add_argument("paths", nargs="*", help="Files to check (.tex/.md/.txt/.bib/.typ)")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--list-metrics", action="store_true", help="Print metrics and thresholds")
    parser.add_argument("--lang", choices=["zh", "en"], default="zh", help="Message language")
    args = parser.parse_args()
    lang = args.lang

    if args.list_metrics:
        if args.json:
            print(json.dumps({"thresholds": {
                "long_sentence": LONG_SENTENCE, "min_sentence": MIN_SENTENCE,
                "min_paragraph": MIN_PARAGRAPH, "min_rhythm_sentences": MIN_RHYTHM_SENTENCES,
                "min_rhythm_paragraphs": MIN_RHYTHM_PARAGRAPHS, "rhythm_band": list(RHYTHM_BAND),
                "para_diff_min": PARA_DIFF_MIN, "max_decimals": MAX_DECIMALS},
                "metrics": [{"id": m["id"], "label": m["label"], "severity": m["severity"],
                             "why": m["why"], "fix": m["fix"]} for m in METRICS]},
                ensure_ascii=False, indent=2))
            return
        print(MSG[lang]["list_header"].format(count=len(METRICS)))
        for metric in METRICS:
            print(f"- {metric['id']:<20} {metric['label']}（{metric['severity']}）")
            print(f"    {metric['why']}")
            print(f"    改法：{metric['fix']}")
        return

    if not args.paths:
        sys.stderr.write(MSG[lang]["no_files"] + "\n")
        raise SystemExit(2)

    targets: list[Path] = []
    for raw in args.paths:
        path = Path(raw).expanduser()
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            sys.stderr.write(MSG[lang]["skip"].format(path=path) + "\n")
            continue
        targets.append(path)
    if not targets:
        sys.stderr.write(MSG[lang]["no_files"] + "\n")
        raise SystemExit(2)

    severity = {m["id"]: m["severity"] for m in METRICS}
    all_hits: list[dict] = []
    total_chars = 0
    for path in targets:
        hits, chars = check_file(path)
        total_chars += chars
        for hit in hits:
            hit["path"] = str(path)
            hit["severity"] = severity.get(hit["metric"], "low")
            all_hits.append(hit)
    all_hits.sort(key=lambda item: (item["path"], item["line"]))

    risk = risk_level(all_hits, total_chars)
    if args.json:
        print(json.dumps({"files": len(targets), "chars": total_chars, "risk": risk,
                          "hits": all_hits}, ensure_ascii=False, indent=2))
    else:
        for hit in all_hits:
            print(MSG[lang]["hit"].format(path=hit["path"], line=hit["line"],
                                          metric=hit["metric"], text=hit["text"]))
            print(MSG[lang]["detail"].format(fix=hit["fix"]))
        template = "summary" if all_hits else "summary_ok"
        print(MSG[lang][template].format(files=len(targets), hits=len(all_hits), risk=risk))

    raise SystemExit(1 if all_hits else 0)


if __name__ == "__main__":
    main()
