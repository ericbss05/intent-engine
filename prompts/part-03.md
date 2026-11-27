# Partie 3 — Extraction du CV + parseur à règles (≈ 4 j)

## Contexte
Partie 2 validée. Lis `docs/06` (CvParser, CvProfile), `docs/04` (R1, R2), `docs/07` (CV de test), `docs/adr/0003`. Ce parseur est la **référence** à battre par l'IA (parties 4–5) et le **mode de repli**.

## Tâche
1. Upload CV : ≤ 4 Mo, type MIME **et** signature (`%PDF`) vérifiés, **traitement en mémoire** (aucune écriture disque), timeout de parsing, PDF scanné/sans texte refusé avec message clair.
2. Extraction de texte avec une bibliothèque Python (pdfplumber ou PyMuPDF : comparer sur 3 CV, justifier, **vérifier la licence**).
3. Suppression de sections inutiles (loisirs, associatif, informations personnelles) par détection de titres.
4. Détection : compétences via `data/skills_dictionary.json` (~200 termes + synonymes, à créer et faire relire), langues, dates, certifications (regex).
5. **Écran de validation** : l'étudiant corrige, ajoute, retire ; formation et expériences montrées en texte pour confirmation.
6. Sauvegarde du **seul profil validé** dans `cv_profiles` (versionné ; purge au-delà de 3 versions ou 90 jours).
7. 10 CV de test **synthétiques** + fichiers `.expected.json` (voir `docs/07`).
8. Tests : rappel des compétences sur les 10 CV ; **test de non-stockage** (ni fichier, ni ligne en base, ni log ne contient le texte du CV) ; PDF scanné refusé.

## Contraintes
- Schéma sans champ identifiant (nom, email, téléphone, adresse, photo, date de naissance).
- Ne jamais logger le texte du CV.
- Interface `CvParser` respectée (remplaçable).
- Aucun appel IA dans cette partie.

## Sorties attendues
Adaptateur `cv`, migration `cv_profiles`, routes, écran de validation, `data/skills_dictionary.json`, `data/eval/cv/*`, tests, `docs/reports/part-03.md` (avec le **rappel mesuré** ; objectif de départ ≈ 80 %, à mesurer sans l'embellir).

## Critères de terminé
- [ ] Rappel mesuré et publié dans le rapport.
- [ ] Test de non-stockage vert.
- [ ] L'écran de validation permet de corriger toutes les détections.

## Questions à poser avant de coder
Choix pdfplumber/PyMuPDF ; liste du dictionnaire ; niveau de détail des expériences affichées.

## Hors périmètre
Anonymisation, LLM, recherches.
