"""Bannière animée du profil GitHub (assets/banner.svg) : textes en tracés Oswald, animations CSS.
Usage : python tools/make_banner.py"""
import re
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

ROOT = Path(__file__).resolve().parents[1]
FONTS = Path('C:/Users/USER/AppData/Local/Microsoft/Windows/Fonts')
LOGO = Path('C:/Users/USER/motion/brand/grafitt-dev/logo/grafitt-dev-color-on-dark.svg')
OR, RED, CH, GR = '#F15A29', '#ED1C24', '#1C1C1E', '#8E8E93'


def text_paths(font_file, text, size, x, y, track=0):
    """Une liste de (d, avance) par caractère : tracés posés sur la ligne de base y."""
    f = TTFont(font_file); gs = f.getGlyphSet(); cmap = f.getBestCmap(); upm = f['head'].unitsPerEm
    s = size / upm; out = []; cx = x
    for ch in text:
        g = cmap.get(ord(ch))
        adv = f['hmtx'][g][0] * s if g else size * 0.3
        if g and ch != ' ':
            pen = SVGPathPen(gs)
            gs[g].draw(TransformPen(pen, (s, 0, 0, -s, cx, y)))
            out.append((pen.getCommands(), cx, adv))
        cx += adv + track
    return out, cx - track - x


def logo_inner():
    s = LOGO.read_text(encoding='utf-8')
    vb = re.search(r'viewBox="([^"]+)"', s).group(1)
    inner = re.sub(r'^<svg[^>]*>|</svg>\s*$', '', s.strip())
    inner = re.sub(r'<title>.*?</title>', '', inner)
    inner = re.sub(r' id="[^"]*"', '', inner)
    return vb, inner


def main():
    W, H = 1280, 400
    bold, med = FONTS / 'Oswald-Bold.ttf', FONTS / 'Oswald-Medium.ttf'
    name, nw = text_paths(bold, 'HERVÉ WOGNIN', 118, 72, 236, track=2)
    sub, sw = text_paths(med, 'DÉVELOPPEUR FULL-STACK  ·  DESIGNER UI/UX  ·  DATA', 24, 76, 306, track=4.2)
    loc, lw = text_paths(med, 'ABIDJAN, CÔTE D’IVOIRE', 15, 76, 350, track=3.5)
    vb, logo = logo_inner()

    css = f"""
    .l {{ opacity:0; transform-box:fill-box; animation: up .7s cubic-bezier(.2,.8,.2,1) forwards; }}
    @keyframes up {{ from {{ opacity:0; transform: translateY(36px); }} to {{ opacity:1; transform:none; }} }}
    .fade {{ opacity:0; animation: fade .9s ease forwards; }}
    @keyframes fade {{ to {{ opacity:1; }} }}
    .grow {{ transform-box:fill-box; transform-origin:left center; transform:scaleX(0); animation: grow .8s cubic-bezier(.2,.8,.2,1) forwards; }}
    @keyframes grow {{ to {{ transform:scaleX(1); }} }}
    .type {{ transform-box:fill-box; transform-origin:left center; transform:scaleX(0); animation: type 6s steps(24) infinite; }}
    @keyframes type {{ 0% {{ transform:scaleX(0); }} 40%,85% {{ transform:scaleX(1); }} 100% {{ transform:scaleX(0); }} }}
    .blink {{ animation: blink 1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity:0; }} }}
    .drift {{ animation: drift 18s linear infinite; }}
    @keyframes drift {{ to {{ transform: translate(-28px, -28px); }} }}
    .pulse {{ transform-box:fill-box; transform-origin:center; animation: pulse 2.4s ease-in-out infinite; }}
    @keyframes pulse {{ 0%,100% {{ transform:scale(1); opacity:.9; }} 50% {{ transform:scale(1.35); opacity:.35; }} }}
    """
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Hervé Wognin, développeur full-stack, designer UI/UX et data, Abidjan">',
             f'<style>{css}</style>',
             '<defs><pattern id="dots" width="28" height="28" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.3" fill="#ffffff" fill-opacity=".07"/></pattern>',
             f'<clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath></defs>',
             '<g clip-path="url(#card)">',
             f'<rect width="{W}" height="{H}" fill="{CH}"/>',
             f'<rect class="drift" x="0" y="0" width="{W + 60}" height="{H + 60}" fill="url(#dots)"/>',
             f'<circle cx="1130" cy="420" r="230" fill="{OR}" fill-opacity=".10"/>']
    # logo Grafitt Dev (version sur fond sombre)
    vx, vy, vw, vh = map(float, vb.split())
    lw_ = 150; sc = lw_ / vw
    parts.append(f'<g class="fade" style="animation-delay:.1s" transform="translate(72 44) scale({sc:.5f}) translate({-vx} {-vy})">{logo}</g>')
    # nom, lettre par lettre
    for i, (d, x, adv) in enumerate(name):
        parts.append(f'<path class="l" style="animation-delay:{.25 + i * .06:.2f}s" fill="#FFFFFF" d="{d}"/>')
    # barres signature
    parts.append(f'<rect class="grow" style="animation-delay:1.1s" x="72" y="254" width="120" height="8" fill="{RED}"/>')
    parts.append(f'<rect class="grow" style="animation-delay:1.3s" x="140" y="266" width="{nw - 68:.0f}" height="4" fill="{OR}"/>')
    parts.append('<g class="fade" style="animation-delay:1.4s">' + ''.join(f'<path fill="{OR}" d="{d}"/>' for d, _, _ in sub) + '</g>')
    parts.append('<g class="fade" style="animation-delay:1.7s">' + ''.join(f'<path fill="{GR}" d="{d}"/>' for d, _, _ in loc) + '</g>')
    parts.append(f'<circle class="pulse" cx="{80 + lw + 18:.0f}" cy="345" r="5" fill="{OR}"/>')
    # fenêtre de code à droite
    cx, cy, cw, chh = 900, 70, 310, 230
    win = [f'<g class="fade" style="animation-delay:.9s"><rect x="{cx}" y="{cy}" width="{cw}" height="{chh}" rx="14" fill="#26262A" stroke="#3A3A40"/>']
    for k, c in enumerate([RED, '#F1962A', '#5A5A62']):
        win.append(f'<circle cx="{cx + 22 + k * 18}" cy="{cy + 20}" r="5.5" fill="{c}"/>')
    rows = [(40, OR, 150), (40, '#D0D0D6', 220), (64, '#7A7A84', 170), (64, '#D0D0D6', 120), (40, OR, 90), (40, '#D0D0D6', 200), (64, '#7A7A84', 140)]
    for j, (ix, col, w) in enumerate(rows):
        y = cy + 52 + j * 24
        win.append(f'<rect class="type" style="animation-delay:{1.2 + j * .45:.2f}s" x="{cx + ix - 18}" y="{y}" width="{w}" height="9" rx="4.5" fill="{col}"/>')
    win.append(f'<rect class="blink" x="{cx + 22}" y="{cy + chh - 34}" width="10" height="16" fill="{OR}"/></g>')
    parts += win
    parts.append('</g></svg>')
    out = ROOT / 'assets' / 'banner.svg'; out.parent.mkdir(exist_ok=True)
    out.write_text('\n'.join(parts), encoding='utf-8')
    print(out, round(out.stat().st_size / 1024), 'Ko', 'largeur du nom', round(nw))


if __name__ == '__main__':
    main()
