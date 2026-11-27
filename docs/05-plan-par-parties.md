# 09 — Plan de développement v2 (27 nov. 2026) : 16 parties à valider une par une

> Ce n'est plus un MVP : c'est un projet complet, avec IA encadrée. Architecture retenue : **option B** (règles + anonymisation locale + LLM à rétention zéro, région UE, mode sans IA toujours disponible). Cadre juridique : `08-analyse-rgpd.md`. Je ne suis pas juriste.
> **Architecture tranchée le 27 nov. : front Next.js (TypeScript) + backend Python complet (FastAPI).** Raisons : le projet est surtout du traitement de texte/données (CV, anonymisation, scoring, scraping), les meilleurs outils sont en Python, et le backend Python est un atout de CV. Coût assumé : deux langages, deux déploiements (≈ +4 jours).
> **Unités** : les durées sont en **jours de travail effectif (≈ 6 h)**, mes estimations pour quelqu'un qui apprend en codant avec Claude Code. Correction par rapport à la v1 : j'avais écrit « 8–11 semaines à ~10 h/semaine », c'était faux (c'était un temps plein). Voir « Calendrier ».

## Résumé

- **16 parties (0 à 15)**. Chacune a un objectif, des technologies, des livrables, une **définition de terminé** et un **point de validation** : on ne passe à la suivante qu'après ton accord.
- **Cœur sans IA** (parties 0–2, 6–9, 11–15) puis **couche IA** (parties 3–5 et 10) activée seulement si elle passe ses « portes de décision » (mesures chiffrées).
- **Architecture** : front **Next.js** (pages uniquement, sur Vercel) + **backend Python FastAPI** (API, pipeline, anonymisation Presidio/spaCy, tâches Inngest) hébergé en **UE**, base Neon (Frankfurt). C'est du traitement de texte, pas du ML d'entraînement.
- **Total ≈ 66 jours de travail effectif** (≈ 49 j pour le cœur sans IA). À 10 h/semaine : ≈ 9 mois ; à 20 h/semaine : ≈ 4,5 mois ; à 30 h/semaine : ≈ 3 mois.
- **Premier pas** : Partie 0 (5 jours) — il me faut seulement tes comptes GitHub, Vercel, Clerk et Neon.

## Stack (rappel, expliquée)

| Brique | C'est quoi | Rôle |
|---|---|---|
| TypeScript | JavaScript avec des types | Langage principal |
| Next.js (App Router) | Framework React | Front uniquement (pages, formulaires) |
| Tailwind + shadcn/ui | Styles + composants prêts | Interface |
| Clerk | Service d'authentification | Comptes, rôle admin |
| PostgreSQL (Neon, Frankfurt) | Base relationnelle serverless | Données |
| SQLAlchemy 2 + Alembic | ORM Python (requêtes) + migrations | Schéma versionné, côté backend |
| Pydantic (backend) + Zod (front) | Validation de données | API, sorties du LLM (Pydantic) ; formulaires (Zod) |
| Inngest | Tâches en arrière-plan (retries, planification) ; SDK Python à vérifier | Recherches récurrentes |
| SSE | Le serveur pousse des événements au navigateur | Progression en direct |
| Vitest (front) + pytest (backend) | Tests | Qualité |
| GitHub Actions | Tests automatiques | CI |
| **Python 3.12 + FastAPI** | Framework d'API web en Python | Tout le backend |
| **Presidio + spaCy (fr)** | Détection/masquage d'informations personnelles | Anonymisation du CV |
| Docker | Conteneur pour déployer le service Python | Déploiement |
| LLM via `LLMClient` | Modèle de langage, derrière une interface | Profil structuré, jugement sur shortlist |

### Services externes et plans B (cascades, du moins cher au plus cher)

