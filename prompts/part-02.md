# Partie 2 — Questionnaire et consentements (≈ 3 j)

## Contexte
Partie 1 validée. Lis `docs/00-brief-produit.md` (parcours), `docs/03`, `docs/04` (R12, R13, R17), `docs/08` §3 et §5.

## Tâche
1. Parcours d'inscription en étapes : information RGPD (texte clair en français) → 18+ → **choix IA** (« analyse du CV assistée par IA » vs « analyse simple »), **décoché par défaut**, journalisé dans `consents` avec la version du texte.
2. Questionnaire : contrat (stage/alternance) et durée, métier visé, secteurs, zone (code postal/département + rayon), taille d'entreprise ; optionnels : priorités, entreprises déjà contactées (liste d'exclusion).
3. Table `search_preferences` (+ migration), validation **Pydantic côté backend** et **Zod côté front**.
4. Fichier `data/naf_mapping.json` : secteurs affichés → codes NAF ; proposer une première liste (~15–20 secteurs) et la **faire relire par l'utilisateur** avant de la figer.
5. Écran de modification des préférences ; retrait du consentement IA possible à tout moment.

## Contraintes
- Aucun consentement « entraînement de modèle » (hors périmètre, ADR 0007).
- Textes d'information : version simple, à relire (juriste en partie 14).
- Pas d'appel externe.

## Sorties attendues
Migration, routes `/me/preferences`, `/me/consents`, pages front, `data/naf_mapping.json`, tests, `docs/reports/part-02.md`.

## Critères de terminé
- [ ] Préférences sauvegardées, validées côté serveur, modifiables.
- [ ] Consentement IA décoché par défaut, journalisé, retirable ; test : sans consentement, aucun appel IA possible (garde en place pour la suite).
- [ ] Table NAF relue et validée par l'utilisateur.

## Questions à poser avant de coder
Liste des secteurs ; format de la zone (rayon en km ?) ; textes d'information.

## Hors périmètre
CV, recherches, scoring.
