# Partie 5 — LLMClient + profil structuré assisté (≈ 5 j) — portes P5a et P5b

## Contexte
Partie 4 validée (**porte P4 ouverte**, sinon n'exécute pas cette partie : demande à l'utilisateur). Lis `docs/adr/0002`, `docs/06` (LLMClient), `docs/07` (P5a, P5b), `docs/04` (R11, R12), `docs/08` §8.

## Tâche
1. **Avant tout code (P5a)** : avec l'utilisateur, comparer 2–3 fournisseurs (candidats : Mistral, OpenAI région UE ; autres si pertinents) sur : DPA, région UE, **rétention zéro réellement disponible pour son compte**, pas d'entraînement, coût, qualité en français. Lire les **documentations officielles actuelles** ; ne rien affirmer de mémoire. Si aucun fournisseur éligible : proposer le repli (modèle auto-hébergé ou option IA fermée) et **s'arrêter**.
2. Interface `LLMClient.structured(...)` : sortie validée par un schéma Pydantic ; journal d'appel **sans contenu** (modèle, version, durée, coût) ; garde : aucun appel sans consentement IA actif ; aucun appel hors fonction `purpose` autorisée.
3. Prompt d'extraction du profil structuré à partir du **texte anonymisé** ; protection contre l'injection (le CV est une donnée, jamais une instruction) ; sortie → `CvProfile` brouillon → **même écran de validation** que la partie 3.
4. Parcours : l'étudiant voit l'aperçu de ce qui est envoyé, choisit « analyse assistée » ou « simple » ; le mode simple reste complet.
5. **Mesure (P5b)** : rappel des compétences assisté vs règles sur les 10 CV ; coût par CV.
6. Tests : le payload envoyé ne contient ni nom/email/téléphone (test de contrat) ; sans consentement, aucun appel ; sorties invalides gérées ; LLM simulé dans les tests (aucun appel réseau).

## Contraintes
- Jamais le CV brut ; jamais de données personnelles non anonymisées ; pas d'envoi automatique de quoi que ce soit.
- Le LLM ne décide pas : l'étudiant valide.
- Clés d'API en variables d'environnement uniquement.

## Sorties attendues
Adaptateur `llm`, prompts versionnés dans le dépôt, écrans, `docs/evaluation-profil-assiste.md`, ADR du fournisseur retenu (`docs/adr/`), `docs/reports/part-05.md` indiquant **P5a et P5b ouvertes ou fermées** et les risques (AIPD, AI Act).

## Critères de terminé
- [ ] Décision P5a documentée (fournisseur ou repli).
- [ ] Si P5b fermée, le mode assisté est désactivé par défaut et le dit clairement.
- [ ] Mode sans IA testé et fonctionnel.

## Questions à poser avant de coder
Fournisseur ; budget mensuel LLM ; langues des CV supportées.

## Hors périmètre
Jugement de pertinence sur les entreprises (partie 10).
