#!/usr/bin/env python3
"""Reframe a 16:9 master into a 9:16, 4:5 or 1:1 cutdown with safe zones and burned captions for muted feeds.

  cutdown.py final.mp4 --aspect 9:16 --out reel.mp4 [--range 0-15] [--captions words.json] [--zoom 1.25 --focus 0.4]
  cutdown.py final.mp4 --aspect 4:5 --captions words.json --accent "#14B8A6" --out feed.mp4
  cutdown.py final.mp4 --aspect 9:16 --safe-sheet 6.5 --out check.png       one frame with the unsafe zones in red

The picture sits inside the safe area over a blurred, darkened copy of itself (or --bg "#hex"). --zoom > 1
crops the sides around --focus (0 left, 1 right) so the UI fills more of the narrow frame. Captions come from a
Parakeet transcript (list of {text, start, end}, or {"words": [...]}); chunks of --words words (3 for 9:16,
5 otherwise) break on punctuation and pauses over 0.25 s, stay at least 1/3 s, and light the spoken word in
--accent. Captions and the safe sheet need Pillow (pip install pillow). Output: H.264 High, yuv420p, bt709,
+faststart, AAC 48 kHz (a silent track is added when the master has none).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

FORMATS = {'9:16': (1080, 1920), '4:5': (1080, 1350), '1:1': (1080, 1080)}
SAFE = {'9:16': (220, 320, 60, 120), '4:5': (90, 90, 60, 60), '1:1': (60, 60, 60, 60)}
FONTS = ['/System/Library/Fonts/Supplemental/Arial Bold.ttf', '/Library/Fonts/Arial Bold.ttf',
         '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/TTF/DejaVuSans-Bold.ttf',
         'C:/Windows/Fonts/arialbd.ttf']


def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,width,height:format=duration',
                          '-of', 'json', path], capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    v = next(s for s in d['streams'] if s['codec_type'] == 'video')
    has_audio = any(s['codec_type'] == 'audio' for s in d['streams'])
    return v['width'], v['height'], float(d['format']['duration']), has_audio


def layout(aspect, src_w, src_h, zoom, captions):
    W, H = FORMATS[aspect]
    top, bottom, _, _ = SAFE[aspect]
    pw = int(round(W * zoom / 2) * 2)
    ph = int(round(pw * src_h / src_w / 2) * 2)
    band = 260 if captions else 0
    room = H - top - bottom
    y = top + max(0, (room - ph - band) // 2)
    return W, H, pw, ph, y, y + ph + 30


def pil():
    try:
        from PIL import Image, ImageDraw, ImageFont
        return Image, ImageDraw, ImageFont
    except ImportError:
        sys.exit('captions and --safe-sheet need Pillow: pip install pillow')


def font(path, size):
    _, _, ImageFont = pil()
    for p in [path] + FONTS:
        if p and os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default(size)


def chunks(words, max_words):
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        brk = w['text'].rstrip()[-1:] in '.,!?;:' or nxt is None or nxt['start'] - w['end'] > 0.25
        if len(cur) >= max_words or brk:
            out.append(cur)
            cur = []
    return out


def caption_track(words, aspect, start, end, accent, font_path, work):
    Image, ImageDraw, _ = pil()
    W, _ = FORMATS[aspect]
    _, _, left, right = SAFE[aspect]
    max_w = W - left - right
    f = font(font_path, 78 if aspect == '9:16' else 64)
    words = [w for w in words if w['end'] > start and w['start'] < end]
    groups = chunks(words, 3 if aspect == '9:16' else 5)
    blank = os.path.join(work, 'blank.png')
    Image.new('RGBA', (W, 230), (0, 0, 0, 0)).save(blank)
    events = []
    for gi, g in enumerate(groups):
        g_end = g[-1]['end'] + 0.15
        nxt = groups[gi + 1][0]['start'] if gi + 1 < len(groups) else end
        if nxt - g_end < 0.6:
            g_end = nxt
        g_end = max(g_end, g[0]['start'] + 0.34)
        for wi, w in enumerate(g):
            img = Image.new('RGBA', (W, 230), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            lines, line = [], []
            for x in g:
                trial = ' '.join(t['text'].strip() for t in line + [x])
                if line and d.textlength(trial, font=f) > max_w:
                    lines.append(line)
                    line = []
                line.append(x)
            lines.append(line)
            y = (230 - len(lines) * 92) // 2
            for ln in lines:
                lw = d.textlength(' '.join(t['text'].strip() for t in ln), font=f)
                x0 = left + (max_w - lw) / 2
                for t in ln:
                    word = t['text'].strip()
                    fill = accent if t is w else '#FFFFFF'
                    d.text((x0, y), word, font=f, fill=fill, stroke_width=5, stroke_fill=(10, 12, 16, 230))
                    x0 += d.textlength(word + ' ', font=f)
                y += 92
            path = os.path.join(work, f'c{gi:03d}_{wi:02d}.png')
            img.save(path)
            w_end = g[wi + 1]['start'] if wi + 1 < len(g) else g_end
            events.append((max(w['start'], start) - start, min(w_end, end) - start, path))
    lst, t = [], 0.0
    for a, b, path in events:
        if a > t + 0.001:
            lst.append((blank, a - t))
        lst.append((path, max(0.034, b - max(a, t))))
        t = max(t, b)
    if end - start > t:
        lst.append((blank, end - start - t))
    listfile = os.path.join(work, 'captions.txt')
    with open(listfile, 'w') as fh:
        for path, dur in lst:
            fh.write(f"file '{path}'\nduration {dur:.3f}\n")
        fh.write(f"file '{lst[-1][0]}'\n")
    return listfile


def build(a):
    sw, sh, dur, has_audio = probe(a.src)
    start, end = 0.0, dur
    if a.range:
        s, _, e = a.range.partition('-')
        start, end = float(s), float(e or dur)
    W, H, pw, ph, y, cap_y = layout(a.aspect, sw, sh, a.zoom, bool(a.captions))
    cx = int(max(0, min(pw - W, a.focus * (pw - W))))
    if a.bg == 'blur':
        bg = f'[0:v]scale=-2:{H},crop={W}:{H},gblur=sigma=38,colorchannelmixer=rr=.42:gg=.42:bb=.42[bg]'
    else:
        bg = f'color=c={a.bg.replace("#", "0x")}:s={W}x{H}:r=30,format=yuv420p[bg]'
    fg = f'[0:v]scale={pw}:{ph}:flags=lanczos,crop={min(W, pw)}:{ph}:{cx}:0[fg]'
    graph = [bg, fg, f'[bg][fg]overlay=x=(W-w)/2:y={y}:shortest=1[pic]']
    last = '[pic]'
    inputs = ['-ss', f'{start:.3f}', '-to', f'{end:.3f}', '-i', a.src]
    work = tempfile.mkdtemp(prefix='cutdown-')
    if a.captions:
        words = json.load(open(a.captions))
        words = words if isinstance(words, list) else words['words']
        listfile = caption_track(words, a.aspect, start, end, a.accent, a.font, work)
        inputs += ['-f', 'concat', '-safe', '0', '-i', listfile]
        graph.append(f'[1:v]format=rgba,setpts=PTS-STARTPTS[cap];{last}[cap]overlay=x=0:y={cap_y}:eof_action=pass[capd]')
        last = '[capd]'
    graph.append(f'{last}format=yuv420p,setsar=1[v]')
    return inputs, graph, start, end, has_audio, work, (W, H, y, ph, cap_y)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('src')
    p.add_argument('--aspect', choices=sorted(FORMATS), default='9:16')
    p.add_argument('--out', required=True)
    p.add_argument('--range', help='start-end in seconds, e.g. 0-15')
    p.add_argument('--captions', help='Parakeet word list JSON')
    p.add_argument('--accent', default='#FFD43B', help='colour of the spoken word')
    p.add_argument('--font', help='TTF/OTF for captions (default: a bold system sans)')
    p.add_argument('--bg', default='blur', help='blur (default) or a "#hex" colour')
    p.add_argument('--zoom', type=float, default=1.0, help='picture width as a multiple of the frame width')
    p.add_argument('--focus', type=float, default=0.5, help='horizontal focus when --zoom crops (0-1)')
    p.add_argument('--safe-sheet', type=float, metavar='T', help='write one frame at T with unsafe zones marked')
    a = p.parse_args()

    inputs, graph, start, end, has_audio, work, (W, H, y, ph, cap_y) = build(a)
    try:
        if a.safe_sheet is not None:
            t = max(0.0, a.safe_sheet - start)
            frame = os.path.join(work, 'frame.png')
            subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', ';'.join(graph), '-map', '[v]',
                            '-ss', f'{t:.3f}', '-frames:v', '1', frame], check=True)
            Image, ImageDraw, _ = pil()
            img = Image.open(frame).convert('RGBA')
            over = Image.new('RGBA', img.size, (0, 0, 0, 0))
            d = ImageDraw.Draw(over)
            top, bottom, left, right = SAFE[a.aspect]
            for box in ((0, 0, W, top), (0, H - bottom, W, H), (0, 0, left, H), (W - right, 0, W, H)):
                d.rectangle(box, fill=(255, 40, 40, 90))
            d.rectangle((left, top, W - right, H - bottom), outline=(255, 255, 255, 200), width=3)
            Image.alpha_composite(img, over).convert('RGB').save(a.out)
            print(f'wrote {a.out}: picture y {y}-{y + ph}, captions from y {cap_y}, safe {SAFE[a.aspect]} (top, bottom, left, right)')
            return
        audio = []
        if has_audio:
            fade_out = max(0.0, end - start - 0.3)
            audio = ['-map', '0:a:0', '-af', f'afade=t=in:d=0.02,afade=t=out:st={fade_out:.3f}:d=0.3']
        else:
            inputs += ['-f', 'lavfi', '-t', f'{end - start:.3f}', '-i', 'anullsrc=r=48000:cl=stereo']
            audio = ['-map', f'{inputs.count("-i") - 1}:a:0']
        subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', ';'.join(graph), '-map', '[v]', *audio,
                        '-t', f'{end - start:.3f}', '-r', '30', '-c:v', 'libx264', '-profile:v', 'high', '-crf', '18',
                        '-preset', 'medium', '-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-color_primaries', 'bt709',
                        '-color_trc', 'bt709', '-color_range', 'tv', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
                        '-movflags', '+faststart', a.out], check=True)
        print(f'wrote {a.out}: {W}x{H}, {end - start:.2f}s, picture at y {y}, captions {"on" if a.captions else "off"}')
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == '__main__':
    main()
