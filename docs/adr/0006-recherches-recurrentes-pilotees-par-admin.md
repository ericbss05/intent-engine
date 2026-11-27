# ADR 0006 — Recherches récurrentes déclenchées par l'utilisateur, quotas fixés par l'admin

- **Statut** : accepté (27 nov. 2026)
- **Contexte** : les quotas gratuits des fournisseurs sont faibles ; il faut du contrôle des coûts et de la volumétrie ; pas de pré-crawl massif.
- **Décision** : l'étudiant crée une recherche (fréquence 1/2/3 jours) ; un job quotidien exécute celles dont `next_run_at <= now` ; **quota par exécution et fréquence autorisée fixés par l'admin** (valeurs globales + exceptions par utilisateur), **appliqués côté serveur** ; budget global mensuel ; pause automatique après ≈ 14 jours d'inactivité ; boutons pause/suppression ; **aucun envoi automatique** ; journal des changements de configuration.
- **Conséquences** : tables `searches`, `admin_config`, `admin_config_user`, `admin_config_log` ; tâches idempotentes (clé SIREN + étape) ; tests de simulation du temps.
