# ADR 0003 — Le CV n'est pas stocké : seul le profil structuré validé est conservé

- **Statut** : accepté (27 nov. 2026)
- **Contexte** : le CV contient des données personnelles, parfois sensibles, et potentiellement de mineurs ; il faut pourtant réutiliser le profil à chaque recherche.
- **Options** : A profil validé seul ; B profil + PDF ; C profil + texte nettoyé.
- **Décision** : option A.
- **Conséquences** : traitement en mémoire ; écran de validation obligatoire ; profil versionné (3 versions max ou 90 jours) ; pas de re-parse possible depuis le fichier d'origine (l'étudiant redépose son CV pour une mise à jour) ; schéma sans champs identifiants ; tests de non-stockage.
