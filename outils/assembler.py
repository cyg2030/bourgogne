import re, json, math, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
S = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else str(HERE.parent / "voyage.html")
t = open(S + "/out/bourgogne2026/voyage.html").read()
def get(n): return json.loads(re.search(r"^const %s = (.*);$" % n, t, re.M).group(1))
DAYS, STOPS, MINOR = get("DAYS"), get("STOPS"), get("STOPS_MINOR")
src = (HERE / "voyage-base.html").read_text(encoding="utf-8")
# lieux connus pour nommer les arrêts
lieux = re.findall(r"name:'((?:[^'\\]|\\.)*)'.*?ll:\[([\d.]+),([\d.]+)\]", src)
def km(a, b, c, d):
    p = math.pi / 180
    x = (math.sin((c - a) * p / 2)) ** 2 + math.cos(a * p) * math.cos(c * p) * math.sin((d - b) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(x))
def nom(s):
    best = min(((km(s["lat"], s["lon"], float(la), float(lo)), n) for n, la, lo in lieux), default=(9, ""))
    if best[0] <= 0.35: return ("Logement" if best[1]=="Notre maison" else best[1]).replace("\\'", "'")
    return s["name"]
dl = {d["date"]: d["dateLabel"] for d in DAYS}
stops = []
for s in STOPS + MINOR:
    nm = "Basilique de Beaune" if s["date"] == "2026-10-18" and "13:00" <= s["timeRange"] < "15:00" and nom(s) == "Hospices de Beaune" else None
    nm = nm or ("Footing du matin" if s["date"] == "2026-10-18" and s["timeRange"] < "10:30" else nom(s))
    stops.append({"date": s["date"], "lat": s["lat"], "lon": s["lon"], "name": nm, "major": s in STOPS,
                  "range": s["timeRange"], "photos": s["photos"]})
for d in DAYS:  # photos du soir au logement
    if d["night"]["photos"]:
        p = d["night"]["photos"]
        stops.append({"date": d["date"], "lat": d["night"]["lat"], "lon": d["night"]["lon"], "name": "Soirée au logement",
                      "major": True, "range": p[0][1] + "-" + p[-1][1], "photos": p})
JOURS = ["dim.", "lun.", "mar.", "mer.", "jeu.", "ven.", "sam."]
import datetime
def lib(date, h): return JOURS[(datetime.date.fromisoformat(date).weekday() + 1) % 7] + " " + h
lp = {}
for n_, la, lo in lieux:
    n_ = n_.replace("\\'", "'")
    if n_ == "Notre maison": continue
    ph = []
    for s in stops:
        if s["name"] not in ("Soirée au logement", "Basilique de Beaune") and km(s["lat"], s["lon"], float(la), float(lo)) <= 0.35:
            ph += [[i, lib(s["date"], h), s["date"] + h] for i, h in s["photos"]]
    ph.sort(key=lambda x: x[2])
    if ph: lp[n_] = [[i, h] for i, h, _ in ph]
trace = [{"date": d["date"], "label": d["dateLabel"], "segments": [{"t": s["type"], "c": s["coords"]} for s in d["segments"]]} for d in DAYS]
data = "const TRACE = %s;\nconst STOPS = %s;\nconst IMMICH = \"https://photo.itcg-consulting.com:5010\";\nconst SHARE_KEY = \"%s\";\nconst LIEU_PHOTOS = %s;\n" % (
    json.dumps(trace, separators=(",", ":")), json.dumps(stops, ensure_ascii=False, separators=(",", ":")), __import__('os').environ['SHARE_KEY'], json.dumps(lp, ensure_ascii=False, separators=(",", ":")))

