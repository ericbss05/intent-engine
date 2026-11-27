# 02 — Stack, structure et conventions

## Stack

| Couche | Choix | Remarque |
|---|---|---|
| Front | Next.js (App Router) + TypeScript strict + Tailwind + shadcn/ui, pnpm | Pages/formulaires ; dernière version stable à l'installation |
| Validation front | Zod + React Hook Form | Formulaires |
| Backend | Python 3.12 + FastAPI + Pydantic v2 | Tout le métier |
| ORM / migrations | SQLAlchemy 2 + Alembic | Migrations versionnées obligatoires |
| Dépendances Python | uv | Lockfile commité |
| Style / types Python | ruff (+ mypy ou pyright, à choisir en partie 0) | |
| Tests | pytest (backend), Vitest (front) | |
| Base | PostgreSQL chez Neon, région **Frankfurt** | Pool de connexions adapté au serverless |
| Auth | Clerk | Backend vérifie le jeton ; rôle admin |
| Tâches | Inngest (SDK Python : **à vérifier**) | Retries, planification, concurrence, annulation |
| Temps réel | SSE + `run_events` | |
| Anonymisation | Presidio + spaCy (modèle français) | Module du backend |
| Conteneur | Docker | Déploiement du backend en UE |
| CI | GitHub Actions | Lint + tests des deux apps |
| Hébergement | Front : Vercel ; Backend : hébergeur UE (Scaleway, OVHcloud, Render EU ou Fly Paris : à comparer en partie 0) | Documenter en ADR |
| Surveillance | Sentry (optionnel) | Sans données personnelles |

## Structure du dépôt

```
/
├─ CLAUDE.md
├─ apps/
│  ├─ web/                      # Next.js
│  │  ├─ src/app/               # pages (App Router)
│  │  ├─ src/components/
│  │  ├─ src/lib/               # client API, Zod schemas
│  │  └─ tests/
│  └─ api/                      # FastAPI
│     ├─ app/
│     │  ├─ main.py
│     │  ├─ core/               # config, sécurité (jeton Clerk), logging, db
│     │  ├─ domain/             # modèles SQLAlchemy + schémas Pydantic
│     │  ├─ interfaces/         # ports (Protocol) : voir 06-interfaces-contrats.md
│     │  ├─ adapters/           # un dossier par fournisseur (sirene, brightdata, firecrawl, hunter, apollo, zerobounce, reoon, llm, anonymizer, cv)
│     │  ├─ services/           # scoring, pipeline, matching, quotas, purge
│     │  ├─ workflows/          # fonctions Inngest
│     │  └─ routers/            # routes HTTP (minces)
│     ├─ alembic/
│     └─ tests/
├─ data/
│  ├─ skills_dictionary.json    # dictionnaire de compétences + synonymes (versionné)
│  ├─ naf_mapping.json          # secteur affiché -> codes NAF (relu à la main)
│  └─ eval/                     # jeux d'évaluation synthétiques (voir 07)
├─ docs/                        # ce pack + rapports + ADR
├─ templates/
├─ .claude/commands/
└─ .github/workflows/
```

## Conventions

- **Nommage** : anglais ; Python en `snake_case`, classes en `PascalCase` ; TypeScript en `camelCase`, composants en `PascalCase` ; tables en `snake_case` pluriel.
- **Interfaces** : un `Protocol` Python par port, un adaptateur par fournisseur, enregistrés dans une configuration (ordre et activation modifiables depuis `admin_config`).
- **Configuration** : variables d'environnement validées au démarrage (Pydantic Settings / Zod) ; jamais de valeur secrète en dur ; quotas et budgets **en base** (`admin_config`), pas en code.
- **Erreurs HTTP** : codes standards, corps `{code, message}` sans donnée personnelle.
- **Réponses de fournisseurs** : toujours validées par un schéma ; enregistrer des **fixtures** de réponses pour les tests.
- **Idempotence** : toute tâche d'enrichissement a une clé `(siren, step)` ; relancer ne duplique rien.
- **Dates** : UTC en base, ISO 8601 dans les API.
- **Commits** : Conventional Commits en anglais.
- **Docs** : français ; ADR numérotés `docs/adr/NNNN-titre.md`.
- **Variables d'environnement** : liste dans `templates/.env.example` (noms seulement).
