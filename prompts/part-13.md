# Partie 13 — Évaluation chiffrée (≈ 3 j)

## Contexte
Parties 7, 9, 11 validées (et 3–5, 10 pour la couche IA). Lis `docs/07-evaluation.md` en entier.

## Tâche
1. Consolider les jeux annotés : ≈ 10 CV synthétiques, ≈ 30 entreprises annotées, profils de test pour la pertinence.
2. Script d'évaluation unique (`make eval` ou équivalent) qui exécute toutes les mesures reproductibles et produit `docs/evaluation.md`.
3. Métriques : rappel des compétences (règles vs assisté si IA), détection d'anonymisation, site correct, « introuvable » honnête, emails valides, crédits par clic, précision@5 (règles vs LLM si activé), taux d'échec par étape, coût par recherche.
4. Test de pertinence perçue avec 5–10 étudiants volontaires (consentement explicite, aucune donnée inutile) : protocole écrit, résultats agrégés.
5. Section « Limites » : petits échantillons, biais, ce qui n'est pas mesuré ; section « Décisions des portes » (P4, P5a, P5b, P10 ouvertes ou fermées).

## Contraintes
- Aucune donnée personnelle réelle dans les jeux ; résultats **non embellis**.
- Reproductibilité : mêmes données → mêmes chiffres (graines fixées).

## Sorties attendues
Script d'évaluation, `docs/evaluation.md`, protocole de test étudiants, `docs/reports/part-13.md`.

## Critères de terminé
- [ ] `docs/evaluation.md` généré par le script, avec limites honnêtes.
- [ ] Les portes de l'IA sont justifiées par des chiffres.

## Questions à poser avant de coder
Combien d'étudiants volontaires ; format de recueil des retours.

## Hors périmètre
Nouvelles fonctionnalités.