css = """.photo-wrap { position:relative; width:220px; margin-bottom:6px; background:#eee; border-radius:6px; overflow:hidden; }
.photo-wrap img { display:block; width:100%; height:auto; }
.photo-badge { position:absolute; left:6px; bottom:6px; background:rgba(0,0,0,.6); color:#fff; font-size:11px; padding:1px 6px; border-radius:8px; }
.photo-nav { position:absolute; top:50%; transform:translateY(-50%); width:30px; height:40px; border:none; background:rgba(0,0,0,.45); color:#fff; font-size:22px; cursor:pointer; }
.photo-nav.prev { left:0; border-radius:0 6px 6px 0; } .photo-nav.next { right:0; border-radius:6px 0 0 6px; }
.liens { display:flex; align-items:center; gap:12px; margin-top:8px; }
.liens a { display:inline-flex; line-height:0; }
.liens img, .liens svg { width:28px; height:28px; }
.dot { display:inline-flex; align-items:center; justify-content:center; width:20px; height:20px; border-radius:50%; color:#fff; font:700 11px Arial; }
.pin-photo { display:flex; align-items:center; justify-content:center; border-radius:50%; background:#fff; box-shadow:0 2px 6px rgba(0,0,0,.45); font-size:11px; }
"""
js = """
// ── TRACÉ RÉEL ET PHOTOS (reconstruits depuis l'album Immich ; voir TRACE / STOPS) ──
%s
const DAY_COLORS = ['#1f78b4', '#e07b00', '#2a9d8f'];
const dayIdx = d => TRACE.findIndex(x => x.date === d);
const dayLabel = d => (TRACE[dayIdx(d)] || {}).label || d;
// un groupe par jour et par type (tracé / arrêts / petits arrêts), affiché si le jour ET le type sont cochés
const TL = TRACE.map(() => ({ trace:L.layerGroup(), photos:L.layerGroup(), petits:L.layerGroup() }));
const dayOn = TRACE.map(() => true), typeOn = { photos:true, petits:false };
TRACE.forEach((d, i) => d.segments.forEach(s => {
  L.polyline(s.c, { color:DAY_COLORS[i %% DAY_COLORS.length], weight:s.t === 'foot' ? 3 : 4, opacity:.85, dashArray:s.t === 'foot' ? '2 7' : null, interactive:false }).addTo(TL[i].trace);
}));
const PHOTO_SETS = {};
const thumbUrl = id => `${IMMICH}/api/assets/${id}/thumbnail?size=preview&key=${SHARE_KEY}`;
const ALBUM_URL = `${IMMICH}/share/${SHARE_KEY}`;
function navPhoto(k, dir){
  const ps = PHOTO_SETS[k]; ps.idx = (ps.idx + dir + ps.photos.length) %% ps.photos.length;
  const [id, h] = ps.photos[ps.idx];
  const img = document.getElementById('img-' + k); img.parentElement.style.display = ''; img.src = thumbUrl(id);
  document.getElementById('badge-' + k).textContent = `${h} · ${ps.idx + 1}/${ps.photos.length}`;
  }
const lienGM = url => `<a href="${url}" target="_blank" rel="noopener" title="Voir sur Google Maps" aria-label="Voir sur Google Maps"><svg viewBox="0 0 24 34" aria-hidden="true"><path d="M12 0C5.4 0 0 5.3 0 11.8 0 20.6 12 34 12 34s12-13.4 12-22.2C24 5.3 18.6 0 12 0z" fill="#ea4335"/><path d="M12 0C8.5 0 5.4 1.5 3.3 3.9L12 14.5z" fill="#4285f4"/><path d="M3.3 3.9C1.2 6 0 8.800 0 11.8c0 2.300.8 4.700 2 7L12 14.5z" fill="#fbbc04"/><circle cx="12" cy="11.8" r="4.300" fill="#fff"/></svg></a>`;
const lienIM = () => `<a href="${ALBUM_URL}" target="_blank" rel="noopener" title="Voir l'album sur Immich" aria-label="Voir l'album sur Immich"><img alt="Immich" src="data:image/png;base64,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"></a>`;
function lieuPhotos(l){
  const ph = LIEU_PHOTOS[l.name]; if (!ph) return '';
  const k = 'l' + LIEUX.indexOf(l); PHOTO_SETS[k] = { photos:ph, idx:0 };
  const n = ph.length;
  const nav = n > 1 ? `<button class="photo-nav prev" onclick="navPhoto('${k}',-1)">‹</button><button class="photo-nav next" onclick="navPhoto('${k}',1)">›</button>` : '';
  return `<div class="photo-wrap"><img id="img-${k}" src="${thumbUrl(ph[0][0])}" onerror="this.parentElement.style.display='none'"><div class="photo-badge" id="badge-${k}">${ph[0][1]}${n > 1 ? ` · 1/${n}` : ''}</div>${nav}</div>`;
}
STOPS.forEach((s, i) => {
  const k = 's' + i, ci = dayIdx(s.date), col = DAY_COLORS[ci %% DAY_COLORS.length], sz = s.major ? 22 : 14;
  PHOTO_SETS[k] = { photos:s.photos, idx:0 };
  const icon = L.divIcon({ className:'', iconSize:[sz, sz], iconAnchor:[sz/2, sz/2], popupAnchor:[0, -sz/2],
    html:s.major ? `<div class="pin-photo" style="width:22px;height:22px;border:3px solid ${col}">📸</div>` : `<div class="pin-photo" style="width:14px;height:14px;border:2px solid ${col}"></div>` });
  L.marker([s.lat, s.lon], { icon, title:s.name }).bindPopup(() => {
    const ps = PHOTO_SETS[k]; ps.idx = 0; const n = ps.photos.length;
    const nav = n > 1 ? `<button class="photo-nav prev" onclick="navPhoto('${k}',-1)">‹</button><button class="photo-nav next" onclick="navPhoto('${k}',1)">›</button>` : '';
    return `<div class="photo-wrap"><img id="img-${k}" src="${thumbUrl(ps.photos[0][0])}" onerror="this.parentElement.style.display='none'"><div class="photo-badge" id="badge-${k}">${ps.photos[0][1]}${n > 1 ? ` · 1/${n}` : ''}</div>${nav}</div>
      <span class="popup-kind" style="background:${col}">${dayLabel(s.date)}</span>
      <div class="popup-title">${s.name}</div>
      <div class="popup-addr">${s.range} · ${n} photo${n > 1 ? 's' : ''}</div>
      <div class="liens">${lienGM(`https://www.google.com/maps/search/?api=1&query=${s.lat},${s.lon}`)}${lienIM()}</div>`;
  }, { minWidth:230 }).addTo(TL[ci][s.major ? 'photos' : 'petits']);
});
function refreshTrace(){
  TL.forEach((g, i) => ['trace','photos','petits'].forEach(t => {
    const on = dayOn[i] && (t === 'trace' || typeOn[t]);
    if (on) g[t].addTo(map); else map.removeLayer(g[t]);
  }));
  TRACE.forEach((d, i) => syncSubBtn('btn-jour' + i, dayOn[i]));
  ['photos','petits'].forEach(t => syncSubBtn('btn-t-' + t, typeOn[t]));
}
function toggleDay(i){ dayOn[i] = !dayOn[i]; refreshTrace(); }
function toggleType(t){ typeOn[t] = !typeOn[t]; refreshTrace(); }
function soloDay(i){ dayOn.fill(false); dayOn[i] = true; refreshTrace(); }
document.getElementById('menu-jours').innerHTML = TRACE.map((d, i) =>
  `<button class="sub-btn active" id="btn-jour${i}" onclick="toggleDay(${i})"><span class="icon"><span class="dot" style="background:${DAY_COLORS[i %% DAY_COLORS.length]}">${i + 1}</span></span><span class="label">J${i + 1} — ${d.label}</span><span class="check"></span></button>`).join('');
refreshTrace();
""" % data
btns = """  <div class="ctrl-group">
    <button class="grp-btn" id="grpbtn-jours" onclick="toggleGroup('jours')" aria-label="Étapes" title="Étapes">🗓️</button>
    <div class="grp-menu" id="grpmenu-jours">
      <div class="sub-label" id="jours-label">Étapes du voyage</div>
      <div id="menu-jours" style="display:flex;flex-direction:column;gap:5px"></div>
    </div>
  </div>
  <div class="ctrl-group">
    <button class="grp-btn" id="grpbtn-poi" onclick="toggleGroup('poi')" aria-label="Points d'intérêt" title="Points d'intérêt">📸</button>
    <div class="grp-menu" id="grpmenu-poi">
      <div class="sub-label">Points d'intérêt (photos)</div>
      <button class="sub-btn active" id="btn-t-photos" onclick="toggleType('photos')"><span class="icon">📸</span><span class="label" id="lbl-photos">Arrêts marquants</span><span class="check"></span></button>
      <button class="sub-btn" id="btn-t-petits" onclick="toggleType('petits')"><span class="icon">🔹</span><span class="label" id="lbl-petits">Autres arrêts, moins marquants</span><span class="check"></span></button>
    </div>
  </div>
"""
def rep(a, b, cnt=1):
    global src
    assert src.count(a) == cnt, a
    src = src.replace(a, b)
