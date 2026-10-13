# CLAUDE.md

Guidance pour Claude Code dans ce dépôt.

## Ce que c'est

Deux pages HTML statiques (Leaflet, pas de framework, pas de build) pour un voyage en Bourgogne :

- `index.html` : préparation du voyage (route des vins, fiches des domaines, carte des régions viticoles).
- `voyage.html` : carte du voyage, plein écran, avec menu de filtres sur le modèle de `islande/preparation.html` (couleurs lie-de-vin et or de `index.html`).

## Dépôt PUBLIC : règles

- Jamais de clé API, jeton, mot de passe ou identifiant dans un fichier ni dans un message de commit (les identifiants de `/home/cyg/claude/CLAUDE.md` ne vont jamais ici).
- Pas de données personnelles non voulues (adresses privées, dates précises de présence) sans accord explicite de l'utilisateur. `voyage.html` contient l'adresse du logement, publiée à la demande de l'utilisateur.
- Messages de commit sans ligne `Co-Authored-By` (règle globale de l'utilisateur).

## `voyage.html`

- Les lieux sont dans le tableau `LIEUX` (`cat`, `name`, `addr`, `ll` = `[lat, lon]`), les catégories dans `CATS` (libellé, émoji, couleur). Ajouter un lieu = une ligne ; une nouvelle catégorie = une entrée dans `CATS`, une couche dans `layers`/`layerState` et un bouton `btn-<nom>` dans le menu.
- Filtres : vignobles, maison et régions affichés par défaut ; restaurants et visites masqués (`DEFAULT_ON`).
- Coordonnées géocodées avec Nominatim (OpenStreetMap), précision de la rue. « Leclerc » = supermarché E.Leclerc, avenue du Bataillon de la Garde (à confirmer avec l'utilisateur).
- `COMMUNES_DATA` (contours des régions) est dupliqué depuis `index.html` : en cas de correction, la reporter dans les deux pages. Source : aires AOC de l'INAO (data.gouv.fr) croisées avec les contours communaux IGN/INSEE (`gregoiredavid/france-geojson`).

## Commandes

- Test local : `python3 -m http.server 8000`, puis `http://localhost:8000/voyage.html`.
- Déploiement : `git push origin main` (GitHub Pages sert la racine de `main`).
- Pas de tests automatisés : vérifier dans un navigateur (ou Chromium headless) que les filtres ajoutent/retirent bien les couches.
