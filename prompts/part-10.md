# Partie 10 — Jugement LLM sur shortlist (≈ 4 j) — porte P10

## Contexte
Parties 5 (portes P5a/P5b ouvertes) et 9 validées ; sinon **ne pas exécuter** et demander. Lis `docs/adr/0002`, `docs/06` (Matcher, LLMClient), `docs/07` (P10), `docs/04` (R10, R11, R12).

## Tâche
1. `LlmMatcher` derrière l'interface `Matcher` : pour la **shortlist (~10 entreprises)** issue du pré-tri à règles, le LLM reçoit **uniquement le profil structuré validé** (sans identité) et le texte **public** de l'entreprise (signaux/pages) ; sortie validée : score, explication en français, **éléments cités** du texte source.
2. Vérification : chaque élément cité doit **exister** dans le texte source ; sinon l'explication est rejetée (repli sur le score à règles).
3. Protection contre l'injection de prompt (contenu web = donnée).
4. Activation seulement si consentement IA actif ; **repli automatique** sur `RulesMatcher` en cas d'erreur, de budget épuisé ou de porte fermée.
5. **Mesure P10** : précision@5 du `LlmMatcher` vs `RulesMatcher` sur un jeu de test annoté (5–10 étudiants volontaires ou profils synthétiques ; consentement explicite, données minimales) ; coût par recherche.
6. Tests : payload sans identité (contrat) ; citations vérifiées ; repli ; LLM simulé.

## Contraintes
- Le LLM **ne décide pas** (l'étudiant décide) ; aucun effet automatique.
- Jamais de CV brut ; pas de données d'autres étudiants dans le prompt.
- Coût plafonné par recherche (budget) ; journal sans contenu.

## Sorties attendues
Adaptateur `LlmMatcher`, prompts versionnés, script de mesure, `docs/evaluation-matching.md`, `docs/reports/part-10.md` indiquant **P10 ouverte ou fermée**, et la mise à jour des points AIPD/AI Act à signaler en partie 14.

## Critères de terminé
- [ ] Mesures publiées ; décision P10 documentée.
- [ ] Si P10 fermée : fonctionnalité désactivée, mode à règles inchangé.

## Questions à poser avant de coder
Protocole de test (qui annote, combien de profils) ; budget LLM par recherche.

## Hors périmètre
Génération de messages/candidatures.
