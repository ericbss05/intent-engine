# 08 — Analyse RGPD, données et IA du projet « service stage/alternance »

> Date : 26 novembre 2026. Je ne suis pas juriste : ce document est une analyse de conformité « par conception » (privacy by design) à faire valider, avant tout lancement public, par le service juridique/DPO de l'école ou un avocat. Les points non vérifiés sont marqués **[À VÉRIFIER]**.

---

## 0. Résumé (à lire en 1 minute)

**Verdict.** Le projet est faisable de façon conforme *si* on assume trois choix de conception : (1) **minimiser** (on ne stocke ni le PDF du CV, ni photo, ni date de naissance, seulement un profil validé par l'étudiant), (2) **traiter les contacts d'entreprises comme des données personnelles** (un email nominatif de RH en est une, même s'il est public), (3) **garder l'humain décideur** (aucun envoi automatique, le score est une aide, pas une décision).

**Les 6 risques majeurs, par ordre de gravité**

| # | Risque | Réponse de conception |
|---|---|---|
| 1 | Données de contacts (RH) collectées/inférées/achetées sans information des personnes (Art. 14) | Registre des sources, information publique générale + mention au premier contact, liste d'opposition (suppression), email vérifié seulement sur clic |
| 2 | CV = données d'étudiants, parfois sensibles ou de mineurs (16–17 ans en alternance) | CV non conservé, dictionnaire de compétences, pas de champs sensibles, validation par l'étudiant, âge minimum à trancher |
| 3 | Sous-traitants hors UE (Vercel, Clerk, Inngest, Firecrawl, ZeroBounce, Hunter, Apollo, Bright Data) | Registre des sous-traitants, DPA signés/acceptés, région UE quand possible, minimisation des données envoyées |
| 4 | « Entreprises individuelles » dans SIRENE (personne physique, statut de diffusion partielle) | Exclure par défaut ou respecter le statut de diffusion ; ne jamais reconstituer une adresse masquée |
| 5 | Scraping (Google Maps via Bright Data, pages web) : CGU et attentes raisonnables | Privilégier API officielles, respecter robots.txt, liste de sites exclus, plan B légal (API Google Places) si le projet est commercialisé |
| 6 | Profilage (score étudiant/entreprise) + AI Act | Score explicable, règles transparentes, pas de décision automatisée ; AIPD allégée documentée ; positionnement AI Act argumenté (incertain) |

**Les 10 actions à faire en premier** : voir §11 (checklist priorité P0).

**Ce que ça montre à un recruteur** : tu as raisonné produit *et* conformité : minimisation par le schéma, cartographie des flux, analyse des risques, registre, arbitrages documentés (§12).

---

## 1. Périmètre et hypothèses

- **Produit** : l'étudiant dépose son CV (PDF) + répond à un questionnaire ; le service lance des recherches récurrentes (1/2/3 jours, quota fixé par l'admin) et propose des entreprises classées avec explication du score ; « Voir le contact » déclenche la recherche/vérification d'email ; « Ignorer » exclut l'entreprise.
- **Pas d'envoi automatique** de candidatures. Pas de suivi de candidatures dans le MVP.
- **LLM — mise à jour du 27 nov.** : l'architecture retenue est l'**option B** (règles + anonymisation locale + LLM à rétention zéro en UE, mode sans IA disponible), voir §8 et §8.bis. Le cas « sans LLM » (§6) reste le mode de repli. Les conditions du §8 sont obligatoires avant d'activer l'IA.
- **Responsabilité** : toi (ou l'entité qui exploite le service) serais **responsable de traitement** pour les données des étudiants et pour la base de contacts d'entreprises. Si le projet reste un projet académique, il faut quand même le tenir comme un vrai traitement dès qu'il y a de vrais utilisateurs. À clarifier avec l'école si le service est testé auprès d'étudiants BSB **[À VÉRIFIER : qui est responsable de traitement, toi ou l'école ?]**.

---

## 2. Rôles

| Acteur | Rôle RGPD | Remarque |
|---|---|---|
| Toi / structure exploitante | Responsable de traitement | Décide des finalités et moyens |
| Étudiants | Personnes concernées (utilisateurs) | Données collectées directement (Art. 13) |
| Contacts RH / dirigeants | Personnes concernées (données collectées indirectement, Art. 14) | Ne savent pas que tu les as |
| Vercel, Clerk, Neon, Inngest, Firecrawl, ZeroBounce, Bright Data | Sous-traitants (Art. 28) | DPA à avoir pour chacun |
| Hunter, Apollo | Selon les cas, **fournisseurs de données qui sont eux-mêmes responsables de traitement** de leurs bases | Tu récupères des données qu'ils ont collectées ; leur licéité n'est pas la tienne, mais ton utilisation l'est |
| API Recherche d'entreprises / Insee Sirene | Sources publiques (Licence Ouverte) | Contiennent des données de personnes physiques (entrepreneurs individuels) |

---

## 3. Cartographie des données (data map)

| Donnée | Qui | Source | Finalité | Base légale (proposée) | Conservation proposée |
|---|---|---|---|---|---|
| Email, identifiant de compte | Étudiant | Clerk | Authentification | Contrat (Art. 6.1.b) | Durée du compte + suppression à la demande |
| Questionnaire (métier, secteurs, zone, taille, contrat) | Étudiant | Saisie | Recherche d'entreprises | Contrat | Durée du compte |
| **Profil CV validé** (compétences, langues, formation/expériences résumées) | Étudiant | CV parsé + validation | Calcul du score | Contrat | Durée du compte, versionné, purge des anciennes versions |
| Fichier PDF du CV | Étudiant | Upload | Parsing seulement | — | **Non conservé** (supprimé après extraction) |
| Données SIRENE (entreprise) | Entreprises | API publique | Découverte | Intérêt légitime (personnes morales : hors RGPD ; entrepreneurs individuels : voir §7.4) | Rafraîchissement/TTL |
| Contacts RH (nom, poste, email) | Tiers | Pages publiques, Hunter/Apollo | Mise en relation étudiant ↔ entreprise | Intérêt légitime (Art. 6.1.f) + test de mise en balance documenté | TTL court (ex. 6 mois sans usage), suppression sur opposition |
| Statut de vérification d'email | Tiers | ZeroBounce/Reoon | Exactitude | Intérêt légitime | Idem contact |
| Statuts par entreprise (proposée/vue/ignorée) | Étudiant | App | Dédoublonnage | Contrat | Durée du compte |
| Logs techniques, `run_events` | Étudiant | App | Sécurité, diagnostic | Intérêt légitime | 6 mois max (repère CNIL logs, à confirmer) |
| Liste de suppression | Tiers | Demandes d'opposition | Honorer l'opposition | Obligation légale | Tant que nécessaire pour ne pas re-collecter |
| Consentement ML (optionnel) | Étudiant | Case dédiée | Entraînement du modèle sur données anonymisées | **Consentement** (Art. 6.1.a) | Jusqu'au retrait |

---

## 4. Principes RGPD appliqués (Art. 5) — traduction en choix concrets

1. **Licéité, loyauté, transparence** → politique de confidentialité en clair, informations Art. 13 à l'inscription, Art. 14 pour les contacts (§7.1).
2. **Limitation des finalités** → finalités listées (recommander des entreprises ; entraîner un modèle *uniquement avec consentement séparé*).
3. **Minimisation** → schéma sans champs photo, date de naissance, nationalité, situation familiale, santé, adresse exacte, téléphone ; texte brut du CV non stocké.
4. **Exactitude** → vérification d'email, TTL des fiches, statut `stale`.
5. **Limitation de la conservation** → durées définies *à l'avance* (§9).
6. **Intégrité et confidentialité** → mesures de sécurité (§10).
7. **Responsabilité (accountability)** → registre, AIPD, journal des décisions, DPA (§11).

---

## 5. Droits des personnes

**Étudiants** : accès/export (bouton « Télécharger mes données » JSON), rectification (écran de profil), effacement (bouton « Supprimer mon compte » = suppression en cascade, y compris profils versionnés et statuts), opposition/retrait du consentement ML, limitation. Réponse sous 1 mois.

**Contacts RH** : adresse de contact dédiée (ex. privacy@…) + page publique « Vous figurez dans notre base ? » ; suppression immédiate + inscription en **liste de suppression** (hash de l'email) pour ne pas re-collecter.

---

## 6. Le MVP sans LLM : points d'attention propres

- **Parseur de CV déterministe** : bon point RGPD (pas d'envoi du CV à un tiers). Reste le risque de **données sensibles incidentes** dans un CV (santé, handicap, religion, opinions, engagement associatif révélateur). Règle : on n'extrait *que* ce que le dictionnaire reconnaît ; le texte brut de formation/expériences n'est montré qu'à l'étudiant pour confirmation puis **jeté** (non stocké) ; les mentions hors dictionnaire sont ignorées.
- **Hébergement du fichier pendant le parsing** : en mémoire (pas de stockage disque/objet), suppression immédiate ; pas de logs contenant le texte du CV.
- **Scoring à règles** : transparence maximale (explication du score visible), ce qui aide aussi pour l'AI Act (§7.6).

---

## 7. Sujets spécifiques

### 7.1 Contacts d'entreprises : information (Art. 14) et prospection

- Une donnée « publique » reste une donnée personnelle ; il faut une base légale et une information. La CNIL le rappelle dans ses recommandations pour les réutilisateurs de données publiées en ligne (juin 2024). Elle indique que l'information doit intervenir au plus tard au premier contact (ou sous un mois), qu'elle doit citer la source accessible au public, et que la dérogation pour « efforts disproportionnés » est interprétée de façon restrictive (généralement l'information est requise quand on peut envoyer un email) ; une information publique générale reste obligatoire dans tous les cas.
- La CNIL recommande de **privilégier les API au moissonnage** et de cibler la collecte.
- **Nature du message** : ton service **n'envoie pas** d'emails ; c'est l'étudiant qui envoie une candidature spontanée. Une candidature n'est pas de la prospection commerciale classique, mais le *traitement* de la base de contacts par ton service reste soumis au RGPD. Si un jour tu ajoutes un envoi depuis la plateforme, applique le régime B2B : la CNIL admet l'intérêt légitime/opposition quand l'objet du message est en rapport avec la profession du destinataire, avec information préalable, identité de l'émetteur et moyen d'opposition simple et gratuit. Les adresses génériques de personnes morales (contact@, info@) ne relèvent pas de ces principes.
- **Conception** : (a) page publique d'information (qui, pourquoi, source, durée, droits) ; (b) préférer les adresses génériques/RH de fonction à des adresses nominatives quand c'est suffisant ; (c) provenance par donnée (`publié | inféré | fournisseur`) ; (d) email trouvé **seulement à la demande** de l'étudiant (limite volume et collecte) ; (e) suppression et liste de suppression.
- **Test de mise en balance (intérêt légitime)** à rédiger (1 page) : intérêt = aider des candidats à contacter des recruteurs ; nécessité = pas d'alternative moins intrusive (sinon : passer par pages carrières/formulaires) ; attentes raisonnables = un RH s'attend à recevoir des candidatures, moins à être dans une base achetée. Le cadre est celui des lignes directrices CEPD sur l'intérêt légitime (test en 3 étapes), repris dans l'avis 28/2024 sur l'IA.

### 7.2 Scraping et sources

- La CNIL considère le scraping de données publiques comme un traitement de données personnelles, reposant en général sur l'intérêt légitime *avec garanties*. Garanties listées dans sa fiche : critères de collecte définis à l'avance, filtres/exclusions pour éviter les catégories non nécessaires, suppression immédiate des données non pertinentes ou sensibles collectées par erreur, **exclusion des sites qui s'opposent au moissonnage (robots.txt, CAPTCHA, CGU)**, liste de sites exclus par défaut, limitation aux données accessibles sans compte, information large, droit d'opposition préalable (« liste repoussoir »), pseudonymisation rapide.
- **Application** : respect de robots.txt dans le `PageFetcher`, aucun contournement de CAPTCHA, aucune collecte derrière un login, liste de domaines exclus (réseaux sociaux, annuaires de particuliers), suppression automatique des pages avec données hors-périmètre.
- **Google Maps (via Bright Data)** : les conditions de Google Maps Platform interdisent d'extraire/scraper du contenu Maps pour l'utiliser hors des services (d'après les conditions EEA et des analyses secondaires). Même si le scraper est opéré par un tiers, **le risque contractuel/réputationnel est pour toi**. Pour un projet CV/portfolio : documenter le risque et le limiter (usage minimal : site web/téléphone d'entreprises). Si commercialisation : **basculer sur l'API Google Places** (légale). **[À VÉRIFIER avec les CGU Bright Data et Google à jour]**.
- **DuckDuckGo en repli** : non retenu (risque CGU).

### 7.3 Données de contact fournies par Hunter/Apollo

Ces fournisseurs sont responsables de traitement de leurs bases. Pour toi : (a) lire leur DPA et leurs conditions d'usage (certaines interdisent la revente/l'export massif), (b) conserver la provenance, (c) **revérifier** l'email avant usage, (d) répercuter les demandes d'opposition (et les transmettre au fournisseur si nécessaire). Hunter distingue les emails publiés des devinés ; garder cette distinction.

### 7.4 SIRENE et entrepreneurs individuels

- Sirene contient des données personnelles ; les réutilisateurs doivent respecter le **statut de diffusion le plus récent** (diffusion partielle : nom/adresse masqués à la demande de l'entrepreneur). Les anciennes entreprises « non diffusibles » ont été converties en « diffusion partielle » : ne pas redistribuer intégralement ni les utiliser pour de la prospection. L'Insee ne diffuse pas l'identité des dirigeants de personnes morales.
- **Conséquence pour le produit** : le filtre « entreprises individuelles » est un risque. Par défaut : **exclure les entreprises individuelles** de la découverte, ou appliquer strictement le statut de diffusion et ne jamais déduire une adresse masquée. Rafraîchir le statut de diffusion à chaque mise à jour de la fiche.
- Licence Ouverte 2.0 : citer la source.

### 7.5 Mineurs

- Âge du consentement numérique en France : 15 ans (loi Informatique et Libertés, art. 45). Des étudiants en alternance peuvent avoir 16–17 ans ; la base légale « contrat » est possible pour des mineurs mais la capacité contractuelle est une question de droit civil.
- **Options** : (A) **18+ uniquement** à l'inscription (simple, recommandé pour le MVP BSB : master = majeurs) ; (B) ouvrir aux 15+ avec information adaptée ; (C) <15 : accord parental, hors périmètre. Le consentement ML optionnel : réservé aux majeurs.
- ⚠️ Ne pas stocker « le fait qu'on est mineur » comme donnée de profil : on bloque l'accès, on ne le consigne pas.

### 7.6 Profilage, décision automatisée, AIPD, AI Act

- **Art. 22** : concerne les décisions *exclusivement automatisées* avec effet juridique ou significatif. Ici le classement est un **profilage** (Art. 4.4) mais l'étudiant décide seul de contacter ou non : pas de décision au sens de l'Art. 22. À écrire noir sur blanc dans la politique de confidentialité, avec explication du score.
- **AIPD** (analyse d'impact, Art. 35) : le profilage/scoring et le croisement de sources externes figurent dans les critères de la CNIL ; deux critères cumulés font présumer une AIPD. Faire une **AIPD simplifiée** (outil PIA de la CNIL) ou, au minimum, un **document d'analyse de seuil** expliquant pourquoi elle est allégée.
- **AI Act (Règl. 2024/1689)** : l'annexe III 4(a) classe en haut risque les systèmes d'IA utilisés pour le recrutement/la sélection. Ton outil sert le **candidat** (pas le recruteur) et, dans le MVP, est **à règles prédéfinies**. Les lignes directrices de la Commission sur la définition d'un système d'IA (février 2025) excluent les systèmes fondés sur des heuristiques classiques ou des règles prédéfinies, sans capacité d'inférence apprise. **Conclusion prudente** : le MVP n'est probablement pas un « système d'IA » au sens de l'AI Act ; dès qu'un modèle de ML ou un LLM calcule le score, la question se rouvre. Le calendrier des obligations haut risque a été reporté par le « Digital Omnibus » (début décembre 2027 d'après mes recherches) **[À VÉRIFIER sur EUR-Lex]**. Ne pas affirmer la conformité : présenter cela comme une analyse d'applicabilité.
- **Projet ML BSB** : si tu entraînes un modèle sur des données d'étudiants → consentement séparé, anonymisation, jeu d'entraînement documenté ; et reconsidérer l'AI Act (modèle appris).

### 7.7 Cookies et traceurs

- Clerk (session/authentification) et cookies strictement nécessaires : en principe exemptés de consentement (traceurs nécessaires à un service demandé). **Mesure d'audience** (Vercel Analytics, etc.) : exemptée seulement sous conditions CNIL (finalité strictement statistique, pas de recoupement, pas de transmission de données non anonymes à des tiers) ; sinon bannière de consentement conforme (refus aussi simple que l'acceptation).
- Choix MVP : **aucun traceur non essentiel** → pas de bannière, mention dans la politique. **[À VÉRIFIER la liste réelle des cookies déposés par Clerk et Vercel]**

---

## 8. Si un LLM est ajouté (via `LLMClient`) : conditions

Critères à exiger d'un fournisseur (agnostiques) :

| Critère | Pourquoi | Constat de mes recherches |
|---|---|---|
| DPA (Art. 28) signé/accepté | Obligatoire pour un sous-traitant | Mistral : DPA publié, Mistral = sous-traitant pour l'API ; OpenAI : conditions business/DPA existent ; Anthropic : DPA existe (mais tu as exclu Claude) |
| Pas d'entraînement sur tes données | Évite la réutilisation des CV | Mistral (doc) : données API non utilisées pour l'entraînement ; certaines sources secondaires signalent des exceptions (modèles « Labs », réglages « amélioration du service ») ; OpenAI : pas d'entraînement par défaut sur l'API |
| Localisation UE / transferts | Art. 44 et s. | OpenAI propose une résidence des données en Europe pour les *nouveaux* projets API éligibles ; Mistral annonce un hébergement UE (source secondaire : à confirmer dans le DPA) |
| Rétention (idéalement zéro) | Minimisation | OpenAI : rétention configurable pour organisations éligibles ; zéro rétention avec résidence européenne |
| Liste des sous-traitants ultérieurs | Art. 28.2 | À relever pour le fournisseur choisi |

**Règles d'usage côté produit** : (1) ne jamais envoyer le CV brut ni de données directement identifiantes (pseudonymiser : pas de nom/email/téléphone) ; (2) n'envoyer que le minimum nécessaire à la tâche ; (3) ne pas laisser le LLM prendre de décision (il propose, l'étudiant valide) ; (4) journaliser le modèle et la version utilisés, pas les prompts contenant des données personnelles ; (5) protéger contre l'injection de prompt (le contenu de pages web scrappées est une entrée non fiable) ; (6) informer l'utilisateur de l'usage d'un LLM (transparence) ; (7) mettre à jour l'AIPD et le registre ; (8) réévaluer l'AI Act ; (9) vérifier que le modèle n'est pas utilisé pour inférer des caractéristiques sensibles.

Références utiles : recommandations de la CNIL sur l'IA et l'intérêt légitime, fiche CNIL sur le déploiement d'IA générative, avis CEPD 28/2024.

---

### 8.bis Architecture retenue le 27 nov. 2026 (option B) — impacts RGPD

Chaîne : extraction locale du texte (`unpdf`) → suppression des sections inutiles → anonymisation locale (règles + Presidio/spaCy, module du backend Python hébergé en UE) → aperçu étudiant → LLM à rétention zéro, région UE (profil structuré) → validation étudiant → suppression du texte. Puis jugement LLM sur shortlist avec **le profil structuré validé uniquement**. Mode « sans IA » toujours disponible (choix informé, consentement séparé, décoché par défaut).

À documenter en conséquence :
- **Sous-traitants supplémentaires** : hébergeur du backend Python (UE) ; fournisseur LLM (DPA, rétention zéro confirmée **sur le compte réel**, région UE, pas d'entraînement).
- **Pseudonymisation ≠ anonymisation** : le texte envoyé reste une donnée personnelle ; base légale, information et DPA restent nécessaires.
- **Mesure** : taux de détection de l'anonymisation sur CV annotés, seuil fixé avant la mesure ; publication du résultat.
- **Portes de décision** : fournisseur éligible, seuil atteint, gain mesuré face au parseur à règles ; sinon repli sur le mode simple ou un modèle auto-hébergé.
- **AIPD complète** (profilage + LLM) et note d'applicabilité AI Act à jour (un LLM qui classe des entreprises pour des candidats se rapproche du domaine « recrutement » : à faire valider).
- **Projet non-MVP** : AIPD, DPA, registre et relecture juridique sont des prérequis au lancement, pas des options.
- **Pas de ML d'entraînement** : le consentement « entraînement » prévu au §3 est **supprimé** du périmètre.

## 9. Durées de conservation proposées (à valider)

| Donnée | Durée proposée | Justification |
|---|---|---|
| Compte actif | Tant que le compte est utilisé | Contrat |
| Compte inactif | **Pause à 14 jours** d'inactivité de recherche ; **suppression à 12 mois** d'inactivité (préavis par email 30 jours avant) | La CNIL exige une durée définie et justifiée ; elle cite 2 ans pour certains comptes de contenus numériques (autre contexte) ; 12 mois est un choix de minimisation à défendre |
| Anciennes versions de profil CV | 3 versions max, ou 90 jours | Minimisation |
| Contacts RH | TTL 6 mois si non consultés ; suppression à l'opposition | Exactitude et minimisation. Repère CNIL pour les prospects B2B : 3 ans max depuis la collecte ou le dernier contact venant du prospect (référentiel gestion commerciale) — **ne pas l'appliquer tel quel**, 6 mois est plus protecteur |
| Logs | 6 mois | Sécurité |
| Liste de suppression | Durée nécessaire | Obligation de respecter l'opposition |

---

## 10. Sécurité (Art. 32) — mesures concrètes

Référence : guide de la CNIL sur la sécurité des données personnelles (fiches cloud, API, authentification, habilitations, journalisation, sous-traitance) et guide RGPD du développeur.

- **Authentification** : Clerk, MFA proposé, sessions courtes ; page admin protégée par rôle (vérifier la méthode Clerk) **[À VÉRIFIER]**.
- **Isolation par utilisateur** : toute requête exige `userId` (couche d'accès aux données) + test automatisé d'isolation ; ensuite **RLS PostgreSQL**. Tables partagées (entreprises, contacts) en lecture seule pour les utilisateurs.
- **Chiffrement** : TLS, chiffrement au repos (Neon), secrets dans variables d'environnement Vercel, jamais dans le code.
- **Upload CV** : taille ≤ 4 Mo, type MIME vérifié, parsing en mémoire avec timeout, aucun stockage du fichier.
- **Journalisation** : sans données personnelles inutiles (pas de texte de CV, pas d'emails en clair dans les logs).
- **Dépendances** : Dependabot/`npm audit`, GitHub Actions.
- **Violation de données** : procédure écrite (qui, quoi, quand) ; notification à la CNIL sous **72 h** si risque, information des personnes si risque élevé (Art. 33–34). Registre interne des incidents.
- **Admin** : journal des changements de config (quota, cascade), accès minimal.
- **Sauvegardes** : durée alignée sur la conservation (une suppression doit finir par disparaître des backups).

---

## 11. Checklist « tout ce qu'il faut mettre en place »

### P0 — avant tout utilisateur réel
1. Choisir l'entité responsable de traitement et le point de contact (email privacy).
2. Politique de confidentialité (Art. 13) + page d'information contacts (Art. 14).
3. Schéma de base de données **sans** champs sensibles/inutiles ; CV non stocké (option A) ; test qui vérifie l'absence de stockage du PDF.
4. Parseur CV : dictionnaire, validation par l'étudiant, texte brut jeté.
5. Boutons **exporter** et **supprimer mon compte** (cascade testée).
6. Âge : 18+ (case et mention) ; ne pas consigner la minorité.
7. Registre des traitements (Art. 30) : une ligne par traitement du §3.
8. Registre des sous-traitants + DPA acceptés + régions UE (Neon Frankfurt, ZeroBounce endpoint UE, etc.).
9. Isolation par utilisateur (+ test) ; secrets sécurisés ; page admin protégée.
10. Aucun envoi automatique ; quotas serveur ; pause automatique.

### P1 — avant ouverture à une classe/public large
11. Test de mise en balance (intérêt légitime) écrit, 1 page, daté.
12. Liste de suppression + procédure d'opposition des contacts (réponse sous 1 mois).
13. Provenance + date + TTL sur chaque donnée de contact ; revérification des emails fournisseurs.
14. Exclure/encadrer les entreprises individuelles (statut de diffusion Sirene).
15. Respect robots.txt, liste de domaines exclus, pas de collecte derrière login.
16. AIPD simplifiée (outil PIA CNIL) ou note d'analyse de seuil.
17. Procédure de violation de données (72 h) + registre d'incidents.
18. Politique de rétention appliquée par un job planifié (suppression à 12 mois d'inactivité).
19. Consentement ML séparé, optionnel, décoché, retirable (si le projet ML utilise les données).
20. Cookies : liste réelle, pas de traceur non essentiel ; sinon bannière conforme.

### P2 — maturité / si commercialisation ou LLM
21. Basculer Google Maps scraper → API Google Places ; revoir CGU Bright Data.
22. DPO (non obligatoire a priori : à confirmer) ou référent RGPD désigné.
23. Revue juridique externe ; clauses contractuelles avec fournisseurs.
24. Si LLM : critères du §8, pseudonymisation, protection contre l'injection de prompt, mise à jour AIPD/registre.
25. AI Act : note d'applicabilité à jour (règles vs ML), suivi du calendrier.
26. Audit annuel : suppression effective, sous-traitants, durées, logs.
27. Analyse de transfert hors UE (DPF, clauses types) ; surveillance du recours contre le DPF (CJUE).

---

## 12. Sous-traitants et transferts (synthèse)

| Prestataire | Rôle | Point RGPD | Statut de vérification |
|---|---|---|---|
| Vercel | Hébergement front/API | DPF ; DPA selon le plan (Hobby probablement exclu) | **[À VÉRIFIER plan]** |
| Clerk | Authentification | DPF + DPA + liste de sous-traitants | OK à relire |
| Neon | PostgreSQL | DPA ; région Frankfurt fixée à la création ; entité US | OK |
| Inngest | Orchestration | Société US, SOC 2 Type II ; DPA/DPF non confirmés | **[À VÉRIFIER]** |
| Firecrawl | Lecture de pages | DPA ; rétention zéro seulement en Enterprise | **[À VÉRIFIER]** |
| Bright Data | Scraper Google Maps | Société israélienne ; la Commission a reconduit la décision d'adéquation pour Israël en janvier 2024 (critiquée par des ONG) | À surveiller |
| ZeroBounce | Vérification d'email | DPF, DPA, endpoint UE (Francfort) disponible | Préférer l'endpoint UE |
| Hunter | Contacts | Responsable de traitement de sa base ; intérêt légitime | Lire conditions |
| Apollo | Contacts | Données issues de contributeurs et de tiers | Lire conditions |

**Transferts vers les États-Unis** : le Data Privacy Framework (DPF) a été validé par le Tribunal de l'UE (3 sept. 2025, T-553/23) ; un pourvoi est pendant devant la CJUE. Prévoir un plan B (clauses contractuelles types) et limiter les données envoyées.

---

## 13. Arguments pour la présentation (recruteurs / classe)

- « J'ai réduit le risque *par le schéma* : le CV n'est pas stocké, pas de champs sensibles. »
- « J'ai distingué deux publics : étudiants (collecte directe) et contacts RH (collecte indirecte, Art. 14). »
- « J'ai documenté mes arbitrages : intérêt légitime avec test de mise en balance, retrait des entreprises individuelles, 18+. »
- « J'ai traité l'IA proprement : MVP à règles explicables, LLM seulement derrière une interface et avec critères contractuels. »
- « J'ai pensé coûts *et* conformité : quotas, email à la demande, suppression automatique. »
- Question piège probable : « Pourquoi avoir le droit de contacter ces RH ? » → intérêt légitime documenté, source publique, information publique, opposition simple, aucun envoi automatique.

---

## 14. Points ouverts à vérifier

- Qui est responsable de traitement (toi vs école) ; validation par un juriste/DPO.
- Texte officiel des articles cités (RGPD 5, 6, 9, 13, 14, 21, 22, 25, 28, 30, 32–35) et du Règl. 2024/1689 sur EUR-Lex (je n'ai pas relu chaque article en texte intégral).
- Calendrier AI Act après le « Digital Omnibus ».
- DPA Inngest, Firecrawl, Hunter/Apollo ; plan Vercel ; cookies réels Clerk/Vercel.
- CGU Bright Data / Google Maps ; accès API gratuit Hunter/Apollo.
- Durée de conservation des comptes inactifs : 12 mois est un choix, pas une règle.
- Détail de la fiche « cas d'usage prospection » (pp. 43–49) des recommandations CNIL de juin 2024 : non relue intégralement.

---

## 15. Bibliographie

### Sources officielles (consultées)
- Règlement (UE) 2016/679 (RGPD), EUR-Lex : https://eur-lex.europa.eu/eli/reg/2016/679/oj/fra
- CNIL, *La prospection commerciale par courrier électronique* : https://www.cnil.fr/la-prospection-commerciale-par-courrier-electronique
- CNIL, fiche *moissonnage (web scraping)* : https://www.cnil.fr/en/node/165783
- CNIL, *Recommandations pour les réutilisateurs de données publiées sur internet* (juin 2024) : https://cnil.fr/sites/cnil/files/2024-06/recommandations_reutilisateurs_donnees_publiees_sur_internet.pdf
- CNIL, *Les durées de conservation des données* : https://cnil.fr/fr/les-durees-de-conservation-des-donnees
- CNIL, *Guide durées de conservation* : https://Cnil.fr/sites/cnil/files/atoms/files/guide_durees_de_conservation.pdf
- CNIL, référentiel gestion des activités commerciales (clients/prospects) : https://Cnil.fr/sites/cnil/files/atoms/files/referentiel_traitements-donnees-caractere-personnel_gestion-activites-commerciales.pdf
- CNIL, *Cookies et traceurs : que dit la loi ?* : https://cnil.fr/fr/cookies-traceurs-que-dit-la-loi
- CNIL, *Cookies : solutions pour les outils de mesure d'audience* : https://www.cnil.fr/fr/solutions-pour-la-mesure-daudience
- Commission européenne, lignes directrices sur la définition d'un système d'IA (C(2025) 5053 final, 29 juillet 2025) : https://ai-act-service-desk.ec.europa.eu/sites/default/files/2025-08/commission_guidelines_on_the_definition_of_an_artificial_intelligence_system_established_by_regulation_eu_20241689_ai_actenglish_nf2skcqfrtjdfggjavcodopcwz4_112455.PDF
- Commission européenne, décisions d'adéquation : https://commission.europa.eu/law/law-topic/data-protection/international-dimension-data-protection/adequacy-decisions_en
- CEPD, lettre sur la revue des 11 décisions d'adéquation (déc. 2024) : https://www.edpb.europa.eu/system/files/2024-12/edpb_letter_20241205_european-commission-review-of-11-existing-adequacy-decisions_en.pdf
- Google Maps Platform, conditions EEA : https://cloud.google.com/terms/maps-platform/eea

### Sources officielles des fournisseurs (consultées)
- Mistral AI, DPA : https://legal.mistral.ai/terms/data-processing-addendum
- Mistral AI, contrôles de confidentialité : https://docs.mistral.ai/fr/admin/monitor-comply/privacy-data-controls
- OpenAI, données business : https://openai.com/business-data/
- OpenAI, résidence des données en Europe : https://openai.com/index/introducing-data-residency-in-europe/

### Sources officielles mentionnées, à rouvrir pour citer l'URL exacte
- CNIL : recommandations sur l'IA et l'intérêt légitime ; Q&R déploiement d'IA générative ; guide recrutement ; guide sécurité des données personnelles ; guide RGPD du développeur ; liste des traitements exigeant une AIPD ; outil PIA.
- CEPD : avis 28/2024 sur les modèles d'IA ; lignes directrices 1/2024 sur l'intérêt légitime.
- Insee / data.gouv : documentation Sirene, statut de diffusion, Licence Ouverte 2.0.
- Légifrance : loi Informatique et Libertés (art. 45 sur l'âge du consentement ; art. 82 sur les traceurs).
- Tribunal de l'UE, affaire T-553/23 (Latombe) ; pourvoi C-703/25 P.
- Règlement (UE) 2024/1689 (AI Act), annexe III 4(a) ; texte du « Digital Omnibus ».

### Sources secondaires (indicatives, moins fiables)
- donneespersonnelles.fr (conservation des prospects, Mistral/RGPD), CMS Law (recrutement), conductatlas.com (clauses Google Maps), tech-insider.org (Mistral), analyses de cabinets (Orrick, Hogan Lovells, Reed Smith, Linklaters) sur la définition d'un système d'IA.
