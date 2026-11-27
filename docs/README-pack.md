# Pack de démarrage pour Claude Code — service stage/alternance

Ce dossier contient tout ce qu'il faut pour que Claude Code construise le projet **partie par partie**, avec des règles claires.

## Contenu

| Élément | Rôle |
|---|---|
| `CLAUDE.md` | Règles permanentes de Claude Code (méthode, RGPD, sécurité, tests, git) |
| `docs/00-brief-produit.md` | Produit, parcours utilisateur, périmètre, hors-périmètre |
| `docs/01-architecture.md` | Architecture, flux, cascades, interfaces |
| `docs/02-stack-et-conventions.md` | Stack, structure du dépôt, conventions |
| `docs/03-modele-de-donnees.md` | Tables, colonnes, conservation |
| `docs/04-regles-rgpd-pour-le-code.md` | Règles RGPD sous forme de règles de code et de tests |
| `docs/05-plan-par-parties.md` | Plan en 16 parties (validation une par une) |
| `docs/06-interfaces-contrats.md` | Contrats des interfaces (ports) en Python |
| `docs/07-evaluation.md` | Jeux annotés, métriques, portes de décision de l'IA |
| `docs/08-analyse-rgpd.md` | Analyse RGPD complète (référence juridique) |
| `docs/adr/` | Décisions d'architecture déjà prises |
| `prompts/part-00.md … part-15.md` | Un prompt par partie : contexte, tâche, contraintes, sorties, critères |
| `.claude/commands/` | Commandes `/start-part N`, `/finish-part N`, `/rgpd-check` |
| `templates/` | `.env.example`, CI GitHub Actions, modèles d'ADR et de rapport |

## Comment l'utiliser

1. Crée le dépôt GitHub (vide) et clone-le en local.
2. **Décompresse ce pack à la racine du dépôt** (les fichiers `CLAUDE.md`, `docs/`, `prompts/`, `.claude/`, `templates/` à la racine).
3. Prépare tes comptes (voir « Avant la partie 0 » ci-dessous).
4. Ouvre Claude Code dans le dépôt et lance : `/start-part 0`.
5. Claude Code te pose ses questions, propose un plan, code, teste, puis écrit `docs/reports/part-00.md`.
6. **Tu relis le rapport, tu testes, tu valides** (ou tu demandes des corrections). Seulement ensuite : `/start-part 1`.
7. Continue jusqu'à la partie 15.

## Avant la partie 0

- [ ] Dépôt GitHub créé (nom à choisir).
- [ ] Comptes : Vercel, Clerk, Neon (**région Frankfurt dès la création**, non modifiable après), hébergeur UE du backend (à choisir en partie 0).
- [ ] Rythme de travail décidé (heures par semaine).
- [ ] Vérifié : le plan Vercel gratuit autorise-t-il ton usage (non commercial) ?
- [ ] Plus tard (parties 9 et 11) : comptes Bright Data, Firecrawl, Hunter.io, Apollo, ZeroBounce, Reoon (à ouvrir seulement quand tu y arrives).

## Rappels importants

- **Je ne suis pas juriste** : le doc RGPD est un cadre de conception, à faire relire par un juriste ou le DPO de l'école avant tout lancement public (partie 14).
- Les quotas et tarifs des fournisseurs cités dans les docs viennent de recherches ponctuelles : **à revérifier** à l'ouverture de chaque compte.
- L'IA (parties 4, 5, 10) est derrière des **portes de décision** : si les mesures ne sont pas bonnes, on ne l'active pas.
- Aucune donnée personnelle réelle dans le dépôt (CV synthétiques uniquement).