rep("</style>", css + "</style>")
rep("""    </div>\n  </div>\n</div>\n</div>\n\n<script>""", """    </div>\n  </div>\n""" + btns + """</div>\n</div>\n\n<script>""")
rep("""function toggleGroup(name){
  const open = document.getElementById('grpmenu-' + name).classList.toggle('open');""", """function toggleGroup(name){
  document.querySelectorAll('.grp-menu').forEach(m => { if (m.id !== 'grpmenu-' + name) m.classList.remove('open'); });
  document.querySelectorAll('.grp-btn').forEach(b => { if (b.id !== 'grpbtn-' + name) b.classList.remove('open'); });
  const open = document.getElementById('grpmenu-' + name).classList.toggle('open');""")
rep(".bindPopup(`<span class=\"popup-kind\" style=\"background:${c.color}\">", ".bindPopup(() => lieuPhotos(l) + `<span class=\"popup-kind\" style=\"background:${c.color}\">")
rep('<a class="popup-link" href="${gmaps}" target="_blank" rel="noopener">Voir sur Google Maps ↗</a>`)\n    .addTo(layers[l.cat]);', '<div class="liens">${lienGM(gmaps)}${LIEU_PHOTOS[l.name] ? lienIM() : ""}</div>`, { minWidth:230 })\n    .addTo(layers[l.cat]);')
rep("// ── UI ──", js + "\n// ── UI ──")
src = src.replace("<div class=\"sub-label\">Afficher</div>", "<div class=\"sub-label\">Lieux et régions</div>", 1)
open(OUT, "w", encoding="utf-8").write(src)
print(len(stops), [s["name"] for s in stops])
