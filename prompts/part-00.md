# Partie 0 — Fondations du dépôt, front + backend (≈ 5 j)

## Contexte
Dépôt vide. Monorepo : `apps/web` (Next.js) et `apps/api` (FastAPI). Lis `CLAUDE.md`, `docs/02-stack-et-conventions.md`, `docs/adr/0001`. L'utilisateur est débutant-intermédiaire : explique les outils au premier usage.

## Tâche
1. Initialiser le monorepo et la structure de `docs/02`.
2. `apps/web` : Next.js (App Router) + TypeScript `strict`, Tailwind, shadcn/ui, pnpm, ESLint/Prettier, Vitest ; une page d'accueil qui affiche l'état du backend (appel au point de santé).
3. `apps/api` : Python 3.12, FastAPI, uv, ruff, (mypy ou pyright : proposer et justifier), pytest ; routes `GET /health` ; configuration par variables d'environnement validées (Pydantic Settings) ; logging structuré **sans données personnelles**.
4. CORS limité à l'origine du front ; clé/jeton prévu pour la suite (pas d'auth réelle encore).
5. Dockerfile du backend ; instructions de déploiement : front sur Vercel, backend sur un hébergeur **UE** (comparer Scaleway, OVHcloud, Render EU, Fly Paris : coût, région, simplicité, RGPD ; proposer, **ne pas trancher seul**).
6. CI GitHub Actions à partir de `templates/ci.yml` (lint + types + tests des deux apps) ; scan de secrets GitHub activé (indiquer la procédure).
7. `.gitignore` strict (`.env`, données, CV), `templates/.env.example` copié et complété, `docs/adr/` avec l'ADR de l'hébergeur.
8. README racine : comment lancer en local, tester, déployer.

## Contraintes
- Aucun secret dans le dépôt. Aucune donnée personnelle.
- Versions : dernières stables à l'installation, figées par lockfile (`pnpm-lock.yaml`, `uv.lock`).
- Pas de fonctionnalité métier (c'est la partie 1 et suivantes).

## Sorties attendues
`apps/web/`, `apps/api/`, `.github/workflows/ci.yml`, `docker`, `README.md`, `docs/adr/0008-hebergeur-backend.md`, `docs/reports/part-00.md`.

## Critères de terminé
- [ ] Un push sur `main` (ou une PR) lance lint + types + tests des deux apps, verts.
- [ ] Le front déployé appelle `/health` du backend déployé (en UE) et affiche « OK ».
- [ ] README permet à un tiers de lancer le projet en local en moins de 15 minutes.

## Questions à poser avant de coder
Nom du projet/dépôt ; hébergeur UE préféré ; plan Vercel (usage non commercial ?) ; mypy ou pyright ; gestionnaire de secrets.

## Hors périmètre
Auth Clerk, base de données, toute logique métier.
