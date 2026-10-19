#!/bin/bash
# Régénère voyage.html depuis l'album Immich. Nécessite le dépôt privé `voyages` à côté (../../voyages)
# et la clé du lien de partage dans SHARE_KEY. Usage : SHARE_KEY=... outils/regenerer.sh
set -e
ICI="$(cd "$(dirname "$0")" && pwd)"; V="$ICI/../../voyages"; T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT
cp "$ICI/footing-dimanche.json" "$T/footing.json"
echo '[{"lat":47.0367,"lon":4.8432,"name":"Logement – Beaune"}]' > "$T/poi.json"
python3 "$ICI/recuperer_photos.py" "$T/photos.json"
python3 "$ICI/corriger_photos.py" "$T"
python3 "$V/scripts/cluster_stops.py" "$T/photos.json" --out "$T/clustered.json" --min-photos-major 3 --min-duration-major-min 0 --merge-gap-min 90
python3 "$ICI/retouche.py" "$T"
python3 "$V/scripts/osrm_match.py" "$T/clustered2.json" --out "$T/matched.json"
python3 "$V/scripts/build_page.py" "$T/matched.json" --slug bourgogne2026 --title Bourgogne --subtitle "Route des vins" --emoji 🍷 \
  --album-id 3d752d3e-17f7-40b5-ac3f-0408a26a8884 --edit-mode off --immich-base-url https://photo.itcg-consulting.com:5010 \
  --poi-json "$T/poi.json" --out-dir "$T/out" || true   # l'étape d'index de `voyages` échoue ici : sans importance
python3 "$ICI/assembler.py" "$T"   # écrit ../voyage.html
