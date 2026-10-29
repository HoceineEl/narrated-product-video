#!/usr/bin/env python3
"""Ask Gemini to watch a video and answer a review question (optional second opinion).

  vqa.py final.mp4 "List every moment where the narration and the picture disagree, with timestamps."

Uploads the video inline (keep it under ~20 MB) and reads GEMINI_API_KEY. The model invents details
(it has reported background music in films with none), so verify each claim against frames before acting.
"""
import argparse
import base64
import json
import os
import sys
import urllib.request


def ask(video, prompt, model, key):
    parts = [{'inline_data': {'mime_type': 'video/mp4', 'data': base64.b64encode(open(video, 'rb').read()).decode()}},
             {'text': prompt}]
    req = urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
                                 data=json.dumps({'contents': [{'parts': parts}]}).encode(),
                                 headers={'Content-Type': 'application/json', 'x-goog-api-key': key})
    r = json.load(urllib.request.urlopen(req, timeout=600))
    return r['candidates'][0]['content']['parts'][0]['text']


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('video')
    p.add_argument('prompt')
    p.add_argument('--model', default='gemini-3.5-flash')
    a = p.parse_args()
    key = os.environ.get('GEMINI_API_KEY') or sys.exit('GEMINI_API_KEY is not set')
    print(ask(a.video, a.prompt, a.model, key))


if __name__ == '__main__':
    main()
