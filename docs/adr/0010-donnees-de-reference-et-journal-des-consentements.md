# ADR 0010 — Données de référence versionnées et journal des consentements

- **Statut** : accepté (choix par défaut pris en autonomie, partie 2 ; à confirmer)
- **Date** : 2026-11-28
- **Contexte** : le questionnaire s'appuie sur une liste de secteurs → codes NAF (`data/naf_mapping.json`) et les consentements doivent être **prouvables** (qui, quoi, quand, quelle version du texte). Il faut aussi garantir que sans accord, aucune IA n'est appelée.
- **Options** :
  - *Où vivent secteurs et textes d'information* : (a) en base ; (b) en fichiers JSON versionnés dans `data/`, validés au démarrage ; (c) en dur dans le front. → (b) : relisable en pull request, une seule source (le front lit l'API), un fichier invalide empêche le démarrage.
  - *Image Docker* : le fichier est hors de `apps/api`. (a) dupliquer le fichier ; (b) contexte de build = racine du dépôt. → (b) (`docker build -f apps/api/Dockerfile .`), aucune duplication.
  - *Consentement* : (a) un booléen dans `user_profile` ; (b) journal en ajout seulement dans `consents`, le booléen n'étant qu'une copie. → (b) : preuve + historique des retraits ; la garde lit le journal.
  - *Texte vu = texte accepté* : le serveur refuse (409) un accord portant sur une version du texte qui n'est plus en vigueur.
- **Décision** : (b) pour les trois premiers points, plus la règle de version.
- **Conséquences** : `GET /reference/sectors` et `/reference/consent-texts` sont publics (aucune donnée personnelle). Changer un texte = changer sa `version` dans `data/consent_texts.json` : les accords existants restent liés à l'ancienne version. Les futures fonctions IA doivent appeler `require_ai_consent` (`services/ai_guard.py`). Aucun consentement « entraînement de modèle » n'existe (ADR 0007) et le serveur refuse tout autre type que `privacy_notice` et `ai_assist`.
- **À vérifier** : relecture de `naf_mapping.json` (statut « brouillon ») par l'utilisateur ; textes à faire relire par un juriste (partie 14) ; ré-affichage et nouvel accord à demander quand une version change (non implémenté).
