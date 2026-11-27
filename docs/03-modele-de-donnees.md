# 03 — Modèle de données (proposition de départ, à affiner partie par partie)

Notation indicative (SQL simplifié). Toutes les dates en UTC. Les tables « privées » sont rattachées à `user_id` et protégées par la couche d'accès + test d'isolation (puis RLS). Les tables « partagées » sont en lecture seule pour les utilisateurs.

## Tables privées (par étudiant)

```
user_profile        (user_id PK [id Clerk], created_at, adult_confirmed_at, ai_assist_consent bool, ai_assist_consent_at, last_active_at, deleted_at NULL)
consents            (id, user_id, kind ['ai_assist'|'privacy_notice'], granted bool, version_text, created_at)
search_preferences  (user_id PK, contract_type, duration_months, target_role, sectors jsonb, zone jsonb [codes postaux/départements + rayon], company_size jsonb, priorities jsonb, excluded_sirens jsonb, updated_at)
cv_profiles         (id, user_id, version int, skills jsonb, languages jsonb, certifications jsonb, education jsonb, experiences jsonb [texte résumé validé], created_at)   -- JAMAIS de PDF, JAMAIS de texte brut
searches            (id, user_id, frequency_days int [1|2|3], quota_per_run int, status ['active'|'paused'|'deleted'], next_run_at, last_run_at, created_at)
search_results      (id, search_id, user_id, company_id, rank, score numeric, score_breakdown jsonb, explanation text, status ['proposed'|'seen'|'ignored'], created_at, updated_at)
contact_requests    (id, user_id, company_id, status ['pending'|'done'|'failed'], created_at)
```

## Tables partagées (cache de fiches)

```
companies   (id, siren UNIQUE, name, naf, address_city, address_postcode, headcount_band, legal_form, diffusion_status, website, website_source, phone, fetched_at, ttl_at, status ['pending'|'ready'|'stale'|'failed'])
analyses    (id, company_id, kind ['careers_page'|'signals'|'llm_summary'], payload jsonb, source_urls jsonb, model NULL, fetched_at, ttl_at)
contacts    (id, company_id, name NULL, title NULL, generic bool, source, source_url NULL, origin ['published'|'inferred'|'provider'], provider NULL, fetched_at, ttl_at)
emails      (id, contact_id, address, origin ['published'|'inferred'|'provider'], status ['valid'|'invalid'|'catch_all'|'unknown'], verified_by NULL, checked_at, ttl_at)
suppression (id, email_hash UNIQUE, domain NULL, reason, created_at)    -- hash (pas l'email en clair)
```

## Tables techniques / admin

```
run_events          (id, search_id NULL, user_id NULL, step, level, detail jsonb [sans donnée personnelle], percent NULL, provider NULL, cost_estimate NULL, created_at)
admin_config        (key PK, value jsonb, updated_by, updated_at)           -- quotas, fréquences, ordre des fournisseurs, budgets
admin_config_user   (user_id, key, value jsonb, updated_by, updated_at)     -- exceptions par utilisateur
admin_config_log    (id, key, scope, old_value, new_value, changed_by, changed_at)
provider_usage      (id, provider, period [YYYY-MM], units_used, units_budget, circuit_state ['closed'|'open'|'half_open'], updated_at)
```

## Règles transversales
- Interdits dans le schéma : photo, date de naissance, nationalité, situation familiale, santé, adresse exacte, téléphone personnel, PDF du CV, texte brut du CV.
- `companies.diffusion_status` : si diffusion partielle, ne stocker/afficher que ce qui est autorisé ; exclure les entreprises individuelles par défaut.
- Index : `companies(siren)`, `search_results(user_id, search_id, status)`, `searches(status, next_run_at)`, `run_events(search_id, id)`, `emails(address)`, `suppression(email_hash)`.
- Idempotence : contraintes uniques sur `(search_id, company_id)` dans `search_results` ; clé `(siren, step)` pour les tâches d'enrichissement.

## Conservation (propositions à valider — voir `04` et `08`)
| Donnée | Durée proposée |
|---|---|
| Compte actif | tant qu'utilisé ; pause après ≈ 14 j sans recherche utile ; **suppression à 12 mois d'inactivité** (préavis 30 j) |
| `cv_profiles` anciennes versions | 3 versions max ou 90 jours |
| `contacts` / `emails` | TTL 6 mois si non consultés ; suppression sur opposition |
| `run_events` / logs | 6 mois |
| `suppression` | tant que nécessaire |
