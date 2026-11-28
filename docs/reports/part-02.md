# Rapport — Partie 2 : Questionnaire et consentements

> **Branche empilée** : `part-02-questionnaire-consentements` est créée depuis `part-01-compte-et-droits` (qui l'est elle-même depuis `part-00-fondations`). Fusionner dans l'ordre : partie 0 → partie 1 → partie 2.

## Résumé
Parcours d'inscription en 3 étapes (information RGPD → 18+ → choix IA décoché par défaut), consentements journalisés avec la version du texte et retirables à tout moment, questionnaire de recherche (table `search_preferences`, validation Pydantic côté serveur + Zod côté front), écran de modification, garde « pas de consentement, pas d'IA », `data/naf_mapping.json` (**brouillon, à relire par toi**). Lint, types, tests verts en local (API : 118 tests + 1 ignoré ; front : 38 tests ; `next build` OK ; image Docker testée). **Critère « table NAF relue et validée » : NON atteint** (c'est à toi de le faire). Aucun appel externe, aucune clé nécessaire.

## Ce qui est fait
- **Backend** : modèle + migration `0002_search_preferences`, `domain/schemas.py` (validation), `domain/reference.py` (chargement validé de `data/*.json`), `services/preferences.py`, `services/consents.py`, `services/ai_guard.py`, routes `GET/PUT /me/preferences`, `GET /me/consents`, `PUT /me/consents/{kind}`, `GET /reference/sectors` et `/reference/consent-texts` (publiques).
- **Données** : `data/naf_mapping.json` (20 secteurs, statut « brouillon »), `data/consent_texts.json` (textes d'information et d'option IA, version `2026-11-28-draft1`).
- **Front** : `OnboardingFlow` (3 étapes), `PreferencesForm` (React Hook Form + Zod, messages en français), `AiConsentPanel` (activer / retirer), page `/preferences`, lien depuis `/account`.
- **Docker** : le contexte de build passe à la racine du dépôt (voir ADR 0010) ; CI et README adaptés.

## Décisions et pourquoi (dont celles prises à ta place)
| Décision | Alternatives | Raison |
|---|---|---|
| **Secteurs : 20 secteurs, codes NAF au niveau division / groupe** (ex. `62`, `58.2`) avec règle « un établissement correspond si son code commence par… » | Sous-classes détaillées partout | Moins de risque d'erreur et de trous ; la précision pourra être affinée après ta relecture |
| **Zone** = code postal (5 chiffres) **ou** département (`75`, `2A`, `971`) + **rayon en km** (0 à 200 ; 0 = cette zone seulement) | Adresse, ville | Zone grossière, jamais d'adresse exacte (R2) |
| **Tailles** : `1-9`, `10-49`, `50-249`, `250-999`, `1000+` salariés | Catégories PME/ETI/GE | Proche des tranches d'effectif SIRENE (à confirmer en partie 6) |
| **Priorités** (facultatif) : secteur / proximité / taille, 3 max | Liste libre | Prépare le scoring (partie 7) sans inventer de critères |
| **Durée** : 1 à 36 mois, sans règle propre à chaque contrat | Stage ≤ 6 mois, alternance 6–36 | Éviter de rejeter une saisie valable sur une règle que je n'ai pas vérifiée |
| **Entreprises exclues** : SIREN à 9 chiffres, **sans contrôle de clé (Luhn)** | Avec Luhn | Certains SIREN réels (ex. La Poste) ne passent pas Luhn |
| **Textes d'information : fichier JSON servi par l'API**, version consignée à chaque accord ; **409** si la version envoyée n'est plus en vigueur | Texte en dur dans le front | Une seule source ; l'accord est toujours lié au texte réellement vu |
| **Consentement IA** : journal en ajout seulement (`consents`) = source de vérité ; `user_profile.ai_assist_consent` = copie synchronisée ; refus initial = aucune ligne ; même choix répété = aucune ligne | Booléen seul | Preuve + historique des retraits |
| **`privacy_notice`** : accusé de lecture, accord seulement (pas de retrait) | Retrait possible | Retirer la prise de connaissance d'une information n'a pas de sens ; la sortie, c'est la suppression du compte |
| **Accord écrit à la fin** du parcours (après la case 18+), pas à chaque étape | Écriture immédiate | Les routes de consentement exigent « 18+ confirmé » ; rien n'est enregistré si la personne abandonne |
| **Routes `/reference/*` publiques** | Authentifiées | L'information RGPD doit être lisible avant l'inscription complète ; aucune donnée personnelle |
| **Pas de consentement « entraînement »** : le serveur refuse tout type autre que `privacy_notice` / `ai_assist` (test) | — | ADR 0007 |
| **Docker : contexte à la racine** | Dupliquer `data/` dans `apps/api` | Une seule source de vérité (ADR 0010) |
| `PUT` ajouté au CORS | — | Nécessaire pour les routes d'écriture |

## Paquets ajoutés (npm ; vérifiés sur le registre officiel, versions figées dans `pnpm-lock.yaml`)
Directs : `react-hook-form` 7.92.0 (mainteneur Bill Luo / org `react-hook-form`) et `@hookform/resolvers` 7.0.9 (org `react-hook-form`) — imposés par `docs/02` (Zod + React Hook Form). Transitifs : `@standard-schema/utils` 0.3.0 (Fabian Hiller, Colin McDonnell — Standard Schema) et `ajv-formats` 2.1.1 (Evgeny Poberezkin — Ajv), installés comme pairs des résolveurs. Aucun doute sur un nom ou un éditeur. **Aucun paquet Python ajouté.**

## Comment tester à la main
1. Les mêmes clés qu'en partie 1 (Clerk, Neon) ; appliquer la migration : `cd apps/api && uv run alembic upgrade head` (applique `0002`).
2. Créer un compte : tu vois d'abord le texte d'information, puis la case 18+, puis le choix IA (**décoché**). Terminer → `/preferences`.
3. Remplir le questionnaire : un champ invalide affiche un message en français et rien n'est envoyé ; enregistrer ; recharger la page : les valeurs reviennent ; modifier et réenregistrer.
4. `/account` : « Analyse du CV assistée par IA : désactivée » ; activer puis « Retirer mon accord ». Vérifier en base (`select kind, granted, version_text from consents`) : une ligne par changement, avec la version du texte.
5. **Relire `data/naf_mapping.json`** (voir « Validation attendue »).
6. Smoke test : `SMOKE_API_URL=http://localhost:8000 uv run python ../../scripts/smoke_test.py` (vérifie aussi les routes publiques et protégées de cette partie).
7. Image : `docker build -f apps/api/Dockerfile -t stage-finder-api .` (depuis la racine).

## Tests automatiques
- API (118 + 1 ignoré) : **validation du questionnaire** (27 cas invalides en paramétré : contrat, durée, métier avec `<`, secteurs vides/inconnus/dupliqués, zone = adresse, rayon, tailles, priorités, SIREN, champs interdits, injection de `user_id`) ; normalisation ; 404 avant première sauvegarde ; **isolation** A/B ; suppression en cascade et export incluent `search_preferences` ; **consentements** (décoché par défaut, accord journalisé avec version, retrait, idempotence, refus initial sans ligne, version obsolète → 409, `privacy_notice` non retirable, types inconnus dont « model_training » → 422, par utilisateur) ; **garde IA** (bloque sans accord, après retrait, par utilisateur, dépendance FastAPI sur une route d'essai : le « futur appel IA » n'est jamais atteint sans accord) ; données de référence (format NAF, codes uniques, fichier corrompu = chargement refusé) ; schéma (liste blanche de colonnes mise à jour, dérive migration/modèles).
- Front (38) : schéma Zod, formulaire (messages français, aucun appel serveur si invalide, chargement et modification), parcours d'inscription (rien envoyé avant la fin, IA décochée par défaut = aucune ligne `ai_assist`, version du texte envoyée si coché, erreur d'enregistrement), panneau IA (activer/retirer).
- Résultats locaux : ruff, format, mypy strict, pytest ; eslint, prettier, tsc, vitest, `next build`.
- **CI GitHub : non observée** (voir « Limites »).

## Règles RGPD / sécurité touchées
R2 (pas de colonne interdite : liste blanche testée ; zone grossière), R3 (isolation : tests), R4 (export et cascade incluent la nouvelle table), R12 (décoché par défaut, journalisé, retirable, **garde testée**), R13 (18+ avant les consentements et le questionnaire : `require_adult`), R17 (texte d'information fourni, version consignée ; politique complète en partie 14). §6.9 : consentement séparé et décoché ; mode sans IA complet. ADR 0007 : aucun consentement d'entraînement. §7 : validation aux frontières (Pydantic + Zod, `extra="forbid"`), erreurs sans écho des valeurs, aucune requête SQL concaténée.

## Limites connues et risques
- **`naf_mapping.json` non validé** : codes écrits de mémoire de la NAF rév. 2, jamais comparés à la nomenclature officielle de l'INSEE ; marqué « brouillon » (un test le rappelle).
- **Textes d'information provisoires** avec des passages **[à compléter]** (responsable de traitement, contact, hébergeurs) visibles dans l'interface : ne pas lancer en public avant la partie 14.
- **Texte du consentement IA** décrit un fournisseur UE à rétention zéro, **pas encore choisi ni vérifié** (porte de décision, parties 4–5).
- Quand une version de texte change, les anciens accords restent liés à l'ancienne version ; le ré-affichage et le nouvel accord ne sont **pas** implémentés.
- Pas de rate limiting sur ces routes ; durée « 12 mois d'inactivité » du texte pas encore appliquée (purge : partie 14).
- Le texte d'information est affiché avant que l'identité soit confirmée par la case 18+ : choix voulu par le parcours du brief.
- **PR / CI** : `gh` absent, voir compte rendu. Les tests API supposent un PostgreSQL local (Docker) comme en partie 1.
- Rapport de la partie 0 : sa commande `docker build … apps/api` est devenue obsolète (voir ADR 0010) ; le README est à jour.

## Idées hors périmètre (non faites)
Ré-acceptation automatique après changement de texte ; secteurs affinés avec la NAF complète ; priorités ordonnées par glisser-déposer ; sauvegarde brouillon du questionnaire ; historique des consentements visible dans l'interface (il est dans l'export JSON).

## À savoir expliquer en entretien
1. **Consentement valable** : libre (case décochée, service accessible sans), spécifique (séparé du reste), éclairé (texte versionné), prouvable (journal horodaté), retirable aussi facilement que donné.
2. **Journal en ajout seulement** : on ne modifie jamais une ligne ; l'état courant est la dernière ligne ; le booléen du profil n'est qu'une copie.
3. **Garde de sécurité par conception** : `require_ai_consent` est une fonction unique que tout futur code IA doit appeler ; testée avec une route d'essai ; lit le journal, donc un retrait est immédiat.
4. **Validation double** : Zod pour l'ergonomie (messages), Pydantic pour la sécurité (source de vérité) ; `extra="forbid"` rejette un champ inattendu (ex. `user_id`).
5. **Minimisation** : zone = code postal ou département, jamais d'adresse ; pas de colonnes interdites, vérifié par un test de liste blanche.
6. **Données de référence validées au démarrage** : un JSON invalide = l'application refuse de démarrer ; texte et version viennent de la même source que celle qui journalise.
7. **Pourquoi 409 si la version du texte a changé** : l'accord doit porter sur le texte réellement vu.
8. **Limites assumées** : NAF de mémoire et marquée brouillon ; textes juridiques provisoires.

## Questions pour l'utilisateur / validation attendue
1. **Relire et valider `data/naf_mapping.json`** : secteurs affichés, codes NAF (nomenclature INSEE), niveau de détail. Une fois validé : passer `status` à « validé le … » et adapter le test `test_naf_mapping_is_flagged_as_draft_until_validated`.
2. Relire `data/consent_texts.json` ; compléter les passages entre crochets ; décider du responsable de traitement.
3. Confirmer : tailles d'entreprise, plage de durée (1–36), contenu de la liste des priorités.
4. Ordre de fusion : 0 → 1 → 2.
