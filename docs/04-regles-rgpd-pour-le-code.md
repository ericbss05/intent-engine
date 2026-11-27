# 04 — Règles RGPD traduites en règles de code

> Version courte et opérationnelle de `08-analyse-rgpd.md` (qui reste la référence, avec ses sources). Je ne suis pas juriste : cadre de conception à faire relire avant lancement public.

## Règle → implémentation → test

| # | Règle | Implémentation | Test à écrire |
|---|---|---|---|
| R1 | CV jamais stocké (ni PDF ni texte brut) | Traitement en mémoire, pas d'écriture disque, pas de champ en base, pas de log du contenu | Test qui parse un CV et vérifie qu'aucun fichier/ligne/log ne contient son texte |
| R2 | Minimisation du schéma | Pas de colonnes interdites (voir `03`) | Test de schéma : liste blanche des colonnes |
| R3 | Isolation par utilisateur | Couche d'accès exigeant `user_id` ; RLS ensuite | A ne lit/modifie jamais les données de B (lecture, écriture, suppression) |
| R4 | Droits : export + suppression | Endpoint `GET /me/export` (JSON) ; `DELETE /me` en cascade ; webhook Clerk synchronisé | Suppression complète vérifiée table par table |
| R5 | Logs sans donnée personnelle | Filtre de logs ; `run_events.detail` sans email/nom/texte | Test qui injecte des données factices et vérifie leur absence des logs |
| R6 | Provenance des contacts | `origin`, `source`, `fetched_at`, `ttl_at` obligatoires | Insertion sans provenance refusée |
| R7 | Liste de suppression | Vérifiée avant toute collecte ou affichage ; stockage par hash | Un contact supprimé n'est jamais recollecté |
| R8 | Email à la demande | Aucune recherche d'email hors action « Voir le contact » | Le pipeline automatique n'appelle jamais `ContactFinder`/`EmailVerifier` |
| R9 | Entreprises individuelles exclues | Filtre à la découverte + statut de diffusion respecté | Une entreprise individuelle n'apparaît jamais ; adresse masquée jamais reconstituée |
| R10 | Pas de décision automatisée | Le classement n'a aucun effet automatique ; aucun envoi d'email | Aucun code d'envoi d'email/candidature (test de recherche statique) |
| R11 | LLM : données minimales | Seul texte anonymisé ou profil structuré validé part vers le LLM ; jamais le CV brut | Test sur le payload envoyé (contrat) : pas de nom, email, téléphone |
| R12 | Consentement IA séparé | Case décochée par défaut, journalisée (`consents`) ; mode sans IA complet | Sans consentement, aucun appel LLM |
| R13 | 18+ | Case obligatoire ; minorité non consignée | Inscription impossible sans la case |
| R14 | Purge automatique | Job planifié : comptes inactifs 12 mois, TTL contacts, anciennes versions | Simulation du temps : les données expirent |
| R15 | Pas de traceur non essentiel | Aucun script analytics tiers par défaut | Contrôle des cookies déposés |
| R16 | Sources respectées | `robots.txt`, pas de login/CAPTCHA, liste de domaines exclus | Un domaine exclu ou interdit n'est jamais appelé |
| R17 | Information (Art. 13/14) | Politique de confidentialité ; page publique « Vous figurez dans notre base ? » ; adresse d'opposition | Pages présentes (partie 14) |

## Données interdites
Photo, date de naissance, nationalité, situation familiale, santé/handicap, religion, opinions, adresse exacte, téléphone personnel, numéro d'identification quelconque.

## Données sensibles incidentes
Dans un CV, ignorer tout ce qui n'est pas reconnu par le dictionnaire ; supprimer des **sections entières** (loisirs, associatif, informations personnelles) avant tout traitement IA.

## Sous-traitants à documenter (registre)
Vercel, hébergeur du backend (UE), Clerk, Neon, Inngest, Firecrawl, Bright Data, ZeroBounce/Reoon, Hunter.io, Apollo, fournisseur LLM (si activé). Pour chacun : rôle, données traitées, région, DPA, statut de vérification. Voir tableau dans `08-analyse-rgpd.md` §12.

## Ce que Claude Code doit faire à chaque partie
1. Relire cette liste ; indiquer dans le rapport quelles règles la partie touche.
2. Écrire les tests correspondants.
3. Signaler tout doute (ne pas deviner) dans le rapport.
