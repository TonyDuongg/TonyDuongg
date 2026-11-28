#!/usr/bin/env python3
"""
Build the SVG cards that lay out the profile README.

GitHub READMEs cannot use CSS, so each block of the layout (header, link
buttons, project cards, stack) is drawn as an SVG and placed with <img>.
Edit the content below and run:  python scripts/build_readme_cards.py
"""

import base64
import html
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "cards")

# Same quiet palette as the portfolio: ivory paper, charcoal ink, moss green.
BG = "#f7f6f3"
SURFACE = "#efede8"
SURFACE_2 = "#e7e4dd"
INK = "#1f2328"
MUTED = "#5c6166"
ACCENT = "#3f6b4f"
ACCENT_INK = "#ffffff"
FONT = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"

FULL = 840
HALF = 412


# ---------------------------------------------------------------- helpers

def esc(text):
    return html.escape(text, quote=True)


def text_width(text, size, bold=False):
    """Rough width of a string in the system UI face."""
    narrow = set("iIl.,:;'|!·()[]/ ")
    wide = set("mwMW@")
    units = 0.0
    for ch in text:
        if ch in narrow:
            units += 0.30
        elif ch in wide:
            units += 0.86
        elif ch.isupper() or ch.isdigit():
            units += 0.62
        else:
            units += 0.53
    return units * size * (1.06 if bold else 1.0)


