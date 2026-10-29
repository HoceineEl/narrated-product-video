import base64, json, os, sys, urllib.request, time
KEY = os.environ['GEMINI_API_KEY']
def synth(text, voice, style, out, model='gemini-3.8-flash-tts', tries=2):
    body = {"model": model,
            "input": [{"type": "user_input", "content": [{"type": "text", "text": text,
                       "annotations": [{"type": "speech_metadata", "style": style}] if style else []}]}],
            "response_format": {"type": "audio", "mime_type": "audio/wav", "sample_rate": 24000},
            "generation_config": {"speech_config": [{"voice": voice}]}}
    for i in range(tries):
        try:
            req = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/interactions",
                data=json.dumps(body).encode(), headers={"x-goog-api-key": KEY, "Content-Type": "application/json"})
            r = json.load(urllib.request.urlopen(req, timeout=900))
            data = None
            for st in r.get('steps', []):
                for c in st.get('content', []):
                    if c.get('type') == 'audio' and c.get('data'): data = c['data']
            if not data: raise RuntimeError('no audio: ' + json.dumps(r)[:400])
            open(out, 'wb').write(base64.b64decode(data)); return out
        except urllib.error.HTTPError as e:
            print('HTTP', e.code, e.read()[:300].decode(errors='ignore'), file=sys.stderr); time.sleep(20 * (i + 1))
        except Exception as e:
            print('ERR', e, file=sys.stderr); time.sleep(3)
    return None
if __name__ == '__main__':
    voice, style, text, out = sys.argv[1:5]
    print(synth(text, voice, style, out))
