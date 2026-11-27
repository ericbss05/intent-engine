# Partie 14 — Conformité appliquée + relecture juridique (≈ 4 j)

## Contexte
Toutes les parties fonctionnelles terminées. Lis `docs/08-analyse-rgpd.md` en entier et `docs/04`. L'utilisateur n'est pas juriste, toi non plus : **prépare** les documents, ne prétends pas à la conformité.

## Tâche
1. **Politique de confidentialité** (Art. 13) claire en français ; **page publique contacts** (Art. 14) ; mentions légales ; adresse d'exercice des droits.
2. **Registre des traitements** (Art. 30) : une ligne par traitement (voir `docs/08` §3).
3. **Registre des sous-traitants** + statut des DPA (Vercel, hébergeur backend UE, Clerk, Neon, Inngest, Firecrawl, Bright Data, ZeroBounce/Reoon, Hunter, Apollo, fournisseur LLM) ; **vérifier les conditions actuelles** de chacun et marquer « à vérifier » ce qui ne l'est pas.
4. **Test de mise en balance** (intérêt légitime) rédigé (1 page) ; **AIPD** complète (profilage + éventuel LLM) avec l'outil PIA de la CNIL ou équivalent ; **note d'applicabilité AI Act** (règles vs LLM) marquée « à valider par un juriste ».
5. **Job de purge** : comptes inactifs 12 mois (préavis 30 j), TTL des contacts, anciennes versions de profil ; test avec simulation du temps.
6. Procédure de **violation de données** (72 h) + registre d'incidents.
7. Contrôle des **cookies/traceurs** réellement déposés ; bannière seulement si nécessaire.
8. Lancer `/rgpd-check` ; produire un tableau « règle → preuve » (liens vers fichiers/tests/pages) pour chaque ligne P0/P1 de `docs/08` §11.
9. Dossier `docs/juridique/` prêt à envoyer au relecteur (juriste ou DPO de l'école) avec la liste des questions ouvertes (responsable de traitement, base légale, AI Act, transferts).

## Contraintes
- Ne pas inventer de références juridiques : citer les sources de `docs/08` ; marquer « à vérifier » le reste.
- Ne pas annoncer « conforme RGPD » : annoncer « conçu pour limiter les risques, relu par … ».

## Sorties attendues
Pages front (politique, contacts, mentions), `docs/juridique/*` (registre, sous-traitants, balance, AIPD, AI Act, violation), job de purge + tests, tableau règle → preuve, `docs/reports/part-14.md`.

## Critères de terminé
- [ ] Chaque ligne P0/P1 de `docs/08` §11 renvoie à une preuve.
- [ ] Dossier juridique transmis au relecteur ; retours intégrés ou consignés.

## Questions à poser avant de coder
Qui est responsable de traitement (utilisateur ou école) ; relecteur choisi ; adresse de contact RGPD.

## Hors périmètre
Nouvelles fonctionnalités.
