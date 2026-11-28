# ADR 0009 — Authentification Clerk, rôle admin, session et connexions Neon

- **Statut** : accepté (valeurs par défaut choisies en autonomie, partie 1 ; à confirmer)
- **Date** : 2026-11-28
- **Contexte** : le front (Clerk) et le backend (FastAPI) sont séparés. Le backend ne doit faire confiance qu'à ce qu'il vérifie lui-même. Il faut aussi décider où vit le rôle admin, la durée de session, et comment se connecter à Neon (serverless).
- **Options** :
  - *Vérification du jeton* : (a) SDK Clerk pour Python ; (b) PyJWT + clés publiques (JWKS) de Clerk ; (c) appeler l'API Clerk à chaque requête. → (b) : standard (JWT RS256), pas de dépendance spécifique, pas d'appel réseau par requête (clés mises en cache 1 h).
  - *Rôle admin* : (a) `public_metadata.role = "admin"` exposé dans le jeton par un « session token claim » ; (b) organisations/rôles Clerk ; (c) liste d'admins en base. → (a) : une ligne dans le tableau de bord Clerk, modifiable seulement par nous (pas par l'utilisateur), vérifiée côté serveur à chaque requête. Limite : un changement de rôle met jusqu'à ~60 s à apparaître (durée de vie du jeton).
  - *Session* : durées par défaut de Clerk (jeton court ≈ 60 s renouvelé automatiquement, session longue configurable dans Clerk). Pas de réglage spécifique en partie 1.
  - *Connexions Neon* : adresse « poolée » (PgBouncer) pour l'application, adresse « directe » pour Alembic ; requêtes préparées désactivées (`prepare_threshold=None`) car incompatibles avec PgBouncer en mode transaction ; petit pool (5 + 5) et `pool_pre_ping` car la base se met en veille.
  - *Signature du webhook* : (a) paquet `svix` ; (b) vérification HMAC écrite à la main (≈ 20 lignes, schéma Standard Webhooks). → (b) : moins de dépendances, compréhensible en entretien, testée (signature valide/falsifiée/ancienne/rotation).
- **Décision** : (b) PyJWT + JWKS, rôle dans `public_metadata`, durées Clerk par défaut, deux URL Neon, HMAC maison.
- **Conséquences** : variables `CLERK_JWT_ISSUER`, `CLERK_WEBHOOK_SECRET`, `CLERK_SECRET_KEY`, `DATABASE_URL`, `DATABASE_URL_DIRECT` obligatoires hors tests. Un seul algorithme accepté (RS256) ; `azp` contrôlé contre `API_ALLOWED_ORIGINS`. La suppression de compte efface nos données **puis** le compte Clerk ; si Clerk échoue, les données sont déjà effacées et la demande est rejouable (idempotente).
- **À vérifier** (avec de vraies clés, `scripts/smoke_test.py`) : format exact du claim personnalisé dans le tableau de bord Clerk ; `DELETE /v1/users/{id}` et le comportement 404 ; événements `user.created` / `user.deleted` du webhook ; que le jeton de session porte bien `azp`.
