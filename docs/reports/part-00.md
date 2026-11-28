# Rapport — Partie 0 : Fondations du dépôt, front + backend

## Résumé
Monorepo `apps/web` (Next.js) + `apps/api` (FastAPI), CI, Dockerfile, README, ADR hébergeur. Lint, types et tests des deux apps sont verts, y compris depuis un clone propre avec lockfiles gelés. Le front local affiche « OK » après avoir appelé `/health` du backend local. **Rien n'est déployé** (mode autonome : préparation seulement). Mode autonome demandé par l'utilisateur ; aucune question posée.

## Ce qui est fait
- `apps/api` : Python 3.12, FastAPI, `GET /health`, config Pydantic Settings validée, CORS restreint, logs JSON à liste blanche de champs, ruff, mypy strict, pytest (8 tests), `uv.lock`, `Dockerfile` (non-root, `/docs` coupé en production).
- `apps/web` : Next.js 16 (App Router), TypeScript strict, Tailwind 4, shadcn/ui, ESLint + Prettier, Vitest (8 tests), Zod (variable d'environnement et réponse de `/health`), `pnpm-lock.yaml`.
- `.github/workflows/ci.yml` (web, api, build Docker), `.gitignore` strict, `.env.example`, `README.md` racine, `docs/adr/0008-hebergeur-backend.md` (statut **proposé**).
- Branche `part-00-fondations`, commits Conventional Commits. Rien poussé.

## Décisions et pourquoi
| Décision | Alternatives | Raison |
|---|---|---|
| Nom « stage-finder » (provisoire) | — | Imposé par le prompt ; facile à renommer |
| mypy (strict) | pyright | Imposé ; intégré à `pydantic.mypy`, s'installe via uv |
| Scaleway proposé (ADR 0008) | Render, Fly Paris | Société et région UE, coût probablement nul ; **non tranché** |
| Appel `/health` depuis le navigateur | Appel côté serveur Next | Vérifie aussi le CORS réel |
| `app/` à la racine de `apps/api`, `package = false` | Layout `src/` d'`uv init` | Conforme à `docs/02` ; c'est une application, pas une librairie |
| CI sans service PostgreSQL | Garder celui du template | Pas de base en partie 0 ; ajout en partie 1 |
| `.env.example` à la racine (copie complétée du template) | — | Demandé par la tâche 7 |
| `/docs` FastAPI désactivé en production | Toujours actif | Réduit la surface exposée |

## Comment tester à la main
1. `cd apps/api && uv sync && uv run uvicorn app.main:app --port 8000` puis `curl localhost:8000/health`.
2. `cd apps/web && pnpm install`, créer `.env.local` avec `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`, `pnpm dev`, ouvrir http://localhost:3000 : « OK ». Arrêter l'API : « Service indisponible ».
3. `docker build -t stage-finder-api apps/api`, puis `docker run -p 8081:8080 stage-finder-api` et `curl localhost:8081/health`.

## Tests automatiques
- API : `/health`, CORS (origine autorisée / refusée), refus de `*`, niveau de log invalide, logs sans champ personnel. Résultat local : ruff, format, mypy, pytest 8/8.
- Web : `fetchBackendState` (4 cas), `parseEnv`, composant `BackendStatus`. Résultat : eslint + prettier, tsc, vitest 8/8, `next build`.
- Preuves : exécution depuis un clone propre ; Chrome headless a lu `data-status="ok"` ; image Docker testée (`/health` OK, `/docs` = 404, utilisateur `appuser`).
- **CI GitHub non exécutée à ce stade** (correction : un remote `origin` existe) ; elle reprend les mêmes commandes.

## Règles RGPD / sécurité touchées
- §6.5 logs sans donnée personnelle : liste blanche de champs + test ; chemin sans query string.
- §7 aucun secret dans le dépôt (scan par motifs : rien), variables validées au démarrage, CORS sans `*`, conteneur non-root.
- Aucune donnée personnelle, aucun CV, aucune fonctionnalité métier.

## Limites connues et risques
- **Déploiement non fait** : le critère « front déployé appelle le backend déployé en UE » reste à réaliser (voir liste ci-dessous).
- ADR 0008 : tarifs et régions issus de recherches web, non vérifiés dans les consoles ; région UE de Render et prix Fly `cdg` non confirmés.
- **Clé/jeton d'API prévu pour la suite** : seulement la structure (en-tête `Authorization` autorisé par le CORS) ; pas d'auth.
- Incidents d'outillage : `create-next-app` et `shadcn` échouaient (`ENOEXEC` en lançant `pnpm`) ; contourné par un wrapper temporaire hors dépôt. `shadcn` avait ajouté `cn` comme dépendance directe : **retirée** de `package.json`, et `cn()` réécrit avec `clsx` + `tailwind-merge`. *Correction (2026-11-28)* : `cn@0.2.6` reste dans `pnpm-lock.yaml` comme dépendance **transitive** de la CLI `shadcn@4.23.1` ; il est publié par le mainteneur de shadcn (dépôt `shadcn-ui/cn`), donc ce n'est pas un paquet inconnu, contrairement à ce que j'avais écrit.
- `httpx2` (suggéré par un avertissement de dépréciation de Starlette) : l'ajout a été **refusé par le garde-fou de l'environnement**, donc non ajouté ; 1 avertissement subsiste dans pytest. Aucun impact fonctionnel.
- Le dépôt n'était pas un dépôt git : `git init`, le pack importé sur `main` en un commit local, puis branche de travail.
- Python système 3.14 sans importance : uv utilise 3.12.

## À faire à la main
1. Créer le dépôt GitHub, ajouter le remote, pousser la branche, ouvrir une PR (vérifier la CI).
2. Activer Secret scanning + Push protection (Settings → Code security).
3. Valider/changer l'hébergeur (ADR 0008), créer le compte, pousser l'image, définir `APP_ENV`, `API_ALLOWED_ORIGINS`, `LOG_LEVEL`, région UE.
4. Compte Vercel (Root Directory `apps/web`, `NEXT_PUBLIC_API_BASE_URL`) ; vérifier que l'offre gratuite couvre l'usage non commercial.
5. Gestionnaire de secrets : variables d'environnement de la plateforme pour l'instant.

## Idées hors périmètre (non faites)
Déploiement automatique après CI ; clé d'API entre front et backend ; Sentry ; dépendabot.

## À savoir expliquer en entretien
1. **Monorepo** : un dépôt, deux apps indépendantes, une CI par app.
2. **Validation aux frontières** : Pydantic Settings au démarrage côté API, Zod côté front ; une réponse invalide donne « indisponible », pas un crash.
3. **CORS** : le navigateur refuse de lire une réponse d'une autre origine sauf autorisation ; liste explicite, jamais `*` ; ce n'est pas une authentification.
4. **Logs RGPD** : liste blanche de champs plutôt que liste noire.
5. **Lockfiles** (`uv.lock`, `pnpm-lock.yaml`) + `--frozen` : builds reproductibles.
6. **Docker** : couche de dépendances séparée (cache), utilisateur non-root, port via `$PORT`.
7. **Choix de l'hébergeur** : critères (juridiction, coût, simplicité), et honnêteté sur ce qui n'est pas vérifié.
8. **Chaîne d'approvisionnement** : un outil peut ajouter des dépendances sans te le dire ; on relit `package.json`, on vérifie l'origine (`pnpm why`, `npm view`) et on lance `pnpm audit` / `uv audit` (aucune alerte au 2026-11-28).

## Validation attendue
Relire l'ADR 0008 (choix de l'hébergeur), tester le lancement local, puis valider avant la partie 1.
