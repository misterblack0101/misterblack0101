"""Builds the README's SVGs (stat cards, section headings, buttons) in the portfolio's style.

Space Grotesk is subset and inlined, since GitHub renders SVGs as <img> and they can't fetch fonts.
Usage: python3 scripts/svgs.py   (needs: pip install fonttools brotli)
"""
import base64, io, pathlib, re, subprocess
from xml.sax.saxutils import escape as esc
from fontTools import subset
from fontTools.ttLib import TTFont

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets"
RED = "#e22928"
CHARS = "".join(chr(c) for c in range(32, 127)) + "↗→·–&"


def curl(*args):  # curl over urllib: python.org builds on macOS ship without CA certs
    return subprocess.run(["curl", "-sfL", *args], check=True, capture_output=True).stdout


def font(weight):
    css = curl("-A", "Mozilla/4.0", f"https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@{weight}").decode()
    ttf = curl(re.search(r"url\((https://[^)]+)\)", css)[1])
    f = TTFont(io.BytesIO(ttf))
    s = subset.Subsetter()
    s.populate(text=CHARS)
    s.subset(f)
    f.flavor = "woff2"
    buf = io.BytesIO()
    f.save(buf)
    return f, base64.b64encode(buf.getvalue()).decode()


FONTS = {w: font(w) for w in (400, 700)}


def width(text, weight, size):
    f = FONTS[weight][0]
    cmap, hmtx = f.getBestCmap(), f["hmtx"]
    return sum(hmtx[cmap[ord(c)]][0] for c in text if ord(c) in cmap) * size / f["head"].unitsPerEm


def svg(w, h, body, css="", weights=(700,)):
    faces = "".join(
        f"@font-face{{font-family:SG;font-weight:{wt};src:url(data:font/woff2;base64,{FONTS[wt][1]}) format('woff2')}}"
        for wt in weights)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f"<style>{faces}text{{font-family:SG,'Segoe UI',Helvetica,Arial,sans-serif}}{css}</style>{body}</svg>")


def stats(items):
    gap, w, h = 16, 284, 176
    cards = []
    for i, (num, label, sub) in enumerate(items):
        x = i * (w + gap)
        cards.append(
            f'<g transform="translate({x} 0)"><g class="c" style="animation-delay:{i * 0.12:.2f}s">'
            f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="24" fill="#111" stroke="#ffffff14"/>'
            f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="24" fill="url(#glow)"/>'
            f'<text x="28" y="84" font-size="54" font-weight="700" fill="{RED}" letter-spacing="-1.5">{esc(num)}</text>'
            f'<text x="28" y="122" font-size="15" font-weight="700" fill="#ffffffb3" letter-spacing="1.6">{esc(label.upper())}</text>'
            f'<text x="28" y="146" font-size="14" fill="#ffffff59">{esc(sub)}</text></g></g>')
    defs = ('<defs><radialGradient id="glow" cx="1" cy="0" r="1">'
            f'<stop offset="0" stop-color="{RED}" stop-opacity=".22"/><stop offset=".7" stop-color="{RED}" stop-opacity="0"/>'
            '</radialGradient></defs>')
    css = (".c{animation:up .7s cubic-bezier(.2,.8,.2,1) both}"
           "@keyframes up{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}")
    return svg(4 * w + 3 * gap, h, defs + "".join(cards), css, weights=(400, 700))


def heading(label, title, fg):
    return svg(1200, 110,
               f'<text x="2" y="26" font-size="17" font-weight="700" fill="{RED}" letter-spacing="3">{esc(label.upper())}</text>'
               f'<text y="94" font-size="62" font-weight="700" fill="{fg}" letter-spacing="-2">{esc(title)}</text>')


