# stage-finder (nom provisoire)

Service d'aide à la recherche de stage/alternance pour étudiants (France). Règles de travail : `CLAUDE.md`. Le pack de départ est décrit dans `docs/README-pack.md`.

État : **partie 0** (fondations). Seul le point `GET /health` et une page d'accueil qui affiche l'état du backend existent.

```
apps/api   Backend Python (FastAPI)       apps/web   Front Next.js (TypeScript)
```

## Prérequis (une fois)

| Outil | Rôle | Installation (macOS) |
|---|---|---|
| Node.js ≥ 20 + pnpm | front | `brew install node pnpm` |
| uv | gère Python 3.12 et les dépendances du backend | `brew install uv` |
| Docker (optionnel) | tester l'image du backend | Docker Desktop |

## Lancer en local (≈ 10 min)

```bash
# 1. Backend  (http://localhost:8000)
cd apps/api
uv sync                                   # installe Python 3.12 + dépendances (verrouillées dans uv.lock)
uv run uvicorn app.main:app --reload --port 8000
# test : curl localhost:8000/health  ->  {"status":"ok"}

# 2. Front  (http://localhost:3000), dans un autre terminal
cd apps/web
pnpm install
echo 'NEXT_PUBLIC_API_BASE_URL=http://localhost:8000' > .env.local
pnpm dev
```

Ouvre http://localhost:3000 : « État du service : **OK** ». Si le backend est arrêté : « Service indisponible ».

Variables : voir `.env.example` (noms seulement). **Depuis la partie 1**, le backend exige `DATABASE_URL` et les variables `CLERK_*` (sauf `APP_ENV=test`) et refuse de démarrer sinon. Copie `.env.example` en `apps/api/.env` et remplis-le ; le front lit `apps/web/.env.local` (`NEXT_PUBLIC_API_BASE_URL`, `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`).

Migrations de la base : `cd apps/api && uv run alembic upgrade head` (utilise `DATABASE_URL_DIRECT` s'il est défini).

Test de fumée avec tes vraies clés : voir l'en-tête de `scripts/smoke_test.py`.

## Tests et qualité

Les tests du backend ont besoin d'un PostgreSQL **jetable** (jamais une vraie base ; le nom doit finir par `_test`) :

```bash
docker run -d --name stagefinder-test-pg -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=stagefinder_test -p 5433:5432 postgres:16-alpine
```

```bash
cd apps/api && uv run ruff check . && uv run ruff format --check . && uv run mypy . && uv run pytest -q
cd apps/web && pnpm lint && pnpm typecheck && pnpm test
```

La CI (`.github/workflows/ci.yml`) lance les mêmes commandes sur chaque PR et chaque push sur `main`.

## Déployer (à faire à la main : rien n'est déployé)

**Front → Vercel**
1. Crée un compte Vercel (vérifie que l'offre gratuite « Hobby » autorise ton usage non commercial).
2. « Add New Project », importe le dépôt GitHub, **Root Directory = `apps/web`**.
3. Variable d'environnement : `NEXT_PUBLIC_API_BASE_URL` = URL publique du backend.

**Backend → hébergeur UE** (proposition : Scaleway, voir `docs/adr/0008-hebergeur-backend.md`, statut « proposé »)
1. Valide ou change l'hébergeur (ADR 0008).
2. Construis l'image : `docker build -f apps/api/Dockerfile -t stage-finder-api .` (depuis la racine du dépôt) et pousse-la dans le registre de l'hébergeur.
3. Crée le service, région **UE**, port `8080`, variables : `APP_ENV=production`, `API_ALLOWED_ORIGINS=<URL du front Vercel>`, `LOG_LEVEL=info`.
4. Teste `https://<url-backend>/health`, puis redéploie le front avec la bonne `NEXT_PUBLIC_API_BASE_URL`.

**Scan de secrets GitHub** : Settings → Code security → activer « Secret scanning » et « Push protection ».

## Sécurité

Aucun secret dans le dépôt (`.gitignore` bloque `.env*`, CV, dumps). Voir `CLAUDE.md` §6–§7.
