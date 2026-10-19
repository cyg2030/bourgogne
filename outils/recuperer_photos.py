"""Récupère les photos géolocalisées de l'album Immich via son lien de partage public.
Usage : SHARE_KEY=<clé du lien de partage> python3 recuperer_photos.py photos.json
Les heures sont celles de localDateTime (heure locale, malgré le Z)."""
import os, sys, json, requests
B = "https://photo.itcg-consulting.com:5010"
A = "3d752d3e-17f7-40b5-ac3f-0408a26a8884"
k = os.environ["SHARE_KEY"]
items, page = [], 1
while True:
    r = requests.post(B + "/api/search/metadata", params={"key": k},
                      json={"albumIds": [A], "withExif": True, "page": page, "size": 1000}, timeout=60)
    r.raise_for_status()
    d = r.json()["assets"]
    items += d["items"]
    if not d.get("nextPage"):
        break
    page = int(d["nextPage"])
out = []
for it in items:
    e = it.get("exifInfo") or {}
    if e.get("latitude") is None:
        continue
    out.append({"id": it["id"], "dt": it.get("localDateTime") or e.get("dateTimeOriginal"),
                "lat": e["latitude"], "lon": e["longitude"], "model": e.get("model"), "city": e.get("city")})
out.sort(key=lambda p: p["dt"])
json.dump(out, open(sys.argv[1], "w"), ensure_ascii=False)
print(len(out), "photos géolocalisées sur", len(items))
