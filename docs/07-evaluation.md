# 07 — Évaluation chiffrée et portes de décision

Principe : **des chiffres, pas des impressions**. Chaque brique risquée (CV, anonymisation, site web, emails, IA) est mesurée sur un jeu annoté. Les résultats sont publiés dans `docs/evaluation.md` (partie 13) avec leurs limites.

## Jeux de données (synthétiques, aucune donnée personnelle réelle)

### CV de test (≈ 10)
- Fichiers PDF **synthétiques** (générés ou inventés) couvrant : une colonne, deux colonnes, design chargé, anglais/français, sections atypiques, un PDF scanné (doit être refusé), un CV avec informations sensibles factices (pour tester la suppression de sections).
- Annotation `data/eval/cv/<id>.expected.json` :
```json
{ "skills": ["python", "sql"], "languages": [{"lang":"en","level":"B2"}], "certifications": [],
  "pii": { "names": ["Prénom Nom"], "emails": ["x@y.fr"], "phones": ["0600000000"], "addresses": ["1 rue ..."] } }
```

### Entreprises annotées (≈ 30)
Entreprises **réelles et publiques** (personnes morales uniquement) ; fichier `data/eval/companies.jsonl` :
```json
{"siren":"...","name":"...","website_expected":"https://...","careers_url_expected":null,"generic_contact_expected":"contact@...","notes":""}
```
Sert à mesurer : site correct, page carrières trouvée, contact générique trouvé.

### Pertinence perçue
Test avec 5 à 10 étudiants volontaires (consentement explicite, données minimales) : note de 1 à 5 de pertinence des 5 premières suggestions ; commentaires libres anonymisés.

## Métriques

| Mesure | Définition | Quand |
|---|---|---|
| Rappel des compétences (règles) | compétences attendues retrouvées / attendues | Partie 3 |
| Détection d'anonymisation | PII attendues masquées / PII attendues, par type (noms, emails, téléphones, adresses) | Partie 4 |
| Rappel des compétences (assisté vs règles) | idem, sur les mêmes CV | Partie 5 |
| Site correct | sites corrects / entreprises annotées | Partie 9 |
| Taux de « site introuvable » honnête | introuvables déclarés / sans site réel | Partie 9 |
| Emails valides | valides (après vérification) / emails trouvés | Partie 11 |
| Crédits par clic « Voir le contact » | moyenne par fournisseur | Partie 11 |
| Précision@5 | part des 5 premières suggestions jugées pertinentes | Parties 7, 10, 13 |
| Taux d'échec par étape, coût par recherche | agrégations `run_events` | Partie 12–13 |

## Portes de décision de la couche IA

À **fixer avant de mesurer** (valeurs de départ, discutables avec l'utilisateur) :

| Porte | Condition d'ouverture | Si non franchie |
|---|---|---|
| **P4 — Anonymisation** | ≥ 95 % de détection sur noms, emails, téléphones ; adresses : seuil à décider | L'option « IA sur CV » reste fermée ; pas d'envoi au LLM |
| **P5a — Fournisseur LLM** | Rétention zéro + région UE + DPA lu + pas d'entraînement, **confirmés sur le compte réel** | Repli : modèle auto-hébergé ou mode sans IA |
| **P5b — Gain du profil assisté** | Rappel des compétences > référence à règles sur les 10 CV | Mode assisté non activé |
| **P10 — Jugement LLM** | Précision@5 > scoring à règles sur le test | Jugement LLM retiré |

Le **mode sans IA** doit rester complet et être testé à chaque partie IA.

## Format du rapport d'évaluation
Tableau des métriques, méthode, limites (petits échantillons, biais), comparaison règles vs IA, coûts, décisions prises (portes ouvertes ou fermées).
