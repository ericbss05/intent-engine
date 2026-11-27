---
description: Contrôle RGPD/sécurité du code en cours
---

Fais une revue RGPD et sécurité de l'état actuel du dépôt (ou de la branche en cours).

1. Parcours `docs/04-regles-rgpd-pour-le-code.md` règle par règle (R1 à R17) et indique pour chacune : **respectée / non applicable à ce stade / violée**, avec le fichier ou le test qui le prouve.
2. Cherche dans le code : stockage ou log de contenu de CV, champs interdits, requêtes sans `user_id`, secrets en dur, appels sortants sans respect de `robots.txt`, envoi d'emails, appels LLM avec données non anonymisées, traceurs tiers.
3. Liste les écarts par gravité et propose une correction (sans l'appliquer sans accord si elle change l'architecture).
4. Rappelle les points qui nécessitent un avis juridique (voir `docs/08-analyse-rgpd.md`, section « Points ouverts »).
