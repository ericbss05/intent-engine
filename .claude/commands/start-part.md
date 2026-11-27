---
description: Démarre une partie du plan (lecture, questions, plan court)
argument-hint: <numéro de partie, ex. 3>
---

Tu démarres la **partie $ARGUMENTS** du projet.

1. Relis `CLAUDE.md`, puis `docs/00` à `docs/07` pertinents, `docs/adr/`, et surtout `prompts/part-$ARGUMENTS.md` (écris le numéro sur 2 chiffres : `part-03.md`, etc.).
2. Vérifie que la partie précédente a un rapport `docs/reports/part-NN.md` **et** que l'utilisateur l'a validée. Sinon, arrête-toi et demande.
3. Liste en français : (a) tes **hypothèses**, (b) tes **questions bloquantes** (5 max, avec 2–3 options + ta recommandation), (c) les **points à vérifier** dans les documentations officielles (APIs, quotas, CGU).
4. Propose un **plan court** : fichiers à créer/modifier, ordre, tests à écrire, règles RGPD/sécurité touchées.
5. **N'écris pas de code avant que l'utilisateur ait répondu aux questions bloquantes** et validé le plan.
6. Crée la branche `part-NN-nom-court` quand le plan est validé.
