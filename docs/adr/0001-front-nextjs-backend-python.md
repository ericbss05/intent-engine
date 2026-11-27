# ADR 0001 — Front Next.js + backend Python (FastAPI)

- **Statut** : accepté (27 nov. 2026)
- **Contexte** : le projet est surtout du traitement de texte et de données (CV, anonymisation, scoring, scraping). Les meilleurs outils (Presidio, spaCy, extraction PDF) sont en Python. L'utilisateur veut un backend Python pour son CV.
- **Options** : (1) tout TypeScript + petit service Python ; (2) front Next.js + backend Python complet ; (3) tout TypeScript.
- **Décision** : option 2.
- **Conséquences** : deux langages, deux déploiements (+≈ 4 jours), authentification entre front et backend (jeton Clerk vérifié côté backend), CORS, deux CI. Pydantic remplace Zod côté backend ; SQLAlchemy + Alembic remplacent Drizzle. Backend hébergé en UE.
- **À vérifier** : SDK Python d'Inngest ; hébergeur UE du backend (partie 0).
