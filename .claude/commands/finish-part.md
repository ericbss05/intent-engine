---
description: Termine une partie : vérifications, rapport, attente de validation
argument-hint: <numéro de partie>
---

Tu termines la **partie $ARGUMENTS**.

1. Lance lint, vérification de types et tests (front et backend concernés) ; corrige ou signale tout échec. Ne désactive aucun test.
2. Relis la définition de « terminé » dans `CLAUDE.md` §13 et les critères de `prompts/part-NN.md` ; coche chaque point **avec une preuve** (commande, test, capture, fichier).
3. Relis `docs/04-regles-rgpd-pour-le-code.md` : indique les règles touchées et les tests associés.
4. Écris `docs/reports/part-NN.md` à partir de `templates/part-report-template.md`, y compris **« À savoir expliquer en entretien »**.
5. Crée un ADR si une décision structurante a été prise ; mets à jour le statut dans `docs/05-plan-par-parties.md`.
6. Résume à l'utilisateur en 5–8 lignes : ce qui marche, ce qui reste incertain, comment tester à la main.
7. **Arrête-toi** : attends la validation explicite avant toute autre partie.
