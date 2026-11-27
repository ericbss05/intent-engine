# ADR 0005 — Entreprises individuelles exclues par défaut

- **Statut** : accepté (27 nov. 2026)
- **Contexte** : dans SIRENE, une entreprise individuelle est une personne physique ; son statut de diffusion peut être partiel (nom, adresse masqués à sa demande) ; l'ancienne « non-diffusibilité » a été convertie en diffusion partielle (pas de redistribution intégrale ni de prospection).
- **Décision** : exclure les entreprises individuelles de la découverte ; respecter le statut de diffusion le plus récent ; ne jamais reconstituer une adresse masquée ; rafraîchir le statut à chaque mise à jour de fiche.
- **Conséquences** : test dédié ; filtre ajouté à `CompanyDiscovery` ; mention de la source (Licence Ouverte 2.0).
