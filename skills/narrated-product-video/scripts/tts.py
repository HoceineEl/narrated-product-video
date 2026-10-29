#!/usr/bin/env python3
"""Gemini text-to-speech for voice-overs.

Examples:
  tts.py --check
  tts.py --voice en-us-podcaster-1 --style "A developer showing a tool to a friend" --text "Hit Alt, Shift, C." --out take.wav
  tts.py --voice fr-fr-podcaster-4 --text-file launch.txt --out take.wav --model gemini-3.1-flash-tts-preview

Reads GEMINI_API_KEY from the environment. Writes a 24 kHz mono WAV.
A daily quota error (HTTP 429 "per day") is never retried, because retrying burns quota.
"""
import argparse
import base64
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

HOST = 'generativelanguage.googleapis.com'
API = f'https://{HOST}/v1beta'
WAV_MODELS = {'gemini-3.8-flash-tts'}


def pin_ip(ip):
    real = socket.getaddrinfo

    def resolve(host, *args, **kwargs):
        return real(ip if host == HOST else host, *args, **kwargs)

    socket.getaddrinfo = resolve


def request(url, key, body=None, timeout=900):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers={'x-goog-api-key': key, 'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(req, timeout=timeout))


def check(key):
    models = request(f'{API}/models?pageSize=200', key, timeout=30).get('models', [])
    tts = sorted(m['name'].split('/')[-1] for m in models if 'tts' in m['name'])
    print('key ok; tts models:', ', '.join(tts) or 'none listed')


def synth(key, text, voice, style, out, model, tries=2):
    content = {'type': 'text', 'text': text}
    if style and model in WAV_MODELS:
        content['annotations'] = [{'type': 'speech_metadata', 'style': style}]
    elif style:
        content['text'] = f'{style}:\n{text}'
    body = {'model': model, 'input': [{'type': 'user_input', 'content': [content]}],
            'generation_config': {'speech_config': [{'voice': voice}]}}
    if model in WAV_MODELS:
        body['response_format'] = {'type': 'audio', 'mime_type': 'audio/wav', 'sample_rate': 24000}
    for attempt in range(tries):
        try:
            r = request(f'{API}/interactions', key, body)
            chunks = [base64.b64decode(c['data']) for s in r.get('steps', []) for c in s.get('content', [])
                      if c.get('type') == 'audio' and c.get('data')]
            if not chunks:
                raise RuntimeError('no audio in response: ' + json.dumps(r)[:300])
            if model in WAV_MODELS:
                open(out, 'wb').write(chunks[-1])
            else:
                subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', '24000', '-ac', '1', '-i', '-', out],
                               input=b''.join(chunks), check=True)
            return out
        except urllib.error.HTTPError as e:
            msg = e.read()[:400].decode(errors='ignore')
            print('HTTP', e.code, msg, file=sys.stderr)
            if e.code in (400, 401, 402, 403) or 'per day' in msg.lower():
                return None
            time.sleep(25 * (attempt + 1))
        except (urllib.error.URLError, RuntimeError, OSError) as e:
            print('error:', e, file=sys.stderr)
            time.sleep(5)
    return None


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--check', action='store_true', help='validate the key and list TTS models (free)')
    p.add_argument('--voice', help='voice name, e.g. en-us-podcaster-1, fr-fr-podcaster-4, Charon')
    p.add_argument('--style', default='', help='direction for the read (tone, pace, who is speaking)')
    p.add_argument('--text', help='text to speak')
    p.add_argument('--text-file', help='read the text from a file')
    p.add_argument('--out', help='output .wav path')
    p.add_argument('--model', default='gemini-3.8-flash-tts')
    p.add_argument('--pin-ip', help=f'resolve {HOST} to this IP when local DNS fails')
    a = p.parse_args()
    key = os.environ.get('GEMINI_API_KEY')
    if not key:
        sys.exit('GEMINI_API_KEY is not set')
    if a.pin_ip:
        pin_ip(a.pin_ip)
    if a.check:
        return check(key)
    text = open(a.text_file).read().strip() if a.text_file else a.text
    if not (a.voice and text and a.out):
        p.error('--voice, --text or --text-file, and --out are required')
    out = synth(key, text, a.voice, a.style, a.out, a.model)
    if not out:
        sys.exit('no audio generated')
    print(out)


if __name__ == '__main__':
    main()
