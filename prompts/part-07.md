# Partie 7 — Scoring à règles + liste de résultats (≈ 4 j)

## Contexte
Parties 3 et 6 validées. Lis `docs/06` (Matcher), `docs/03` (search_results), `docs/07` (précision@5), `docs/04` (R10).

## Tâche
1. `RulesMatcher` : **fonction pure** (profil validé + préférences + fiche entreprise → score, `breakdown`, explication en français). Critères pondérés : secteur ↔ métier visé, distance, taille, mots-clés du profil vs libellé d'activité/NAF. Pondérations dans la configuration (pas en dur).
2. Tables `search_results` (rang, `score_breakdown`, statut `proposed/seen/ignored`) + contrainte unique `(search_id, company_id)`.
3. UI : liste classée, panneau « **Pourquoi cette entreprise** » (contribution de chaque critère), boutons « Ignorer » (effectif) et « Voir le contact » (désactivé jusqu'à la partie 11).
4. Exclusion des entreprises déjà contactées/ignorées/vues ; déduplication entre exécutions.
5. Tests : **reproductibilité** (mêmes entrées → même sortie), cas limites, explication cohérente avec le score.

## Contraintes
- Aucun appel externe ni IA dans le scoring.
- Le classement n'a **aucun effet automatique** (R10).
- Expliquer dans le rapport comment les pondérations ont été choisies et comment les ajuster.

## Sorties attendues
Service `scoring`, migration, routes, UI liste/détail, tests, `docs/reports/part-07.md`.

## Critères de terminé
- [ ] Première liste utile **sans scraping**, avec explication lisible.
- [ ] Score reproductible (test).
- [ ] Test rapide avec 2–3 étudiants (informel) : notes de pertinence consignées dans le rapport.

## Questions à poser avant de coder
Pondérations de départ ; présentation de l'explication ; seuil minimal d'affichage.

## Hors périmètre
Récurrence automatique, enrichissement, contacts.
