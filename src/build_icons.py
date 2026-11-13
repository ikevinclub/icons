"""Generate Qure-style (white monochrome, transparent bg, 108x108, glyph 72x72) icons."""
import re, os
from PIL import Image, ImageDraw

SS = 8                      # supersample factor
SIZE = 108
PAD = 18                    # glyph box = 72x72 inside 108

# ---------------- SVG path parsing / flattening ----------------
NUM = re.compile(r'[A-Za-z]|-?\d*\.?\d+(?:[eE][-+]?\d+)?')


def tokenize(d):
    return NUM.findall(d)


def flatten_cubic(p0, p1, p2, p3, n=48):
    pts = []
    for i in range(1, n + 1):
        t = i / n
        mt = 1 - t
        x = mt**3*p0[0] + 3*mt*mt*t*p1[0] + 3*mt*t*t*p2[0] + t**3*p3[0]
        y = mt**3*p0[1] + 3*mt*mt*t*p1[1] + 3*mt*t*t*p2[1] + t**3*p3[1]
        pts.append((x, y))
    return pts


def parse_path(d):
    """Return list of closed polygons (list of (x,y))."""
    toks = tokenize(d)
    i = 0
    polys, cur = [], []
    x = y = 0.0
    start = (0.0, 0.0)
    prev_ctrl = None
    cmd = None

    def need(n):
        nonlocal i
        vals = []
        while len(vals) < n:
            vals.append(float(toks[i])); i += 1
        return vals

    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            i += 1
            if cmd in 'zZ':
                if cur:
                    polys.append(cur); cur = []
                x, y = start
                prev_ctrl = None
                continue
        rel = cmd.islower()
        c = cmd.upper()
        if c == 'M':
            nx, ny = need(2)
            if rel:
                nx, ny = x + nx, y + ny
            if cur:
                polys.append(cur)
            cur = [(nx, ny)]
            x, y = nx, ny
            start = (nx, ny)
            prev_ctrl = None
            cmd = 'l' if rel else 'L'      # subsequent coords are lineto
        elif c == 'L':
            nx, ny = need(2)
            if rel:
                nx, ny = x + nx, y + ny
            cur.append((nx, ny)); x, y = nx, ny
            prev_ctrl = None
        elif c == 'C':
            x1, y1, x2, y2, nx, ny = need(6)
            if rel:
                x1, y1 = x + x1, y + y1
                x2, y2 = x + x2, y + y2
                nx, ny = x + nx, y + ny
            cur += flatten_cubic((x, y), (x1, y1), (x2, y2), (nx, ny))
            prev_ctrl = (x2, y2); x, y = nx, ny
        elif c == 'S':
            x2, y2, nx, ny = need(4)
            if rel:
                x2, y2 = x + x2, y + y2
                nx, ny = x + nx, y + ny
            if prev_ctrl:
                x1 = 2*x - prev_ctrl[0]
                y1 = 2*y - prev_ctrl[1]
            else:
                x1, y1 = x, y
            cur += flatten_cubic((x, y), (x1, y1), (x2, y2), (nx, ny))
            prev_ctrl = (x2, y2); x, y = nx, ny
        else:
            raise ValueError('unsupported command ' + cmd)
    if cur:
        polys.append(cur)
    return polys


def render_polys_eo(polys, box, viewbox=24.0, ss=SS):
    """Even-odd rasterise polygons into a supersampled L mask fitted into box (x,y,w,h)."""
    W = int(round(box[2] * ss))
    H = int(round(box[3] * ss))
    acc = Image.new('1', (W, H), 0)
    sx = W / viewbox
    sy = H / viewbox
    for poly in polys:
        m = Image.new('1', (W, H), 0)
        d = ImageDraw.Draw(m)
        pts = [(px * sx, py * sy) for px, py in poly]
        if len(pts) >= 3:
            d.polygon(pts, fill=1)
        acc = Image.frombytes('1', (W, H), bytes(
            a ^ b for a, b in zip(acc.tobytes(), m.tobytes())))
    # expand 1-bit -> 8-bit
    return acc.convert('L').point(lambda v: 255 if v else 0)


def finish(mask, size=SIZE, out='out.png', fill=(255, 255, 255)):
    """Crop to ink, scale so longest side = SIZE-2*PAD, centre on transparent SIZE canvas."""
    bbox = mask.getbbox()
    mask = mask.crop(bbox)
    target = size - 2 * PAD
    w, h = mask.size
    scale = target / max(w, h)
    nw, nh = max(1, round(w * scale)), max(1, round(h * scale))
    mask = mask.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new('L', (size, size), 0)
    canvas.paste(mask, ((size - nw) // 2, (size - nh) // 2))
    img = Image.new('RGBA', (size, size), (fill[0], fill[1], fill[2], 0))
    img.putalpha(canvas)
    px = img.load()
    for yy in range(size):
        for xx in range(size):
            r, g, b, a = px[xx, yy]
            if a:
                px[xx, yy] = (fill[0], fill[1], fill[2], a)
    img.save(out)
    return img


def render_siri_wave(ss=SS, bar_w=6.4, gap=4.2, heights=(22, 42, 64, 72, 64, 42, 22)):
    """Qure-style Siri mark: symmetric rounded-bar voice waveform."""
    n = len(heights)
    total_w = n * bar_w + (n - 1) * gap
    W = int(round(total_w * ss))
    H = int(round(max(heights) * ss))
    m = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(m)
    cx = W / 2.0
    x0 = cx - total_w * ss / 2.0
    for i, h in enumerate(heights):
        left = x0 + i * (bar_w + gap) * ss
        bh = h * ss
        top = (H - bh) / 2.0
        d.rounded_rectangle([left, top, left + bar_w * ss, top + bh],
                            radius=bar_w * ss / 2.0, fill=255)
    return m


if __name__ == '__main__':
    HERE = os.path.dirname(os.path.abspath(__file__))
    os.chdir(HERE)
    ROOT = os.path.normpath(os.path.join(HERE, '..'))

    # ---- Spotify ----
    svg = open('spotify_si.svg', encoding='utf8').read()
    d = re.search(r'd="([^"]+)"', svg).group(1)
    polys = parse_path(d)
    print('subpaths:', len(polys))
    mask = render_polys_eo(polys, (0, 0, 24 * SS, 24 * SS))
    os.makedirs(os.path.join(ROOT, 'light-theme'), exist_ok=True)
    DARK = (34, 34, 34)
    finish(mask, out=os.path.join(ROOT, 'Spotify.png'))
    finish(mask, out=os.path.join(ROOT, 'light-theme', 'Spotify.png'), fill=DARK)
    print('Spotify.png + light-theme/Spotify.png written')

    # ---- Siri ----
    siri = render_siri_wave()
    finish(siri, out=os.path.join(ROOT, 'Siri.png'))
    finish(siri, out=os.path.join(ROOT, 'light-theme', 'Siri.png'), fill=DARK)
    print('Siri.png + light-theme/Siri.png written')
