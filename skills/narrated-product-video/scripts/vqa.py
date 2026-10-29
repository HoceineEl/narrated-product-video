import base64, json, os, sys, urllib.request
KEY = os.environ['GEMINI_API_KEY']
def ask(video, prompt, model='gemini-3.5-flash'):
    parts = [{"inline_data": {"mime_type": "video/mp4", "data": base64.b64encode(open(video, 'rb').read()).decode()}}, {"text": prompt}]
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={KEY}", data=json.dumps({"contents": [{"parts": parts}]}).encode(), headers={"Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=600))
    return r['candidates'][0]['content']['parts'][0]['text']
if __name__ == '__main__':
    print(ask(sys.argv[1], sys.argv[2], *(sys.argv[3:4])))
