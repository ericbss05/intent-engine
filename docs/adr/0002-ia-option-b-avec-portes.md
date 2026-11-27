# ADR 0002 — IA : règles + anonymisation locale + LLM à rétention zéro, avec portes de décision

- **Statut** : accepté (27 nov. 2026)
- **Contexte** : pour un classement pertinent, comparer profil et entreprise exige plus que des règles ; mais envoyer un CV complet à un tiers est le risque RGPD principal.
- **Options** : A tout à règles ; B hybride (anonymisation locale + LLM rétention zéro UE) ; C modèle auto-hébergé.
- **Décision** : B, **conditionnée** par des portes mesurées (`docs/07-evaluation.md`) ; le **mode sans IA reste complet** ; C en repli si aucun fournisseur éligible.
- **Conséquences** : interfaces `Anonymizer`, `LLMClient`, `Matcher` ; consentement séparé décoché par défaut ; AIPD complète et note AI Act avant lancement ; fournisseur LLM = sous-traitant à documenter (DPA, région UE, rétention zéro **confirmée sur le compte réel**) ; le LLM ne reçoit que du texte anonymisé ou le profil structuré validé ; il ne décide jamais (l'étudiant décide).
- **Risques** : détection imparfaite (pseudonymisation ≠ anonymisation) ; réidentification indirecte ; éligibilité à la rétention zéro incertaine ; AI Act (domaine « recrutement ») à faire valider.
