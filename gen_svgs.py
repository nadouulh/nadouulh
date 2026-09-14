import re
import urllib.request
import os

DEVICON = "https://raw.githubusercontent.com/devicons/devicon/master/icons/{name}/{name}-{variant}.svg"

ICONS = {
    "Linux": (DEVICON.format(name="linux", variant="plain"), True),
    "Rust": (DEVICON.format(name="rust", variant="original"), True),
    "Python": (DEVICON.format(name="python", variant="original"), False),
    "Bash": (DEVICON.format(name="bash", variant="original"), True),
    "Google Cloud": (DEVICON.format(name="googlecloud", variant="original"), False),
    "Terraform": (DEVICON.format(name="terraform", variant="original"), False),
    "OpenTofu": ("https://cdn.simpleicons.org/opentofu", False),
    "Docker": (DEVICON.format(name="docker", variant="original"), False),
    "Kubernetes": (DEVICON.format(name="kubernetes", variant="plain"), False),
    "Ansible": (DEVICON.format(name="ansible", variant="original"), True),
    "GitHub Actions": (DEVICON.format(name="githubactions", variant="original"), False),
    "Bitbucket": (DEVICON.format(name="bitbucket", variant="original"), False),
    "GitLab CI": (DEVICON.format(name="gitlab", variant="original"), False),
}

BLOBS = []

HEAD = """<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs>
  <linearGradient id="glassLight" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#d0d0d0" stop-opacity="0.7"/>
    <stop offset="1" stop-color="#e8e8e8" stop-opacity="0.4"/>
  </linearGradient>
  <linearGradient id="glassDark" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0.17"/>
    <stop offset="1" stop-color="#ffffff" stop-opacity="0.03"/>
  </linearGradient>
{grads}
</defs>
<style>
  .glass {{ fill: url(#glassLight); filter: drop-shadow(0 1px 3px rgba(0,0,0,0.12)); backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px); }}
  .border {{ fill: none; stroke: #b0b0b0; stroke-opacity: 0.7; stroke-width: 1; }}
  text {{ fill: #1f2328; font-family: -apple-system,"Segoe UI",Helvetica,Arial,"Apple Color Emoji","Segoe UI Emoji"; }}
  @media (prefers-color-scheme: dark) {{
    .glass {{ fill: url(#glassDark); filter: drop-shadow(0 1px 3px rgba(0,0,0,0.45)); backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px); }}
    .border {{ stroke-opacity: 0.22; }}
    text {{ fill: #e6edf3; }}
    .mono {{ filter: brightness(0) invert(1); }}
  }}
</style>
{body}
</svg>"""


def urlopen(u):
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")


def fetch_icon(name):
    url, mono = ICONS[name]
    raw = urlopen(url)
    raw = re.sub(r"<\?xml[^>]*\?>", "", raw)
    raw = re.sub(r"<!--.*?-->", "", raw, flags=re.S)
    m = re.search(r"<svg[^>]*>", raw)
    if not m:
        raise RuntimeError(f"no svg root for {name}")
    vb = re.search(r"viewBox=\"([^\"]+)\"", m.group(0))
    if not vb:
        raise RuntimeError(f"no viewBox for {name}")
    vx, vy, vw, vh = [float(v) for v in vb.group(1).replace(",", " ").split()]
    inner = raw[m.end():raw.rindex("</svg>")]
    inner = re.sub(r"<(/?)(title)[^>]*>.*?</\2>|<title[^>]*/>", "", inner, flags=re.S)
    inner = re.sub(r"<defs>.*?</defs>", "", inner, flags=re.S)
    return inner, (vx, vy, vw, vh), mono


