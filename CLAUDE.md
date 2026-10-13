# CLAUDE.md

Guidance pour Claude Code dans ce dépôt.

## Ce que c'est

Deux pages HTML statiques (Leaflet, pas de framework, pas de build) pour un voyage en Bourgogne :

- `index.html` : menu d'accueil (deux cartes, sur le modèle de `islande/index.html`) ; séjour du 17 au 19 octobre 2026.
- `preparation.html` : préparation du voyage (route des vins, fiches des domaines, carte des régions viticoles).
- `voyage.html` : carte du voyage, plein écran, avec menu de filtres sur le modèle de `islande/preparation.html` (couleurs lie-de-vin et or de `index.html`).

## Dépôt PUBLIC : règles

- Jamais de clé API, jeton, mot de passe ou identifiant dans un fichier ni dans un message de commit (les identifiants de `/home/cyg/claude/CLAUDE.md` ne vont jamais ici).
- Pas de données personnelles non voulues (adresses privées, dates précises de présence ; les dates 17-19 octobre sont publiées à la demande de l'utilisateur) sans accord explicite de l'utilisateur. `voyage.html` contient l'adresse du logement, publiée à la demande de l'utilisateur.
- Messages de commit sans ligne `Co-Authored-By` (règle globale de l'utilisateur).

## `voyage.html`

- Les lieux sont dans le tableau `LIEUX` (`cat`, `name`, `addr`, `ll` = `[lat, lon]`), les catégories dans `CATS` (libellé, émoji, couleur). Ajouter un lieu = une ligne ; une nouvelle catégorie = une entrée dans `CATS`, une couche dans `layers`/`layerState` et un bouton `btn-<nom>` dans le menu.
- Ordre de passage des vignobles : champs optionnels `ordre`, `jour`, `heure` dans `LIEUX` (séjour : samedi 17, dimanche 18, lundi 19 octobre 2026). `ordre` s'affiche en pastille dorée sur l'icône et `jour · heure` dans la popup (« Étape n sur N »). Pour changer l'ordre, modifier ces champs.
- Les contours des régions sont non interactifs (`interactive:false`) : pas de clic, pas de cadre de focus, pas d'infobulle. Les couleurs distinguent Nuits / Beaune / Chalonnaise (`REGION_COLORS`).
- Filtres : vignobles, maison et régions affichés par défaut ; restaurants et visites masqués (`DEFAULT_ON`).
- Mise en page : pas de bandeau d'en-tête ; la carte (`#wrap`) est en `position:fixed` plein viewport (évite la bande vide de `100vh`/`100dvh` sur Safari), recadrée par `refit()` au chargement, à la rotation et au redimensionnement. Retour au menu via le bouton flottant `#back`.
- Popups : lien « Voir sur Google Maps » en mode recherche de lieu (`maps/search/?api=1&query=`), volontairement pas en mode itinéraire.
- Coordonnées géocodées avec Nominatim (OpenStreetMap), précision de la rue. « Leclerc » = supermarché E.Leclerc, avenue du Bataillon de la Garde (à confirmer avec l'utilisateur).
- `COMMUNES_DATA` (contours des régions) est dupliqué depuis `preparation.html` : en cas de correction, la reporter dans les deux pages. Source : aires AOC de l'INAO (data.gouv.fr) croisées avec les contours communaux IGN/INSEE (`gregoiredavid/france-geojson`).

## Commandes

- Identité git (globale sur la machine de l'utilisateur) : `cyg2030`. Les commits publics exposent donc l'e-mail configuré.
- Test local : `python3 -m http.server 8000`, puis `http://localhost:8000/voyage.html`.
- Déploiement : `git push origin main` (GitHub Pages sert la racine de `main`).
- Pas de tests automatisés : vérifier dans un navigateur (ou Chromium headless) que les filtres ajoutent/retirent bien les couches.
