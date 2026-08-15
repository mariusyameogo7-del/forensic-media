import urllib.request
import json
from pathlib import Path

# Load test image
img_path = Path("temp_uploads/samples/photo_manifestation_ouaga.jpg")
with open(img_path, "rb") as f:
    img_data = f.read()

boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
header_bytes = (
    f"--{boundary}\r\n"
    f"Content-Disposition: form-data; name=\"file\"; filename=\"photo_manifestation_ouaga.jpg\"\r\n"
    f"Content-Type: image/jpeg\r\n\r\n"
).encode("utf-8")
footer_bytes = f"\r\n--{boundary}--\r\n".encode("utf-8")
body = header_bytes + img_data + footer_bytes

# 1. Post analysis
req = urllib.request.Request(
    "http://127.0.0.1:8000/api/v1/analyses",
    data=body,
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
)
res = urllib.request.urlopen(req)
data = json.loads(res.read().decode())
print("[OK] Created Analysis:", data["public_id"], "ID:", data["analysis_id"])

# 2. Check Progress endpoint
prog_req = urllib.request.Request(
    f"http://127.0.0.1:8000/api/v1/analyses/{data['analysis_id']}/progress",
    headers={"X-Analysis-Token": data["access_token"]}
)
prog_res = urllib.request.urlopen(prog_req)
prog_data = json.loads(prog_res.read().decode())
print("[OK] Progress Status:", prog_data["status"], "Progress Percent:", prog_data["progress_percent"])

# 3. Check Result endpoint
res_req = urllib.request.Request(
    f"http://127.0.0.1:8000/api/v1/analyses/{data['analysis_id']}/result",
    headers={"X-Analysis-Token": data["access_token"]}
)
res_res = urllib.request.urlopen(res_req)
res_data = json.loads(res_res.read().decode())
print("[OK] Result Conclusion:", res_data["conclusion_level"])
print("     Provenance:", res_data["provenance_status"])
print("     Integrity:", res_data["integrity_status"])
print("     AI status:", res_data["ai_status"])
print("     Context:", res_data["context_status"])
print("     Evidences count:", len(res_data["evidences"]))
print("     Summary:", res_data["summary_fr"])
