# Partie 12 — Admin, coûts, observabilité (≈ 3 j)

## Contexte
Partie 8 validée (idéalement après 9 et 11 pour avoir des données). Lis `docs/03` (admin_*, provider_usage, run_events), `docs/adr/0004` et `0006`.

## Tâche
1. Pages admin (rôle vérifié côté serveur) : quotas et fréquences (global + exceptions par utilisateur), **ordre et activation des fournisseurs** par besoin, **budget mensuel** par fournisseur, état des disjoncteurs.
2. Tableau de bord : coût estimé par recherche et par semaine, taux d'échec par étape et fournisseur, crédits restants, recherches actives/en pause.
3. Journal des changements de configuration (`admin_config_log`) visible.
4. Alertes (au minimum dans l'interface et `run_events`) : fournisseur sous disjoncteur, budget > 80 %, taux d'échec anormal. Sentry **optionnel**, sans données personnelles.
5. Tests : accès admin refusé aux non-admins (403 serveur), modifications journalisées, la configuration modifiée est bien appliquée au pipeline.

## Contraintes
- Aucune donnée personnelle dans les tableaux de bord (agrégats).
- Valeurs de config en base, jamais en dur.

## Sorties attendues
Routes et pages admin, requêtes d'agrégation, tests, `docs/reports/part-12.md`.

## Critères de terminé
- [ ] Tu réponds en 1 minute à « combien cette semaine ? » et « quelle étape échoue le plus ? ».
- [ ] Changement d'ordre de fournisseurs appliqué sans redéploiement.

## Questions à poser avant de coder
Seuils d'alerte ; devise/estimation des coûts (indiquer clairement que ce sont des estimations).

## Hors périmètre
Facturation, multi-admin avancé.
