"""닭의 목을 비틀어도 새벽은 온다 — 위키 문서 형식 투자자 서한 뷰어."""
import base64
import re
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).parent
LETTER = ROOT / "letter.md"
LAST_EDIT = "2026-08-08 00:10:00"
CATEGORIES = ["반도체", "메모리 반도체", "투자", "2026년 주식시장", "투자자 서한"]

st.set_page_config(page_title="닭의 목을 비틀어도 새벽은 온다", page_icon="📄", layout="centered")


def embed_image(alt: str, src: str) -> str:
    path = ROOT / src
    if not path.exists():
        return f"<p class='wiki-p'>[이미지 없음: {src}]</p>"
    b64 = base64.b64encode(path.read_bytes()).decode()
    ext = path.suffix.lstrip(".").lower() or "png"
    return (
        f"<div class='wiki-img'><img src='data:image/{ext};base64,{b64}' alt='{alt}'>"
        f"<div class='img-cap'>{alt}</div></div>"
    )


def inline(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return text


def make_table(rows: list[str]) -> str:
    html = ["<table class='wiki-table'>"]
    body_started = False
    for i, row in enumerate(rows):
        if re.match(r"^\|[\s\-:|]+\|$", row):
            body_started = True
            continue
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        tag = "th" if not body_started and i == 0 else "td"
        html.append("<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in cells) + "</tr>")
    html.append("</table>")
    return "".join(html)


def parse(md: str):
    """letter.md → (title, subtitle, body_html, toc[])"""
    lines = md.splitlines()
    title = subtitle = ""
    out: list[str] = []
    toc: list[tuple[int, str, str]] = []  # (depth, label, anchor)
    table_buf: list[str] = []
    quote_buf: list[str] = []
    list_buf: list[str] = []
    h2_n = 0
    h3_n = 0

    def flush():
        nonlocal table_buf, quote_buf, list_buf
        if table_buf:
            out.append(make_table(table_buf))
            table_buf = []
        if quote_buf:
            inner = "<br>".join(inline(q) for q in quote_buf)
            out.append(f"<div class='wiki-quote'>{inner}</div>")
            quote_buf = []
        if list_buf:
            out.append("<ul class='wiki-ul'>" + "".join(f"<li>{inline(x)}</li>" for x in list_buf) + "</ul>")
            list_buf = []

    for raw in lines:
        line = raw.rstrip()
        if line.startswith("| "):
            table_buf.append(line)
            continue
        if re.match(r"^\|[\s\-:|]+\|$", line):
            table_buf.append(line)
            continue
        if line.startswith("> "):
            flush()
            quote_buf.append(line[2:])
            continue
        if line.startswith("- "):
            flush()
            list_buf.append(line[2:])
            continue
        flush()

        if not line:
            continue
        if line == "---":
            continue
        m_img = re.match(r"^!\[(.*?)\]\((.*?)\)$", line)
        if m_img:
            out.append(embed_image(m_img.group(1), m_img.group(2)))
            continue
        if line.startswith("# "):
            title = line[2:]
            continue
        if line.startswith("### ") and not out and not subtitle:
            subtitle = line[4:]
            continue
        if line.startswith("## "):
            h2_n += 1
            h3_n = 0
            label = re.sub(r"^\d+\.\s*", "", line[3:])
            anchor = f"s-{h2_n}"
            toc.append((1, f"{h2_n}. {label}", anchor))
            out.append(
                f"<div class='anchor' id='{anchor}'></div>"
                f"<h2 class='wiki-h2'><a class='hnum' href='#toc'>{h2_n}.</a> "
                f"{inline(label)} <span class='edit'>[편집]</span></h2>"
            )
            continue
        if line.startswith("### "):
            h3_n += 1
            label = line[4:]
            anchor = f"s-{h2_n}-{h3_n}"
            toc.append((2, f"{h2_n}.{h3_n}. {label}", anchor))
            out.append(
                f"<div class='anchor' id='{anchor}'></div>"
                f"<h3 class='wiki-h3'><a class='hnum' href='#toc'>{h2_n}.{h3_n}.</a> "
                f"{inline(label)} <span class='edit'>[편집]</span></h3>"
            )
            continue
        m = re.match(r"^(\d+)\.\s+(.*)$", line)
        if m:
            out.append(f"<div class='wp'><span class='wnum'>{m.group(1)}.</span> {inline(m.group(2))}</div>")
            continue
        out.append(f"<p class='wiki-p'>{inline(line)}</p>")

    flush()
    return title, subtitle, "".join(out), toc


CSS = """
<style>
#MainMenu, footer, header[data-testid="stHeader"] {visibility: hidden; height: 0;}
[data-testid="stHeaderActionElements"] {display: none;}
.anchor {position: relative; top: -10px;}
.block-container {padding-top: 0.5rem; max-width: 1060px;}
html, body, [class*="css"] {font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Malgun Gothic", sans-serif;}

.doc-title {font-size:32px; font-weight:700; border-bottom:1px solid #ccc;
  padding-bottom:6px; margin:14px 0 2px 0; letter-spacing:-1px;}
.doc-sub {color:#666; font-size:14px; margin-bottom:2px;}
.last-edit {text-align:right; color:#888; font-size:12.5px; margin-bottom:8px;}
.cats {border:1px solid #ccc; border-radius:3px; padding:6px 10px; font-size:13px;
  margin-bottom:14px; background:#fff;}
.cats a {color:#0275d8; text-decoration:none;}

.warn-box {border:1px solid #ddd; border-left:6px solid #e65b5b; border-radius:3px;
  background:#fff8f8; padding:10px 14px; font-size:14px; margin:10px 0 16px 0; color:#333;}
.warn-box .wt {font-weight:700; color:#c0392b;}

.toc-box {display:inline-block; border:1px solid #ccc; border-radius:3px; background:#f8f9fa;
  padding:12px 26px 12px 18px; margin:6px 0 22px 0; font-size:14.5px; line-height:1.9;}
.toc-title {font-weight:700; font-size:15px; margin-bottom:4px;}
.toc-box a {color:#0275d8; text-decoration:none;}
.toc-d2 {padding-left:22px;}

.wiki-h2 {font-size:24px; font-weight:600; border-bottom:1px solid #ccc;
  padding-bottom:5px; margin:34px 0 14px 0; letter-spacing:-0.5px;}
.wiki-h3 {font-size:19px; font-weight:600; border-bottom:1px solid #e0e0e0;
  padding-bottom:4px; margin:26px 0 12px 0;}
.hnum {color:#0275d8; text-decoration:none; margin-right:2px;}
.edit {font-size:12px; color:#aaa; font-weight:400;}

.wp {font-size:15.5px; line-height:1.85; margin:7px 0; color:#212529;}
.wnum {color:#0275d8; font-weight:600; margin-right:2px;}
.wiki-p {font-size:15.5px; line-height:1.85; color:#212529;}

.wiki-quote {border-left:4px solid #00A495; background:#f8f9fa; padding:10px 14px;
  margin:12px 0; font-size:14.5px; line-height:1.9; color:#444; border-radius:0 3px 3px 0;}

.wiki-table {border-collapse:collapse; margin:14px auto; font-size:14px; line-height:1.7;}
.wiki-table th {background:#eaecef; border:1px solid #ccc; padding:5px 12px; font-weight:700;}
.wiki-table td {border:1px solid #ccc; padding:5px 12px;}
.wiki-table tr:nth-child(even) td {background:#fafbfc;}

.wiki-ul {font-size:14px; line-height:1.85; color:#333;}
code {background:#f1f3f5; border-radius:3px; padding:1px 5px; font-size:13px;}

.wiki-img {text-align:center; margin:16px 0;}
.wiki-img img {max-width:100%; border:1px solid #ddd; border-radius:3px;}
.img-cap {color:#888; font-size:12.5px; margin-top:4px;}
</style>
"""


def main():
    md = LETTER.read_text(encoding="utf-8")
    title, subtitle, body, toc = parse(md)

    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(f"<div class='doc-title'>{title}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='doc-sub'>{subtitle}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='last-edit'>최근 수정 시각: {LAST_EDIT}</div>", unsafe_allow_html=True)
    cats = " | ".join(f"<a href='#'>{c}</a>" for c in CATEGORIES)
    st.markdown(f"<div class='cats'>분류: {cats}</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='warn-box'><span class='wt'>⚠️ 이 문서는 투자 자문이 아닙니다.</span><br>"
        "개인의 판단 기록이며 특정 종목의 매수·매도를 권유하지 않습니다. "
        "모든 수치는 기준일 점추정이고, 투자 판단과 그 결과는 각자의 몫입니다.</div>",
        unsafe_allow_html=True,
    )

    toc_rows = "".join(
        f"<div class='toc-d{d}'><a href='#{a}'>{label}</a></div>" for d, label, a in toc
    )
    st.markdown(
        f"<div class='toc-box' id='toc'><div class='toc-title'>목차</div>{toc_rows}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(body, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
