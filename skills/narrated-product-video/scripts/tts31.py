import base64, json, subprocess, sys, time, urllib.request
URL = "https://generativelanguage.googleapis.com/v1beta/interactions"


def synth(text, voice, style, out, key, tries=3):
    body = {"model": "gemini-3.1-flash-tts-preview",
            "input": [{"type": "user_input", "content": [{"type": "text", "text": text,
                       "annotations": [{"type": "speech_metadata", "style": style}] if style else []}]}],
            "generation_config": {"speech_config": [{"voice": voice}]}}
    for i in range(tries):
        try:
            req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"x-goog-api-key": key, "Content-Type": "application/json"})
            r = json.load(urllib.request.urlopen(req, timeout=900))
            pcm = b''.join(base64.b64decode(c['data']) for s in r.get('steps', []) for c in s.get('content', []) if c.get('type') == 'audio')
            if not pcm:
                raise RuntimeError(json.dumps(r)[:300])
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', '24000', '-ac', '1', '-i', '-', out], input=pcm, check=True)
            return out
        except urllib.error.HTTPError as e:
            msg = e.read()[:300].decode(errors='ignore')
            print('HTTP', e.code, msg, file=sys.stderr)
            if e.code in (400, 402) or 'per day' in msg:
                return None
            time.sleep(25)
        except Exception as e:
            print('ERR', e, file=sys.stderr); time.sleep(5)
    return None
