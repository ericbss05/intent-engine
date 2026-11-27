# Partie 6 — Découverte SIRENE + cache partagé (≈ 4 j)

## Contexte
Partie 1 validée (peut se faire avant 3–5). Lis `docs/06` (CompanyDiscovery), `docs/03` (companies), `docs/adr/0005`, `docs/04` (R9), `docs/08` §7.4.

## Tâche
1. Interface `CompanyDiscovery` + adaptateur **API Recherche d'entreprises** (données ouvertes) : filtres NAF, code postal/département, tranche d'effectif ; pagination ; limites de débit ; retries ; **lire la documentation officielle** (champs, limites, licence).
2. Adaptateur de secours **API INSEE Sirene** (clé requise) derrière la même interface ; bascule automatique avec disjoncteur simple.
3. Table partagée `companies` (clé unique SIREN) : provenance, `fetched_at`, `ttl_at`, statut `pending/ready/stale/failed` ; upsert idempotent.
4. **Exclusion des entreprises individuelles** ; respect du statut de diffusion ; jamais de reconstitution d'adresse masquée.
5. Jeu de fixtures de réponses (enregistrées/synthétisées) ; tests sans réseau.
6. Commande/route admin de test : lancer une découverte à partir de préférences factices.

## Contraintes
- Citer la source (Licence Ouverte 2.0) là où les données sont affichées.
- Respect des limites de débit officielles (ne pas les deviner : lire et configurer).
- Aucun enrichissement (site, contact) ici.

## Sorties attendues
Adaptateurs `sirene` et `insee`, migration `companies`, service de découverte, fixtures, tests, `docs/reports/part-06.md`.

## Critères de terminé
- [ ] Une découverte renvoie ≥ 50 entreprises plausibles pour des préférences types, sans doublon.
- [ ] Test : aucune entreprise individuelle, aucune adresse masquée reconstituée.
- [ ] Bascule SIRENE → INSEE testée avec une panne simulée.

## Questions à poser avant de coder
Format exact des filtres de zone ; durée de vie (TTL) des fiches ; clé INSEE disponible ?

## Hors périmètre
Scoring, site web, contacts.