def hero(fg, muted, panel):
    lines = ["I write code so your phone does cool things.", "Powered by Flutter & AI.", "Loved by 3M+ users."]
    n = len(lines)
    rotating = "".join(
        f'<text class="t" x="0" y="268" font-size="30" fill="{muted}" style="animation-delay:{i * 3}s">{esc(t)}</text>'
        for i, t in enumerate(lines))
    # phone mockup: cards slide in one after another, then the loop restarts
    cards = "".join(
        f'<rect class="k" x="902" y="{96 + i * 58}" width="{196 - i * 30}" height="42" rx="12" fill="{RED if i == 0 else panel}" '
        f'style="animation-delay:{i * .35}s"/>' for i in range(4))
    body = (
        f'<text x="2" y="70" font-size="20" font-weight="700" fill="{RED}" letter-spacing="4">FLUTTER · AI · 3M+ USERS</text>'
        f'<text y="196" font-size="132" font-weight="700" fill="{fg}" letter-spacing="-5">Hi, I\'m <tspan fill="{RED}">Harsh</tspan>'
        f'<tspan class="cur" fill="{RED}">_</tspan></text>'
        f'{rotating}'
        f'<g class="ph"><rect x="884" y="40" width="232" height="300" rx="36" fill="none" stroke="{fg}" stroke-opacity=".25" stroke-width="3"/>'
        f'<rect x="966" y="56" width="68" height="10" rx="5" fill="{fg}" fill-opacity=".2"/>{cards}'
        f'<circle class="dot" cx="1110" cy="46" r="14" fill="{RED}"/></g>')
    css = (f".t{{opacity:0;animation:rot {3 * n}s infinite}}"
           f"@keyframes rot{{0%{{opacity:0;transform:translateY(12px)}}4%,{100 / n - 4:.0f}%{{opacity:1;transform:none}}"
           f"{100 / n:.0f}%,100%{{opacity:0;transform:translateY(-12px)}}}}"
           ".cur{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
           ".k{opacity:0;animation:k 4s cubic-bezier(.2,.8,.2,1) infinite}"
           "@keyframes k{0%{opacity:0;transform:translateX(30px)}15%,85%{opacity:1;transform:none}100%{opacity:0}}"
           ".ph{animation:float 6s ease-in-out infinite}@keyframes float{50%{transform:translateY(-10px)}}"
           ".dot{transform-origin:1110px 46px;animation:pulse 2s infinite}@keyframes pulse{50%{transform:scale(.7);opacity:.6}}")
    return svg(1200, 360, body, css, weights=(400, 700))


def button(text, primary, w):
    size, h = 26, 64
    # transparent outline reads on both light and dark GitHub themes
    bg, fg, stroke = (RED, "#fff", RED) if primary else ("none", RED, RED)
    return svg(w, h,
               f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{h / 2 - 1}" fill="{bg}" stroke="{stroke}" stroke-width="2"/>'
               f'<text x="{w / 2}" y="{h / 2 + 9}" text-anchor="middle" font-size="{size}" font-weight="700" fill="{fg}">{esc(text)}</text>')


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    files = {
        "stats.svg": stats([
            ("3M+", "Global installs", "Consumer apps in production"),
            ("$1.5M+", "ARR scaled", "Trial paywalls & conversion"),
            ("4+ yrs", "Shipping Flutter", "Lead Flutter Dev @ Lingopanda"),
            ("99%", "Crash-free", "High-reliability monitoring"),
        ]),
        "hero-dark.svg": hero("#ffffff", "#ffffffb3", "#ffffff26"),
        "hero-light.svg": hero("#0a0a0a", "#0a0a0ab3", "#0a0a0a1a"),
    }
    # equal widths so the row lines up as one block
    btns = [("work", "See my work ↗"), ("linkedin", "LinkedIn ↗"), ("email", "Email ↗"), ("resume", "Resume ↗")]
    bw = round(max(width(t, 700, 26) for _, t in btns) + 68)
    for i, (key, text) in enumerate(btns):
        files[f"btn-{key}.svg"] = button(text, i == 0, bw)
    for key, label, title in [("scale", "Track record & scale", "Experience"),
                              ("arsenal", "Tech arsenal", "Stack"),
                              ("activity", "Always shipping", "Activity")]:
        files[f"h-{key}-dark.svg"] = heading(label, title, "#ffffff")
        files[f"h-{key}-light.svg"] = heading(label, title, "#0a0a0a")
    for name, content in files.items():
        (OUT / name).write_text(content)
        print(f"{name:24} {len(content) // 1024}KB")
