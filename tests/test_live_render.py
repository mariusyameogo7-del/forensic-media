import urllib.request
import json
import io
from PIL import Image

base_url = "https://forensic-media-app.onrender.com"

# Create a small valid test JPEG
buf = io.BytesIO()
Image.new("RGB", (200, 200), color=(50, 120, 180)).save(buf, format="JPEG")
img_bytes = buf.getvalue()

boundary = "----WebKitFormBoundaryForensicMediaTest"
body = bytearray()
body.extend(f"--{boundary}\r\n".encode("utf-8"))
body.extend(b'Content-Disposition: form-data; name="file"; filename="test_live.jpg"\r\n')
body.extend(b"Content-Type: image/jpeg\r\n\r\n")
body.extend(img_bytes)
body.extend(b"\r\n")
body.extend(f"--{boundary}\r\n".encode("utf-8"))
body.extend(b'Content-Disposition: form-data; name="claim"\r\n\r\n')
body.extend("Verification de production sur Render\r\n".encode("utf-8"))
body.extend(f"--{boundary}--\r\n".encode("utf-8"))

req = urllib.request.Request(
    f"{base_url}/api/v1/analyses",
    data=bytes(body),
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    method="POST"
)

with urllib.request.urlopen(req) as r:
    data = json.loads(r.read())
    print("[SUCCES 1/3] Analyse creee en direct sur Render !")
    print("  Public ID   :", data.get("public_id"))
    print("  Analysis ID :", data.get("analysis_id"))
    analysis_id = data.get("analysis_id")

# Get result
token = data.get("access_token")
headers = {"X-Analysis-Token": token} if token else {}
req_res = urllib.request.Request(f"{base_url}/api/v1/analyses/{analysis_id}/result", headers=headers)
with urllib.request.urlopen(req_res) as r:
    res = json.loads(r.read())
    print("\n[SUCCES 2/3] Resultats d'evaluation recuperes en production !")
    print("  Conclusion :", res.get("conclusion_level"))
    print("  Synthese   :", res.get("summary_fr"))
    print("  Preuves    :", len(res.get("evidences", [])))

print("\n[SUCCES 3/3] La plateforme Forensic Media est 100% operationnelle en ligne !")
