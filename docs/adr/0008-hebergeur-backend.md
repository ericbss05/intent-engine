# ADR 0008 — Hébergeur du backend (UE)

- **Statut** : proposé (à valider par l'étudiant ; rien n'est déployé)
- **Date** : 2026-11-27
- **Contexte** : le backend FastAPI (conteneur Docker) doit tourner en UE (RGPD, `docs/04`). Il reçoit des requêtes occasionnelles et, plus tard, des tâches Inngest. Budget d'étudiant : on veut un coût proche de zéro et peu d'administration.

## Options (sources : documentation et pages tarifaires officielles, consultées le 2026-11-27)

| Critère | **Scaleway Serverless Containers** | **Render (offre UE)** | **Fly.io (Paris)** |
|---|---|---|---|
| Société / juridiction | Française (Iliad) | Américaine | Américaine |
| Région UE confirmée | Paris (aussi Amsterdam, Varsovie) | **Non confirmée dans mes sources** : à vérifier dans la console | Paris (`cdg`) |
| Coût | Facturé à la consommation (€0,00001/vCPU-s, €0,000002/Go-s, HT) après une allocation gratuite mensuelle (200 000 vCPU-s, 400 000 Go-s) ; trafic sortant gratuit | Offre gratuite avec mise en veille après 15 min (réveil ≈ 1 min) ; payant « toujours actif » dès ≈ 7 $/mois | Machine facturée à l'heure ; prix de base 2,19 $/mois (256 Mo) en région US ; **prix `cdg` non trouvé** |
| Simplicité | Pousse d'une image, mise à l'échelle à zéro | Très simple (lien GitHub) | CLI `flyctl`, plus technique |
| RGPD | Pas de transfert hors UE lié à la société | Société US : clauses contractuelles à examiner | Société US : idem |

## Décision proposée
**Scaleway Serverless Containers (région Paris)** : plus simple à justifier devant un jury RGPD (société et données en UE), coût probablement nul à notre volume grâce à l'allocation gratuite, et notre `Dockerfile` suffit.

## Conséquences
- Le `Dockerfile` (`apps/api/Dockerfile`) est prêt ; le port est lu dans `$PORT`.
- Démarrage à froid possible (mise à l'échelle à zéro) : le front doit tolérer une première réponse lente.
- Si on change d'avis, seul le déploiement change, pas le code.

## À vérifier (non confirmé, ne pas présenter comme un fait)
- Que l'allocation gratuite et les tarifs de Scaleway sont toujours ceux de la page actuelle (le tarif mémoire a changé le 2026-06-01 selon leur blog).
- Pour Render : la présence d'une région UE ; pour Fly : le tarif `cdg`.
- Les délais d'un démarrage à froid réel avec notre image.
- Les conditions contractuelles (DPA) de l'hébergeur retenu.