| Besoin | Cascade (on s'arrête au premier résultat fiable) | Partie |
|---|---|---|
| Entreprises | API Recherche d'entreprises (SIRENE) → API INSEE Sirene | 6 |
| Site web, téléphone | Bright Data (Google Maps) → domaine deviné + contrôle DNS/HTTP | 9 |
| Lecture des pages | Firecrawl → requête HTML simple | 9 |
| **Contact RH** | Pages équipe/carrières → mentions légales/contact → registre (dirigeants, limité) → **Hunter.io** → **Apollo** | 11 |
| **Email** | Email publié → motif inféré (3 candidats max) → **Hunter.io** → **Apollo** → vérification | 11 |
| Vérification d'email | Syntaxe + MX (interne) → ZeroBounce (endpoint UE) → Reoon | 11 |

Hunter.io et Apollo sont des **plans B payants à crédits** (Hunter : environ 50 crédits gratuits par mois, partagés entre recherche et vérification ; accès API gratuit d'Apollo à confirmer). Ce sont aussi des fournisseurs de données personnelles : provenance enregistrée, email revérifié avant usage, cascade et budget par fournisseur réglables depuis l'admin (partie 12).

Interfaces (chaque source externe est remplaçable) : `CvParser`, `Anonymizer`, `LLMClient`, `Matcher`, `CompanyDiscovery`, `WebsiteFinder`, `PageFetcher`, `ContactFinder`, `EmailVerifier`.

## Vue d'ensemble

| # | Partie | Effort | Dépend de | Type |
|---|---|---|---|---|
| 0 | Fondations du dépôt (front + backend) | 5 j | — | Cœur |
| 1 | Compte, base, isolation, droits | 4 j | 0 | Cœur |
| 2 | Questionnaire et consentements | 3 j | 1 | Cœur |
| 3 | Extraction du CV + parseur à règles (référence) | 4 j | 2 | Cœur |
| 4 | Anonymisation (service Python) + mesure | 5 j | 3 | IA (porte) |
| 5 | `LLMClient` + profil structuré assisté | 5 j | 4 | IA (porte) |
| 6 | Découverte SIRENE + cache partagé | 4 j | 1 | Cœur |
| 7 | Scoring à règles + liste de résultats | 4 j | 3, 6 | Cœur |
| 8 | Recherches récurrentes + orchestration | 5 j | 7 | Cœur |
| 9 | Site web + lecture des pages | 5 j | 8 | Cœur |
| 10 | Jugement LLM sur shortlist | 4 j | 5, 9 | IA (porte) |
| 11 | Contacts et emails à la demande | 5 j | 9 | Cœur |
| 12 | Admin, coûts, observabilité | 3 j | 8 | Cœur |
| 13 | Évaluation chiffrée | 3 j | 7, 9, 11 | Cœur |
| 14 | Conformité appliquée + relecture juridique | 4 j | toutes | Cœur |
| 15 | Finition, démo, portfolio | 3 j | 14 | Cœur |

Option à instruire en parallèle (partie 6b) : **offres réelles** via sources officielles (API France Travail, La bonne alternance — à confirmer) pour ne pas se limiter aux entreprises.

---

## Partie 0 — Fondations du dépôt, front + backend (5 j)
**Objectif** : dépôt propre, deux applications déployées, CI verte.
**Technos** : un seul dépôt (« monorepo ») avec `apps/web` (Next.js + TypeScript strict, Tailwind, shadcn/ui, pnpm, ESLint/Prettier, Vitest) et `apps/api` (Python 3.12, FastAPI, uv pour les dépendances, ruff pour le style, pytest, Docker) ; GitHub Actions ; Vercel pour le front ; hébergeur **UE** pour le backend (Scaleway, OVHcloud, Render EU ou Fly Paris : à comparer) ; variables d'environnement validées (Zod côté front, Pydantic côté backend) ; scan de secrets GitHub ; CORS et clé d'API entre front et backend.
**Livrables** : dépôt, déploiement du front et du backend, CI (lint + tests des deux), `docs/adr/` (une page par décision), README initial.
**Terminé quand** : un push sur `main` lance les tests des deux applications puis les déploie, et le front appelle un point de santé du backend.
**À valider ensemble** : nom du dépôt, structure des dossiers, hébergeur du backend, plan Vercel (usage non commercial ?).

## Partie 1 — Compte, base, isolation, droits (4 j)
**Objectif** : un utilisateur crée un compte et ne voit que ses données.
**Technos** : Clerk (rôle admin ; le backend vérifie le jeton de connexion), Neon (région Frankfurt), SQLAlchemy 2 + Alembic (tables `user_profile`, `consents`), couche d'accès aux données exigeant `user_id`, test d'isolation.
**Livrables** : webhook Clerk, **bouton « Supprimer mon compte »** (cascade) et **« Exporter mes données » (JSON)**, page admin protégée.
**Terminé quand** : test d'isolation vert ; suppression de compte testée de bout en bout.
**À valider** : schéma des tables, méthode de protection admin.

## Partie 2 — Questionnaire et consentements (3 j)
**Objectif** : l'étudiant décrit sa recherche et donne (ou non) ses accords.
**Technos** : React Hook Form + Zod, shadcn/ui, table `search_preferences`.
**Contenu** : contrat et durée, métier, secteurs (→ NAF), zone, taille, entreprises déjà contactées ; mention d'information RGPD ; 18+ ; **choix « analyse du CV assistée par IA » vs « analyse simple »** (consentement séparé, décoché par défaut) ; consentement d'entraînement : **supprimé** (pas de ML dans ce projet).
**Livrables** : parcours en étapes, table secteur → NAF relue à la main.
**Terminé quand** : préférences validées côté serveur, modifiables, consentements journalisés.
**À valider** : liste des secteurs, textes d'information.

## Partie 3 — Extraction du CV + parseur à règles (4 j)
**Objectif** : PDF → profil validé, sans stockage ; sert de **référence** pour mesurer l'IA.
**Technos** : pdfplumber ou PyMuPDF (extraction de texte PDF en Python, avec timeout), dictionnaire de compétences (~200 termes + synonymes, JSON versionné), regex (langues, dates, certifications), interface `CvParser`, modèle Pydantic `CvProfile`, table `cv_profiles` versionnée.
**Étapes** : upload ≤ 4 Mo, type vérifié, **traitement en mémoire** → extraction → suppression des sections inutiles (loisirs, associatif, infos personnelles) → détection → **écran de validation** → sauvegarde du seul profil.
**Livrables** : 10 CV de test annotés à la main (matière première des parties 4, 5 et 13), tests de non-régression, test prouvant que ni PDF ni texte brut ne sont stockés ou loggés.
**Terminé quand** : rappel des compétences mesuré sur les 10 CV (objectif de départ ≈ 80 %).
**À valider** : la liste du dictionnaire, l'écran de validation.

## Partie 4 — Anonymisation (module du backend Python) + mesure (4 j) — *porte de décision*
**Objectif** : masquer les informations identifiantes avant tout envoi à un LLM.
**Technos** : Presidio (détection/masquage), spaCy (modèle français), regex (emails, téléphones, URLs), interface `Anonymizer`, dans le backend FastAPI (même hébergeur UE, plus de service séparé ni d'authentification entre services).
**Livrables** : module déployé, **aperçu pour l'étudiant** de ce qui serait envoyé, rapport de mesure (taux de détection par type : noms, adresses, contacts) sur les 10 CV annotés.
**Porte** : seuil de détection fixé **avant** de mesurer (proposition : ≥ 95 % sur noms/contacts ; à discuter) ; en dessous, l'option IA sur CV reste fermée.
**Risques** : réidentification indirecte, données « sensibles » non détectables (d'où la suppression de sections) ; un hébergeur de plus à documenter.
**À valider** : hébergeur, seuil.

## Partie 5 — `LLMClient` + profil structuré assisté (5 j) — *porte de décision*
**Objectif** : que le LLM construise le profil structuré à partir du CV anonymisé, l'étudiant validant.
**Technos** : interface `LLMClient`, sortie structurée Zod, journal des appels **sans contenu** (modèle, version, durée, coût), garde contre l'injection de prompt.
**Préalable bloquant** : **fournisseur confirmé sur ton compte** pour rétention zéro + région UE + DPA lu + pas d'entraînement. Candidats à instruire : Mistral, OpenAI (région UE, projets éligibles). Sinon repli : modèle auto-hébergé ou option désactivée.
**Livrables** : mode « analyse assistée » dans le parcours CV, mode « simple » toujours disponible, comparaison chiffrée assisté vs règles sur les 10 CV.
**Porte** : le mode assisté **bat** la référence (partie 3) sur le rappel des compétences, sinon il n'est pas activé.
**À valider** : fournisseur, résultats de comparaison.

## Partie 6 — Découverte SIRENE + cache partagé (4 j)
**Objectif** : des entreprises candidates réelles à partir des préférences.
**Technos** : API Recherche d'entreprises via `CompanyDiscovery` (secours : API INSEE Sirene), table partagée `companies` (clé SIREN, `source`, `fetched_at`, TTL, statut `pending/ready/stale/failed`), Zod sur les réponses, retries et limites de débit, tests avec réponses enregistrées.
**Règles RGPD** : **exclure les entreprises individuelles** par défaut, respecter le statut de diffusion, ne jamais reconstituer une adresse masquée.
**Terminé quand** : ≥ 50 entreprises plausibles sans doublon, exclusion prouvée par test.
**À valider** : filtres exposés, exclusion des entreprises individuelles.

## Partie 7 — Scoring à règles + liste de résultats (4 j)
**Objectif** : classer et expliquer.
**Technos** : fonction de scoring TypeScript pure (secteur ↔ métier, distance, taille, mots-clés), `search_results` (rang, statut `proposée/vue/ignorée`, `score_breakdown` JSON), interface liste + panneau « Pourquoi ».
**Livrables** : boutons « Ignorer » et « Voir le contact » (inactif jusqu'à la partie 11), exclusion des déjà contactées, déduplication.
**Terminé quand** : score **reproductible** et explicable ; première liste utile sans scraping.
**À valider** : pondérations, présentation de l'explication.

## Partie 8 — Recherches récurrentes + orchestration (5 j)
**Objectif** : relance automatique tous les 1/2/3 jours avec quota.
**Technos** : Inngest (planification, étapes **idempotentes**, concurrence par utilisateur, annulation), SSE + `run_events` (reprise `Last-Event-ID`), tables `searches` et `admin_config` (global + exceptions), journal des changements.
**Règles** : quota et fréquence **fixés par l'admin**, appliqués côté serveur ; budget mensuel global ; pause après ≈ 14 jours d'inactivité ; pause/suppression par l'utilisateur ; aucun envoi automatique.
**Terminé quand** : en simulant le temps, la recherche part à l'heure, respecte son quota, sans doublon même relancée deux fois.
**À valider** : valeurs par défaut de quota et fréquence.

## Partie 9 — Site web + lecture des pages (5 j)
**Objectif** : pour les ~5 entreprises retenues, site, page carrières, signaux.
**Technos** : `WebsiteFinder` (Bright Data → domaine deviné + contrôle DNS/HTTP avec vérification du nom/ville), `PageFetcher` (Firecrawl → HTML simple), `robots.txt` respecté, **disjoncteur** par fournisseur, liste de domaines exclus.
**Principe** : s'arrêter au premier résultat fiable ; provenance et date ; « site introuvable » plutôt qu'invention.
**Risques** : CGU Google/Bright Data (plan B : API Google Places), quotas gratuits.
**Terminé quand** : taux de site correct mesuré sur ≈ 30 entreprises annotées.
**À valider** : fournisseurs retenus après test des comptes.

## Partie 10 — Jugement LLM sur shortlist (4 j) — *porte de décision*
**Objectif** : affiner le classement des ~10 meilleures entreprises.
**Technos** : `Matcher` (règles) et `LlmMatcher` ; le LLM reçoit **uniquement le profil structuré validé** + le texte public de l'entreprise ; sortie Zod (score + explication + éléments cités) ; vérification que les éléments cités existent dans le texte source.
**Porte** : meilleure pertinence que les règles seules sur le test (précision sur les 5 premières), sinon retiré. L'étudiant garde la décision.
**Risques** : réévaluation AI Act et AIPD (voir doc 08).
**À valider** : protocole de test (qui annote, quels critères).

## Partie 11 — Contacts et emails à la demande (5 j)
**Objectif** : au clic « Voir le contact », un contact RH et un email vérifié.
**Technos** : `ContactFinder` en cascade qui s'arrête au premier résultat fiable : (1) pages équipe/carrières, (2) mentions légales/contact, (3) registre (dirigeants, limité), (4) **Hunter.io**, (5) **Apollo** en dernier recours ; disjoncteur par fournisseur ; `EmailVerifier` (syntaxe + MX en interne, puis ZeroBounce endpoint UE, Reoon en secours), provenance `publié | inféré | fournisseur`, revérification des emails de fournisseurs, cache par adresse, table `suppression` (hash).
**Règles** : ordre Hunter/Apollo décidé après test des deux comptes ; pas de téléphone personnel ; « catch-all » jamais présenté comme vérifié.
**Livrables** : bouton actif, page publique d'information des contacts, adresse d'opposition, procédure de suppression.
**Terminé quand** : taux d'emails valides et crédits par clic mesurés.
**À valider** : ordre des fournisseurs, textes publics.

## Partie 12 — Admin, coûts, observabilité (3 j)
**Technos** : pages admin (quotas, ordre et activation des fournisseurs, budgets), requêtes SQL sur `run_events` (coût par recherche, taux d'échec par étape), Sentry optionnel.
**Terminé quand** : tu réponds en 1 minute à « combien cette semaine ? » et « quelle étape échoue le plus ? ».

## Partie 13 — Évaluation chiffrée (3 j)
**Technos** : Vitest, ≈ 30 entreprises et 10 CV annotés, script produisant `docs/evaluation.md`.
**Métriques** : site correct, rappel des compétences (règles vs assisté), détection d'anonymisation, emails valides, pertinence des 5 premières suggestions (test avec 5–10 étudiants), échec par étape, coût par recherche.

## Partie 14 — Conformité appliquée + relecture juridique (4 j)
**Livrables** : politique de confidentialité, page contacts, registre des traitements, registre des sous-traitants et DPA (dont service Python et fournisseur LLM), test de mise en balance, **AIPD complète** (profilage + LLM), note d'applicabilité AI Act, job de purge (inactivité 12 mois, TTL des contacts) testé, procédure de violation (72 h), contrôle des cookies, **relecture par un juriste ou le DPO de l'école**.
**Terminé quand** : chaque ligne P0/P1 de `08-analyse-rgpd.md` renvoie à une preuve.

## Partie 15 — Finition, démo, portfolio (3 j)
**Livrables** : README avec schéma, ADR, vidéo de 2 min, données de démo, page « décisions et limites », test avec 5 étudiants BSB, déploiement.

---

## Calendrier

| Rythme | Durée totale (≈ 66 j) | Cœur sans IA (≈ 49 j) |
|---|---|---|
| 10 h/semaine | ≈ 9 mois | ≈ 6,5 mois |
| 20 h/semaine | ≈ 4,5 mois | ≈ 3,3 mois |
| 30 h/semaine | ≈ 3 mois | ≈ 2,2 mois |

Pour accélérer sans perdre l'essentiel : faire le cœur (parties 0–3, 6–9, 11–15) d'abord, puis la couche IA (4, 5, 10) si les portes sont franchies.

## Risques principaux (à tester tôt)
1. Parsing CV (partie 3) et qualité de l'anonymisation (partie 4).
2. Éligibilité d'un fournisseur LLM à la rétention zéro (partie 5) : à vérifier **avant** de coder.
3. Trouver le site web (partie 9) et fiabilité des emails (partie 11).
4. Pertinence perçue du classement (partie 7) : testable tôt avec des étudiants.

## Questions ouvertes
1. Rythme réel (h/semaine) et échéance.
2. Hébergeur du backend Python (UE).
3. Seuil de détection de l'anonymisation.
4. Responsable de traitement (toi ou l'école) ; relecteur juridique.
5. Plan Vercel pour un usage non commercial / test avec étudiants.
6. Partie 6b : offres réelles via sources officielles (à instruire).
