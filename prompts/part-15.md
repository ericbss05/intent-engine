# Partie 15 — Finition, démo, portfolio (≈ 3 j)

## Contexte
Partie 14 validée. L'objectif : qu'une personne sans contexte comprenne le problème, la solution et les limites en 3 minutes (recruteurs, camarades).

## Tâche
1. README principal : problème, solution, schéma d'architecture, stack, comment lancer, résultats chiffrés (renvoi vers `docs/evaluation.md`), limites honnêtes.
2. Récit « décisions et limites » : 8–10 décisions clés (ADR) avec alternatives et raisons ; ce qui a été **mesuré** ; ce qui a été **refusé** (envoi automatique, scraping derrière login, CV stocké…).
3. Jeu de **données de démo** : comptes fictifs, CV synthétiques, entreprises réelles publiques (personnes morales) ; mode démo sans données personnelles.
4. Vidéo ou GIF de 2 minutes (script fourni) ; captures d'écran pour le CV/portfolio.
5. Guide de test pour 5 étudiants BSB (consentement, durée, retours).
6. Page « Ce que j'ai appris / architecture / RGPD par conception » (version pour recruteurs).
7. Déploiement final vérifié (front + backend UE), checklist de lancement restreint (quelques étudiants), plan de suppression des données de test.

## Contraintes
- Aucune donnée personnelle réelle dans la démo ni les captures.
- Ne pas gonfler les résultats ni la conformité (« conçu pour limiter les risques » ; relu par … si c'est le cas).

## Sorties attendues
`README.md`, `docs/recit-decisions.md`, données de démo, script de vidéo, guide de test, page recruteurs, `docs/reports/part-15.md`.

## Critères de terminé
- [ ] Une personne externe comprend et peut tester en 10 minutes.
- [ ] Les chiffres du README correspondent exactement à `docs/evaluation.md`.

## Questions à poser avant de coder
Public visé (recruteurs, école) ; ton du récit ; mode démo public ou sur invitation.

## Hors périmètre
Nouvelles fonctionnalités.
