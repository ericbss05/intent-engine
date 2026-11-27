# Partie 4 — Anonymisation (module du backend) + mesure (≈ 4 j) — porte P4

## Contexte
Partie 3 validée. Lis `docs/adr/0002`, `docs/06` (Anonymizer), `docs/07` (porte P4), `docs/04` (R1, R11, R12), `docs/08` §8 et §8.bis.

## Tâche
1. Interface `Anonymizer` + implémentation : règles (emails, téléphones, URLs, codes postaux) + **Presidio** + **spaCy (modèle français)** ; vérifier les versions/licences et le **poids** des modèles sur l'hébergeur (si trop lourd pour le plan retenu, le signaler avec options).
2. Pipeline : texte extrait → suppression de sections → anonymisation → **aperçu pour l'étudiant** de ce qui serait envoyé (écran dédié).
3. Script de **mesure** : sur les CV de test annotés, taux de détection par type (noms, emails, téléphones, adresses) ; sortie dans un rapport Markdown reproductible.
4. Test de contrat : le texte sorti ne contient aucune des PII annotées dans les cas détectés ; rapport des **non-détectées**.

## Contraintes
- **Aucun envoi à un LLM dans cette partie.**
- Ne jamais stocker ni logger le texte (avant ou après anonymisation).
- Fixer le **seuil de la porte P4 avant de mesurer** (proposer 95 % noms/emails/téléphones ; adresses à discuter) et l'écrire dans le rapport.
- Rappeler dans le rapport : pseudonymisation ≠ anonymisation (le texte reste une donnée personnelle).

## Sorties attendues
Module `adapters/anonymizer`, écran d'aperçu, script de mesure, `docs/evaluation-anonymisation.md`, ADR si choix de modèle spaCy/Presidio structurant, `docs/reports/part-04.md` indiquant **porte P4 ouverte ou fermée**.

## Critères de terminé
- [ ] Mesures publiées ; décision de la porte P4 documentée.
- [ ] Aperçu étudiant fonctionnel ; mode sans IA inchangé et testé.

## Questions à poser avant de coder
Seuil P4 ; types d'adresses à traiter ; contraintes de taille de l'image Docker.

## Hors périmètre
Appel LLM, profil assisté (partie 5).
