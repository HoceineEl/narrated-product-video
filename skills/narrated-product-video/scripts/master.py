#!/usr/bin/env python3
"""Master audio with ffmpeg and print loudness.

  master.py voice take.wav take-m.wav     raw TTS take: highpass, EQ, de-ess, compress, -16 LUFS, 48 kHz
  master.py film film.mp4 film-final.mp4  finished video: compress, limit under 0 dBTP after AAC, -14 LUFS
  master.py measure film.mp4              integrated loudness and true peak only
"""
import argparse
import json
import re
import subprocess

VOICE = ('highpass=f=70,equalizer=f=250:t=q:w=1:g=-2,equalizer=f=3500:t=q:w=1.5:g=1.5,deesser=i=0.35,'
         'acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=3,loudnorm=I=-16:TP=-1.5:LRA=7')


def measure(path):
    err = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    summary = err[err.rfind('Summary:'):]
    lufs = float(re.search(r'I:\s+(-?[\d.]+) LUFS', summary).group(1))
    peak = float(re.search(r'Peak:\s+(-?[\d.]+|-inf) dBFS', summary).group(1))
    return lufs, peak


def loudnorm_film(src, dst, lufs):
    chain = f'acompressor=threshold=-26dB:ratio=3:attack=10:release=200:makeup=4,loudnorm=I={lufs}:TP=-2:LRA=9'
    probe = subprocess.run(['ffmpeg', '-hide_banner', '-i', src, '-af', chain + ':print_format=json', '-f', 'null', '-'],
                           capture_output=True, text=True).stderr
    m = json.loads(probe[probe.rindex('{'):probe.rindex('}') + 1])
    second = (f"acompressor=threshold=-26dB:ratio=3:attack=10:release=200:makeup=4,loudnorm=I={lufs}:TP=-2:LRA=9:"
              f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
              f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,"
              'alimiter=limit=0.7:level=false,aresample=48000')
    video = dst.lower().endswith(('.mp4', '.mov', '.mkv', '.webm'))
    codec = ['-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k'] if video else ['-ar', '48000']
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-af', second, *codec, dst], check=True)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('mode', choices=['voice', 'film', 'measure'])
    p.add_argument('src')
    p.add_argument('dst', nargs='?')
    p.add_argument('--lufs', type=float, default=-14.0, help='film target (default -14, social platforms)')
    a = p.parse_args()
    if a.mode != 'measure' and not a.dst:
        p.error('dst is required')
    if a.mode == 'voice':
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', a.src, '-af', VOICE, '-ar', '48000', a.dst], check=True)
    elif a.mode == 'film':
        loudnorm_film(a.src, a.dst, a.lufs)
    lufs, peak = measure(a.dst or a.src)
    print(f'{a.dst or a.src}: {lufs:.1f} LUFS, true peak {peak:.1f} dBTP')


if __name__ == '__main__':
    main()
