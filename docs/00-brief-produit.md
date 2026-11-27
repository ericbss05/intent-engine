# 00 — Brief produit

## Résumé
Service web pour **étudiants français** cherchant un stage ou une alternance. L'étudiant dépose son **CV (PDF, obligatoire)** et remplit un **questionnaire**. Le service lance des **recherches récurrentes** (tous les 1, 2 ou 3 jours, quota par exécution fixé par l'admin) qui trouvent des entreprises, les **classent avec une explication**, et proposent « Voir le contact » (contact RH + email vérifié, **recherché à la demande seulement**) ou « Ignorer ». **Aucun envoi automatique.**

## Utilisateurs
- **Étudiant** : cherche des entreprises adaptées, veut comprendre pourquoi elles lui sont proposées, garde la décision.
- **Admin** (le propriétaire du projet) : règle quotas, fréquences, cascades de fournisseurs, budgets ; surveille coûts et échecs.

## Parcours étudiant
1. Inscription (Clerk) → case **18 ans minimum** → information RGPD → choix **analyse du CV assistée par IA** (optionnel, décoché) ou **simple**.
2. Questionnaire : contrat (stage/alternance) et durée, métier visé, secteurs, zone (code postal/département + rayon), taille d'entreprise ; optionnels : priorités, entreprises déjà contactées (exclusion).
3. Dépôt du CV → extraction **en mémoire** → (si IA : anonymisation + aperçu) → **écran de validation** (corriger/ajouter/retirer les compétences et infos détectées) → profil structuré **versionné** sauvegardé. Le PDF n'est jamais conservé.
4. Création d'une **recherche** (fréquence 1/2/3 jours ; quota imposé par l'admin).
5. Réception de la liste classée : pour chaque entreprise, score + **explication** ; actions « Voir le contact », « Ignorer ».
6. « Voir le contact » → déclenche la recherche du contact RH et la vérification de l'email → affichage avec provenance (publié/inféré/fournisseur) et statut de vérification.
7. À tout moment : pause/suppression d'une recherche, modification des préférences, **export** et **suppression** du compte.

## Admin
Page protégée par rôle : quotas et fréquences (global + exceptions par utilisateur), ordre et activation des fournisseurs, budget mensuel par fournisseur, tableau de bord coûts/échecs, journal des changements.

## Périmètre (dans le projet)
Compte, questionnaire, CV → profil validé, découverte SIRENE, scoring à règles explicable, recherches récurrentes, enrichissement (site web, lecture de pages, contacts, emails), admin, évaluation chiffrée, conformité, démo. **Couche IA conditionnelle** : anonymisation, profil structuré assisté, jugement LLM sur shortlist (portes de décision).

## Hors périmètre (ne pas faire)
- Suivi des candidatures (contacté/réponse/entretien/refus) — **retiré** ; seul un statut minimal par entreprise (proposée/vue/ignorée) existe.
- Envoi automatique d'emails ou de candidatures, génération de séquences d'emails.
- ML d'entraînement (aucun modèle appris pour l'instant).
- Saisie manuelle des compétences à la place du CV (le CV est obligatoire).
- Collecte derrière un login, contournement de CAPTCHA, scraping de moteurs de recherche.
- Entreprises individuelles (exclues par défaut — risque données personnelles SIRENE).
- Application mobile, paiement, multi-pays.

## Principes produit
- **Explicabilité** : chaque classement est justifié ; reproductible.
- **Honnêteté** : « introuvable » plutôt qu'inventé ; statut « catch-all » jamais présenté comme vérifié.
- **Sobriété** : petits quotas, recherche d'email à la demande, minimisation des données.
- **Contrôle** : l'étudiant peut tout corriger, exporter, supprimer.

## Mesures de succès (produit)
Activation (profil validé), délai jusqu'au premier résultat, part des résultats consultés, part des contacts demandés, pertinence perçue des 5 premières suggestions (test avec 5–10 étudiants).

## Décisions encore ouvertes (à demander à l'utilisateur au bon moment)
- Nom du projet et du dépôt ; hébergeur UE du backend (partie 0).
- Fournisseur LLM et éligibilité à la rétention zéro/région UE (partie 5, **avant** de coder).
- Seuil de détection de l'anonymisation (partie 4).
- Ordre Hunter.io / Apollo après test (partie 11) ; accès API gratuit à confirmer.
- Responsable de traitement (utilisateur ou école) ; relecteur juridique (partie 14).
- Offres réelles via sources officielles (France Travail, La bonne alternance : à instruire).