def wrap(text, size, width, bold=False):
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if text_width(trial, size, bold) <= width:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def svg(width, height, body, label, extra_style=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="{esc(label)}">
  <style>
    text {{ font-family: {FONT}; }}
    {extra_style}
  </style>
  <rect width="{width}" height="{height}" fill="{BG}"/>
{body}
</svg>
"""


def t(x, y, text, size=14, fill=INK, weight=400, anchor="start"):
    return (f'  <text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}">{esc(text)}</text>')


def paragraph(x, y, text, size, width, line_height, max_lines, fill=INK):
    lines = wrap(text, size, width)[:max_lines]
    return "\n".join(t(x, y + i * line_height, line, size, fill) for i, line in enumerate(lines))


def chips(x, y, items, max_width, size=12.5, core=()):
    parts, cursor = [], x
    for item in items:
        w = text_width(item, size) + 20
        if cursor + w > x + max_width:
            break
        filled = item in core
        parts.append(f'  <rect x="{cursor:.1f}" y="{y}" width="{w:.1f}" height="26" fill="{ACCENT if filled else SURFACE_2}"/>')
        parts.append(t(round(cursor + 10, 1), y + 17.5, item, size, ACCENT_INK if filled else INK, 600 if filled else 400))
        cursor += w + 6
    return "\n".join(parts)


def write(name, content):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"wrote assets/cards/{name}")


# ---------------------------------------------------------------- header

PIXELS = {
    "T": ["########", "########", "...##...", "...##...", "...##...", "...##...", "...##...", "...##..."],
    "N": ["##....##", "###...##", "####..##", "##.##.##", "##..####", "##...###", "##....##", "##....##"],
    "Y": ["##....##", "##....##", ".##..##.", "..####..", "...##...", "...##...", "...##...", "...##..."],
    "D": ["######..", "#######.", "##...###", "##....##", "##....##", "##...###", "#######.", "######.."],
}


def avatar_data_uri():
    """The pixel avatar, embedded because README images cannot load other files."""
    with open(os.path.join(os.path.dirname(__file__), "..", "assets", "avatar.png"), "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")


def header():
    unit, height = 14, 340
    word_w = (5 * 8 + 4) * unit
    x0, y0 = (FULL - word_w) / 2, 52
    groups = []
    for i, letter in enumerate("TONYD"):
        ox = x0 + i * 9 * unit
        if letter == "O":
            groups.append(f'  <image class="o" href="{avatar_data_uri()}" x="{ox}" y="{y0}" width="{8 * unit}" height="{8 * unit}" style="image-rendering:pixelated"/>')
            continue
        rects = []
        for row_i, row in enumerate(PIXELS[letter]):
            start = -1
            for col in range(len(row) + 1):
                filled = col < len(row) and row[col] == "#"
                if filled and start < 0:
                    start = col
                if not filled and start >= 0:
                    rects.append(f'<rect x="{ox + start * unit}" y="{y0 + row_i * unit}" width="{(col - start) * unit}" height="{unit}"/>')
                    start = -1
        groups.append(f'  <g class="l" style="animation-delay:{120 + i * 80}ms">{"".join(rects)}</g>')
    body = "\n".join(groups) + "\n" + "\n".join([
        t(FULL / 2, 236, "Nguyễn Hải Dương", 32, INK, 700, "middle"),
        t(FULL / 2, 270, "Java backend developer · Spring Boot · PostgreSQL · AWS", 17, INK, 400, "middle"),
        t(FULL / 2, 300, "Studying software development at FPT University, Ho Chi Minh City", 15, MUTED, 400, "middle"),
    ])
    style = (".l { fill: %s; animation: rise 700ms cubic-bezier(0.22,1,0.36,1) both; } "
             ".o { animation: pop 900ms cubic-bezier(0.22,1,0.36,1) 200ms both; transform-box: fill-box; transform-origin: center; } "
             "@keyframes rise { from { opacity: 0; transform: translateY(28px); } } "
             "@keyframes pop { from { opacity: 0; transform: scale(0.82); } } "
             "@media (prefers-reduced-motion: reduce) { .l, .o { animation: none; } } "
             "svg { shape-rendering: crispEdges; } text { shape-rendering: auto; }") % INK
    write("header.svg", svg(FULL, height, body, "TONYD wordmark. Nguyễn Hải Dương, Java backend developer, FPT University, Ho Chi Minh City", style))


# ---------------------------------------------------------------- link buttons

def button(name, label):
    w, h = 200, 52
    body = "\n".join([
        f'  <rect width="{w}" height="{h}" fill="{ACCENT}"/>',
        t(22, 33, label, 17, ACCENT_INK, 700),
        # small arrow, drawn so it does not depend on a font glyph
        f'  <path d="M{w - 38} {h - 19} l12 -12 M{w - 34} {h - 31} h8 v8" stroke="{ACCENT_INK}" stroke-width="2.2" fill="none" stroke-linecap="square"/>',
    ])
    write(f"link-{name}.svg", svg(w, h, body, label))


# ---------------------------------------------------------------- about cards

def now_card():
    h = 250
    rows = [
        ("Building", "Backend systems in Java, Spring Boot and Node.js, and their databases"),
        ("Exploring", "AWS architecture, Docker, React and Next.js"),
        ("Open to", "Backend projects, database work and cloud services"),
    ]
    parts = [t(28, 46, "Right now", 22, INK, 700)]
    y = 84
    for label, value in rows:
        parts.append(t(28, y, label, 13, MUTED))
        parts.append(paragraph(118, y, value, 14, HALF - 118 - 24, 20, 2))
        y += 20 * len(wrap(value, 14, HALF - 118 - 24)[:2]) + 18
    write("now.svg", svg(HALF, h, "\n".join(parts), "Right now: building backend systems in Java, Spring Boot and Node.js; exploring AWS, Docker, React and Next.js; open to backend projects"))


def principles_card():
    h = 250
    quote = "Automate everything, optimize bottlenecks, eliminate single points of failure."
    parts = [
        t(28, 46, "How I work", 22, INK, 700),
        f'  <rect x="28" y="70" width="4" height="70" fill="{ACCENT}"/>',
        paragraph(46, 92, quote, 18, HALF - 46 - 28, 25, 3),
        paragraph(28, 200, "Based in Ho Chi Minh City, UTC+7.", 14, HALF - 56, 20, 1, MUTED),
    ]
    write("principles.svg", svg(HALF, h, "\n".join(parts), "How I work: " + quote))


# ---------------------------------------------------------------- projects

FEATURED = {
    "file": "project-creator-studio.svg",
    "kind": "Backend service and desktop app",
    "status": "Public · v1.1.0",
    "name": "Creator Studio",
    "text": "Reads public TikTok channels, ranks their videos by engagement and writes three-part short-video scripts: a 3-second hook, the body and a call to action. Script jobs run through AWS SQS, and a job that fails lands in a dead-letter queue and refunds its credits.",
    "chips": ["Java 21", "Spring Boot 3", "PostgreSQL", "Redis", "AWS SQS", "S3"],
    "steps": [("Channel ingest", "RapidAPI"), ("Raw payload", "Amazon S3"), ("Video metrics", "PostgreSQL"),
              ("Script job", "AWS SQS"), ("Worker", "Gemini or Bedrock"), ("Hook, body, CTA", "saved"),
              ("Failed job", "DLQ, credits back")],
}

PROJECTS = [
    {"file": "project-agent-redact.svg", "kind": "Open-source library", "status": "Public · npm, PyPI",
     "name": "agent-redact",
     "text": "Local secret and PII redactor for AI agents. Masks API keys, database URLs and personal data before a prompt leaves the machine, and restores them in the answer.",
     "chips": ["TypeScript", "Node.js", "Python", "MCP"]},
    {"file": "project-appfinance.svg", "kind": "Finance platform · in production", "status": "Private",
     "name": "AppFinance",
     "text": "Reconciliation across shops for Shopee and TikTok Shop sellers: OAuth tokens stored with AES-256-GCM, order sync every 15 minutes, payouts and profit and loss per shop.",
     "chips": ["Java 21", "Spring Boot 4", "React 19", "PostgreSQL", "Docker"]},
    {"file": "project-rugmaxing.svg", "kind": "Telegram bot and web studio", "status": "Private",
     "name": "RugMaxing Studio",
     "text": "Design rugs with AI from Telegram or the web. HMAC login, quota ledger with idempotency, SePay payments by webhook, uploads to Cloudflare R2, image pipeline in n8n.",
     "chips": ["Node.js", "Express", "React", "SQLite", "R2", "n8n"]},
    {"file": "project-tien-len.svg", "kind": "Browser game", "status": "Public · playable",
     "name": "Tiến Lên",
     "text": "A game for 30 April: drive from Hà Nội to Dinh Độc Lập through seven stops and answer a timed history question at each one.",
     "chips": ["JavaScript", "CSS", "Canvas"]},
    {"file": "project-portfolio.svg", "kind": "Personal site", "status": "Public · live",
     "name": "Portfolio",
     "text": "The TONYD wordmark, a live agent-redact demo and every project, rendered to static HTML at build time and deployed to GitHub Pages.",
     "chips": ["React", "TypeScript", "Vite", "GitHub Actions"]},
    {"file": "project-prj301.svg", "kind": "University project", "status": "Private",
     "name": "PRJ301 User Management",
     "text": "Java MVC web app with login, admin and user roles, user search and CRUD, and a shopping cart, with data access through DAO and DTO layers.",
     "chips": ["Java", "Servlet/JSP", "SQL Server", "Tomcat"]},
]


def project_card(p):
    w, h, pad = HALF, 250, 28
    parts = [
        t(pad, 40, p["kind"], 13, MUTED),
        t(w - pad, 40, p["status"], 13, MUTED, 400, "end"),
        t(pad, 80, p["name"], 26, INK, 700),
        paragraph(pad, 112, p["text"], 14, w - 2 * pad, 20, 4),
        chips(pad, h - 26 - pad + 4, p["chips"], w - 2 * pad),
    ]
    write(p["file"], svg(w, h, "\n".join(parts), f'{p["name"]}: {p["text"]}'))


def featured_card(p):
    w, h, pad = FULL, 300, 32
    text_w = 430
    parts = [
        t(pad, 44, p["kind"], 13, MUTED),
        t(pad, 92, p["name"], 38, INK, 700),
        paragraph(pad, 128, p["text"], 14.5, text_w, 21, 6),
        chips(pad, h - 26 - pad + 4, p["chips"], text_w),
        t(w - pad, 44, p["status"], 13, MUTED, 400, "end"),
    ]
    # the request path, as a small interface fragment on the right
    px, py, pw = 500, 64, w - 500 - pad
    parts.append(t(px, py + 2, "One script request", 13, MUTED))
    for i, (step, where) in enumerate(p["steps"]):
        y = py + 16 + i * 30
        parts.append(f'  <rect x="{px}" y="{y}" width="{pw}" height="26" fill="{SURFACE}"/>')
        parts.append(t(px + 12, y + 17.5, step, 13, INK))
        parts.append(t(px + pw - 12, y + 17.5, where, 13, MUTED, 400, "end"))
    write(p["file"], svg(w, h, "\n".join(parts), f'{p["name"]}: {p["text"]}'))


# ---------------------------------------------------------------- stack

STACK = [
    ("Languages", ["Java", "TypeScript", "JavaScript", "Python"]),
    ("Backend", ["Spring Boot", "Node.js", "Express", "REST APIs"]),
    ("Data", ["PostgreSQL", "Redis", "SQL Server", "MySQL", "SQLite"]),
    ("Cloud, delivery", ["AWS SQS", "AWS S3", "Docker", "Railway", "Cloudflare R2", "GitHub Actions"]),
    ("AI", ["Gemini", "AWS Bedrock", "MCP"]),
    ("Frontend", ["React", "Vite", "Tailwind CSS"]),
    ("Tools", ["Git", "Postman", "Swagger"]),
    ("Learning next", ["AWS architecture", "Next.js"]),
]
CORE = {"Java", "Spring Boot", "PostgreSQL", "AWS SQS"}


def stack_card():
    pad, row_h = 32, 40
    h = pad + len(STACK) * row_h + pad - 14
    parts = []
    for i, (label, tools) in enumerate(STACK):
        y = pad + i * row_h
        parts.append(t(pad, y + 18, label, 14, MUTED))
        parts.append(chips(190, y, tools, FULL - 190 - pad, 13, CORE))
    write("stack.svg", svg(FULL, h, "\n".join(parts), "Stack: " + "; ".join(f"{l}: {', '.join(v)}" for l, v in STACK)))


if __name__ == "__main__":
    header()
    for name, label in [("portfolio", "Portfolio"), ("linkedin", "LinkedIn"), ("email", "Email"), ("facebook", "Facebook")]:
        button(name, label)
    now_card()
    principles_card()
    featured_card(FEATURED)
    for project in PROJECTS:
        project_card(project)
    stack_card()
