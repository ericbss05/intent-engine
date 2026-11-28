# Rapport — Partie 1 : Compte, base, isolation, droits

## Résumé
Comptes (Clerk), base PostgreSQL (SQLAlchemy 2 + Alembic), vérification du jeton **côté backend**, rôle admin vérifié côté serveur, couche d'accès aux données exigeant `user_id`, webhook Clerk signé, export JSON (`GET /me/export`) et suppression en cascade (`DELETE /me`), case 18+, page admin vide, pages front (connexion, inscription, onboarding 18+, compte, admin). Lint, types et tests verts en local (API : 59 tests passés + 1 ignoré ; front : 22 tests ; `next build` OK ; image Docker construite). **Rien n'a été testé contre un vrai Clerk ni un vrai Neon** (pas de clés) : voir « À faire à la main ». Mode autonome : aucune question posée, choix listés ci-dessous.

## Ce qui est fait
- **Backend** (`apps/api`) : `core/config` (variables obligatoires hors test), `core/db` (pool Neon), `core/security` (jeton RS256 + JWKS, `require_admin`), `core/webhook` (signature Svix/Standard Webhooks), `core/errors` (`{code, message}`), `domain/models` (`user_profile`, `consents`), `services/user_data` (accès aux données), `adapters/clerk` (suppression du compte Clerk), routes `/me`, `/me/adult-confirmation`, `/me/export`, `DELETE /me`, `/admin/status`, `/webhooks/clerk`.
- **Migration** `alembic/versions/0001_user_profile_and_consents.py` (testée : montée, descente, absence de dérive avec les modèles).
- **Front** (`apps/web`) : Clerk (`@clerk/nextjs`, textes en français), `proxy.ts`, pages `/sign-in`, `/sign-up`, `/onboarding` (18+), `/account` (export + suppression à deux clics), `/admin`, client d'API validé par Zod.
- **CI** : service PostgreSQL pour les tests de l'API ; clé Clerk factice de forme valide pour le `build` du front.
- **Outillage** : `scripts/smoke_test.py` (tes vraies clés), `.env.example` complété, Dockerfile (copie d'`alembic`), README.

## Décisions et pourquoi (dont celles prises à ta place)
| Décision | Alternatives | Raison |
|---|---|---|
| **Branche créée depuis `part-00-fondations`**, pas depuis `main` | Depuis `main` | Constat : `origin/main` ne contient **que l'import du pack** ; la partie 0 n'y est pas fusionnée (contrairement à l'énoncé). Sans elle, il n'y a aucun code. |
| Rôle admin = `public_metadata.role` + claim `metadata` dans le jeton | Organisations Clerk, liste en base | Simple, non modifiable par l'utilisateur, vérifié serveur (ADR 0009) |
| Session / durée : défauts Clerk | Réglage fin | Pas de besoin métier en partie 1 (ADR 0009) |
| Pool Neon : URL poolée (app) + directe (migrations), `prepare_threshold=None` | Une seule URL | PgBouncer et migrations/requêtes préparées s'entendent mal |
| Webhook : HMAC écrit à la main | Paquet `svix` | Une dépendance en moins, plus pédagogique, testé |
| `PyJWT` + JWKS | SDK Clerk Python | Standard, pas de dépendance spécifique |
| **Pas de colonne `deleted_at`** dans `user_profile` (écart avec `docs/03`) | La garder | Suppression **définitive** (cascade) : une suppression « logique » contredirait l'effacement RGPD |
| Case 18+ : étape `/onboarding` **après** l'inscription Clerk, pas dans le formulaire Clerk | Champ personnalisé Clerk | Le composant Clerk n'a pas de case personnalisée simple ; l'étape est imposée côté serveur par `require_adult` (à utiliser sur toutes les routes métier suivantes) |
| Pas de consignation du refus 18+ ; lien « Quitter et supprimer mon compte » sur l'onboarding | Enregistrer le refus | Règle §6.10 : ne pas consigner la minorité |
| Profil créé par le webhook **ou** à la confirmation 18+ (idempotent) | Webhook seul | Le webhook peut arriver après le premier clic |
| `DELETE /me` : données effacées **puis** compte Clerk ; si Clerk échoue → 502 mais données déjà effacées, rejouable | Clerk d'abord | Priorité à l'effacement de nos données |
| Export générique : `USER_OWNED_MODELS` + test qui échoue si une table avec `user_id` est oubliée | Export écrit à la main | Les parties suivantes ne pourront pas « oublier » une table |
| `record_consent` ajouté dans la couche d'accès (relève de la partie 2) | Attendre | La table `consents` existe dès maintenant ; nécessaire pour tester export/cascade/isolation |
| `GET /me` met à jour `last_active_at` | Ne rien faire | Servira à la purge des comptes inactifs (partie 14) |
| `/docs` etc. inchangés ; CORS autorise maintenant `GET, POST, DELETE` | — | Nécessaire pour les nouvelles routes (PUT/PATCH seront ajoutés en partie 2 si besoin) |
| Tests : base locale `stagefinder_test` (garde-fou : nom finissant par `_test`) | Base en mémoire (SQLite) | PostgreSQL réel = mêmes contraintes, `ON CONFLICT`, cascades |
| `urllib` pour l'appel à Clerk | Ajouter `httpx` en dépendance d'exécution | Un seul appel simple ; aucune dépendance ajoutée |

## Paquets ajoutés (vérifiés sur PyPI / npm ; versions figées dans les lockfiles)
**Backend (PyPI)** — directs : `alembic` 1.20.1 (Mike Bayer / SQLAlchemy), `SQLAlchemy` 2.1.9 (Mike Bayer), `psycopg[binary]` 3.3.9 (Daniele Varrazzo), `PyJWT[crypto]` 2.15.1 (José Padilla), `cryptography` 50.0.2 (Python Cryptographic Authority). Transitifs : `psycopg-binary` 3.3.9 (Varrazzo), `cffi` 2.1.1 (Armin Rigo, Maciej Fijalkowski), `pycparser` 3.12 (Eli Bendersky), `Mako` 1.4.3 (Mike Bayer), `MarkupSafe` 3.0.4 (Pallets), `tzdata` 2026.6 (Python Software Foundation).
**Front (npm)** — directs : `@clerk/nextjs` 7.10.10 et `@clerk/localizations` 4.28.0 (Clerk, dépôt `clerk/javascript`). Transitifs : `@clerk/backend` 3.33.1, `@clerk/react` 6.19.7, `@clerk/shared` 4.50.0 (Clerk) ; `@stablelib/base64` 1.0.1 et `fast-sha256` 1.3.0 (Dmitry Chestnykh) ; `@tanstack/query-core` 5.108.4 (TanStack, Tanner Linsley) ; `glob-to-regexp` 0.4.1 (Nick Fitzgerald) ; `js-cookie` 3.0.8 (Klaus Hartl) ; `server-only` 0.0.1 (Sebastian Markbåge, React) ; `standardwebhooks` 1.3.0 (Standard Webhooks). Aucun doute sur un nom ou un éditeur ; `pnpm audit` / `uv audit` non relancés (voir limites). Un avertissement de pair `@types/node` (vitest) existait déjà en partie 0.

## Comment tester à la main (avec tes clés)
1. **Clerk** : crée une application (région UE si possible). Récupère `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY`, l'URL de l'instance (`CLERK_JWT_ISSUER`, ex. `https://xxx.clerk.accounts.dev`). *Sessions → Customize session token* : `{"metadata": "{{user.public_metadata}}"}`. *Webhooks* : endpoint `https://<ton-api>/webhooks/clerk` (en local : tunnel) avec les événements `user.created` et `user.deleted` ; copie le secret `whsec_…` dans `CLERK_WEBHOOK_SECRET`.
2. **Neon** (région Frankfurt) : copie l'URL poolée dans `DATABASE_URL` et l'URL directe dans `DATABASE_URL_DIRECT`. Puis `cd apps/api && uv run alembic upgrade head`.
3. **Smoke test** : `cd apps/api && uv run python ../../scripts/smoke_test.py` ; puis, backend lancé, `SMOKE_API_URL=http://localhost:8000 uv run python ../../scripts/smoke_test.py` (+ `SMOKE_SESSION_TOKEN` copié du navigateur pour tester `/me` et `/admin/status`).
4. **Parcours** : lance l'API et `pnpm dev` ; crée un compte → tu arrives sur `/onboarding` → coche 18+ → `/account` ; « Exporter mes données » télécharge un JSON ; « Supprimer mon compte » (2 clics) te déconnecte et l'utilisateur disparaît de Clerk et de la base.
5. **Admin** : dans Clerk, ajoute `{"role": "admin"}` aux *public metadata* de ton utilisateur, reconnecte-toi (≈ 1 min), ouvre `/admin` : espace vide. Un autre compte voit « Accès refusé » (403 renvoyé par le serveur).

## Tests automatiques
- API (`uv run pytest`) : jetons (valide, expiré, mauvais émetteur/`azp`/clé, HS256, `alg=none`, sans jeton, rôle falsifié, auth non configurée = fermé), webhook (signature unitaire + HTTP : création idempotente, suppression, signature fausse, trop ancien, corps falsifié, trop gros), **isolation A/B** (services : lecture, écriture, suppression ; HTTP ; aucune route avec `user_id`), export complet, **suppression en cascade table par table**, idempotence, panne de Clerk, 18+ (refus non consigné, consigné une seule fois, `require_adult`), schéma (liste blanche de colonnes, mots interdits, registre d'export, migration montée/descendue, aucune dérive), erreurs sans écho des valeurs, logs sans donnée personnelle, configuration (variables manquantes, issuer https, secrets non affichés). 1 test `integration` (JWKS réel) ignoré sans `CLERK_JWT_ISSUER`.
- Front (`pnpm test`) : client d'API (jeton, erreurs, réponse invalide, réseau), onboarding 18+ (bouton bloqué, rien envoyé avant la case), suppression à deux clics, panneau admin 200/403.
- Résultats locaux : ruff, format, mypy strict, pytest 59 + 1 ignoré ; eslint, prettier, tsc, vitest 22, `next build` ; `docker build` OK ; l'image refuse de démarrer sans variables (message sans valeur secrète).
- **CI GitHub : non observée** — `gh` n'est pas installé sur cette machine (voir limites).

## Règles RGPD / sécurité touchées
R2 (liste blanche de colonnes), R3 (isolation : couche d'accès + tests), R4 (export, suppression, webhook), R5 (logs : whitelist, webhook jamais loggé, test), R12 (colonne `ai_assist_consent` décochée par défaut ; le journal sera alimenté en partie 2), R13 (18+). §7 : jeton vérifié côté serveur à chaque requête, admin côté serveur, aucun secret dans le dépôt (`SecretStr`, `.env.example` = noms), requêtes SQL paramétrées (ORM), erreurs `{code, message}` sans donnée personnelle. **Pas de RLS** (prévue plus tard) : la structure (toutes les requêtes passent par `services/user_data` avec `user_id`) permet de l'ajouter.

## Limites connues et risques
- **Aucun test avec un vrai Clerk/Neon** : le format du claim personnalisé, `DELETE /v1/users/{id}` (404 = déjà supprimé) et les événements du webhook viennent de la documentation/mémoire, pas d'un appel réel. Le smoke test les vérifie.
- Le **jeton garde ses droits jusqu'à son expiration** (~60 s) : un retrait de rôle admin n'est pas instantané.
- Un mineur qui ne coche pas la case reste « connecté » à Clerk sans profil adulte : les routes métier futures doivent utiliser `require_adult` (non utilisé par d'autres routes tant qu'il n'y en a pas).
- Pas de limitation de débit (rate limiting) sur le webhook ni sur `/me` : à traiter avec les quotas (partie 12).
- `gh` absent : **PR non ouverte, CI non vérifiée** (branche poussée ; voir compte rendu). Partie 0 non fusionnée sur `main` (voir décisions).
- `pnpm audit` / `uv audit` non relancés sur les nouvelles dépendances (réseau/permissions) : à faire.
- Texte d'information RGPD complet et consentement IA : partie 2 (hors périmètre ici).

## Idées hors périmètre (non faites)
RLS PostgreSQL ; limitation de débit ; invalidation immédiate des sessions admin ; tâche de purge des comptes inactifs (partie 14) ; message d'erreur dédié quand Clerk est injoignable côté front.

## À savoir expliquer en entretien
1. **Authentification vs autorisation** : le jeton (JWT) prouve *qui* ; le rôle et `require_adult` décident *ce qu'on peut faire*. Tout est vérifié côté serveur, le front n'est que de l'affichage.
2. **JWT signé RS256 + JWKS** : on vérifie signature, émetteur, expiration avec les clés *publiques* de Clerk ; un seul algorithme accepté (sinon attaques `alg=none` / HS256, testées).
3. **Isolation par construction** : aucune route n'accepte un `user_id` ; l'identité vient du jeton ; la couche d'accès filtre toujours dessus ; un test garde-fou impose que toute nouvelle table avec `user_id` soit exportée.
4. **Webhook signé** : HMAC-SHA256 sur `id.timestamp.corps`, comparaison en temps constant, fenêtre de 5 min contre le rejeu, opérations idempotentes.
5. **Droit à l'effacement** : cascade en base (`ON DELETE CASCADE`), vérifiée table par table ; ordre « nos données puis Clerk » et pourquoi.
6. **Neon serverless** : pooler (PgBouncer) pour l'app, connexion directe pour les migrations, requêtes préparées désactivées.
7. **Minimisation** : liste blanche de colonnes testée ; pas de `deleted_at` (suppression réelle) ; la minorité n'est jamais consignée.
8. **Migrations testées** : on applique les vraies migrations sur une base jetable et on vérifie qu'elles correspondent aux modèles.

## Questions pour l'utilisateur / validation attendue
1. Valider le schéma (`user_profile`, `consents`, sans `deleted_at`) et la méthode admin (`public_metadata` + claim).
2. Brancher Clerk/Neon, lancer le smoke test et le parcours manuel ci-dessus.
3. Installer `gh` (ou ouvrir toi-même la PR) ; décider de l'ordre de fusion (partie 0 d'abord).
