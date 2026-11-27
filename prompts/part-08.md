# Partie 8 — Recherches récurrentes + orchestration (≈ 5 j)

## Contexte
Partie 7 validée. Lis `docs/adr/0006`, `docs/01-architecture.md` (flux), `docs/03` (searches, admin_config*, run_events), `docs/04` (R8, R10).

## Tâche
1. **Vérifier d'abord** la disponibilité et les limites du **SDK Python d'Inngest** (documentation officielle). Si inadapté, proposer 2 alternatives (ex. file de tâches maison avec planificateur, autre orchestrateur) avec avantages/inconvénients, et **demander** avant de continuer.
2. Tables `searches` (fréquence 1/2/3 jours, quota par exécution, `next_run_at`, statut), `admin_config`, `admin_config_user`, `admin_config_log`, `run_events`.
3. Tâche planifiée quotidienne : sélectionner les recherches `active` avec `next_run_at <= now`, respecter quota, budget global mensuel et concurrence par utilisateur ; enchaîner découverte → fiches → scoring → enregistrement des résultats (**étapes idempotentes**, clé `(siren, step)`) ; recalculer `next_run_at`.
4. **Quota et fréquence fixés par l'admin** (valeurs globales + exceptions par utilisateur), **appliqués côté serveur** ; l'étudiant ne peut que choisir parmi les fréquences autorisées.
5. Pause automatique après ≈ 14 jours sans activité ; boutons pause/reprise/suppression ; journal des changements de config.
6. **SSE** : endpoint qui diffuse `run_events` ; reprise via `Last-Event-ID` ; page de suivi en direct.
7. Tests avec **simulation du temps** : exécution à l'heure, respect du quota, aucun doublon même relancée deux fois, pause automatique.

## Contraintes
- Aucun appel à `ContactFinder`/`EmailVerifier` dans cette tâche automatique (R8).
- Aucun envoi d'email ou de candidature.
- `run_events` sans donnée personnelle.

## Sorties attendues
Migrations, workflows, services quotas/budget, endpoint SSE, pages front de suivi, tests, `docs/reports/part-08.md`.

## Critères de terminé
- [ ] Cycle complet sans action manuelle, respectant quota/fréquence/budget.
- [ ] Relance double sans doublon (test).
- [ ] Reprise SSE après coupure démontrée.

## Questions à poser avant de coder
Valeurs par défaut (quota, fréquences autorisées, budget) ; orchestrateur si Inngest Python inadapté.

## Hors périmètre
Site web/lecture de pages, contacts.