def box_svg(name, x, y, box=36, ic=26):
    inner, (vx, vy, vw, vh), mono = fetch_icon(name)
    s = min(ic / vw, ic / vh)
    iw, ih = vw * s, vh * s
    ix = x + (box - iw) / 2
    iy = y + (box - ih) / 2
    cls = "mono" if mono else ""
    return '<g><title>{name}</title>'.replace("{name}", name) + (
        '<rect class="glass" x="{}" y="{}" width="{}" height="{}" rx="8"/>').format(
        x, y, box, box) + '<rect class="border" x="{}" y="{}" width="{}" height="{}" rx="8"/>'.format(
        x, y, box, box) + (
        '<g class="{}" transform="translate({} {}) scale({}) translate({} {})">{}</g></g>').format(
        cls, round(ix, 2), round(iy, 2), round(s, 4), int(-vx), int(-vy), inner)


def tech_stack():
    rows = [
        ["Linux", "Rust", "Python", "Bash"],
        ["Google Cloud", "Terraform", "OpenTofu", "Docker", "Kubernetes", "Ansible"],
        ["GitHub Actions", "Bitbucket", "GitLab CI"],
    ]
    BOX, GAP, ROW, M = 36, 8, 8, 4
    widths = [len(r) * (BOX + GAP) - GAP + 2 * M for r in rows]
    W = max(widths)
    H = M * 2 + len(rows) * BOX + (len(rows) - 1) * ROW
    body = []
    y = M
    for r in rows:
        rw = len(r) * (BOX + GAP) - GAP
        x = (W - rw) / 2
        for name in r:
            body.append(box_svg(name, x, y))
            x += BOX + GAP
        y += BOX + ROW
    return HEAD.format(w=W, h=H, grads="", body="\n".join(body))


LANG_PILLS = [
    ("French", "🇫🇷", "Native", "🟢"),
    ("Italian", "🇮🇹", "Native", "🟢"),
    ("English", "🇬🇧", "Fluent", "🔵"),
    ("Arabic", "🇲🇦", "Native", "🟢"),
]


def text_w(s, fs=13, emoji=False):
    if emoji:
        return 16
    return sum(7.5 if (len(c.encode("utf-8")) > 1) else 6.5 for c in s) + 2


def languages():
    FS = 16
    PAD, GAPH, PILLH, GAP = 12, 6, 32, 12
    GAP_ELEMS = 14
    PILL_W = 170
    pills = []
    x = 0
    for name, flag, level, dot in LANG_PILLS:
        pills.append((x, PILL_W, name, flag, level, dot))
        x += PILL_W + GAP
    W = x - GAP
    H = PILLH + 8
    blobs = ""
    body = []
    for px, w, name, flag, level, dot in pills:
        y = 4
        ry = y + (PILLH + FS) / 2
        fx = px + PAD
        tx = px + PAD + 26
        dx = px + PILL_W * 2 // 3
        lx = dx + 22
        body.append((
            '<g><rect class="glass" x="{px}" y="{y}" width="{w}" height="{PILLH}" rx="10"/>'
            '<rect class="border" x="{px}" y="{y}" width="{w}" height="{PILLH}" rx="10"/>'
            '<text x="{fx}" y="{ry}" font-size="{FS}">{flag}</text>'
            '<text x="{tx}" y="{ry}" font-weight="bold" font-size="{FS}">{name}</text>'
            '<text x="{dx}" y="{ry}" font-size="{FS}">{dot}</text>'
            '<text x="{lx}" y="{ry}" font-size="{FS}">{level}</text>'
            "</g>").format(px=px, y=y, w=w, PILLH=PILLH, FS=FS,
                           fx=fx, ry=round(ry, 1), tx=tx, dx=dx, lx=lx,
                           flag=flag, name=name, dot=dot, level=level))
    return HEAD.format(w=W, h=H, grads="", blobs=blobs, body="\n".join(body))


os.makedirs("assets", exist_ok=True)
with open("assets/tech-stack.svg", "w") as f:
    f.write(tech_stack())
with open("assets/languages.svg", "w") as f:
    f.write(languages())
print("generated assets/tech-stack.svg and assets/languages.svg")