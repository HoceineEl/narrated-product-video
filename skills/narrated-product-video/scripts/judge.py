import base64, json, os, sys, urllib.request, glob
KEY=os.environ['GEMINI_API_KEY']
def ask(files, prompt, model='gemini-3.8-flash'):
    parts=[{"text":prompt}]
    for f in files:
        parts.append({"text":f"--- FILE: {os.path.basename(f)}"})
        parts.append({"inline_data":{"mime_type":"audio/wav","data":base64.b64encode(open(f,'rb').read()).decode()}})
    body={"contents":[{"parts":parts}]}
    req=urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={KEY}",data=json.dumps(body).encode(),headers={"Content-Type":"application/json"})
    r=json.load(urllib.request.urlopen(req,timeout=300))
    return r['candidates'][0]['content']['parts'][0]['text']
if __name__=='__main__':
    files=sorted(glob.glob(sys.argv[1]))
    print(ask(files, sys.argv[2]))
