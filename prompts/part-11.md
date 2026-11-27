# Partie 11 — Contacts et emails à la demande (≈ 5 j)

## Contexte
Partie 9 validée. Lis `docs/adr/0004`, `docs/06` (ContactFinder, EmailVerifier), `docs/04` (R6, R7, R8, R17), `docs/08` §7.1 et §7.3, `docs/07`.

## Tâche
1. **Lire les documentations officielles** de Hunter.io, Apollo, ZeroBounce, Reoon (accès API, quotas gratuits, conditions d'usage, DPA, endpoints UE) ; **ne pas coder les quotas en dur** ; noter les incohérences trouvées.
2. `ContactFinder` en **cascade** qui s'arrête au premier résultat fiable : (1) pages équipe/carrières, (2) mentions légales/contact, (3) registre (dirigeants, limité), (4) **Hunter.io**, (5) **Apollo** en dernier recours. Préférer une adresse générique/RH de fonction à une adresse nominative quand suffisant. Pas de téléphone personnel.
3. Emails : publié → motif inféré (3 candidats max, marqués « inféré ») → fournisseurs. `EmailVerifier` : syntaxe + MX (interne, gratuit) → **ZeroBounce (endpoint UE)** → **Reoon** en secours ; cache par adresse ; « catch-all » jamais présenté comme « vérifié ». Les emails venant d'un fournisseur sont **revérifiés**.
4. Provenance sur chaque donnée (`origin`, `source`, `fetched_at`, `ttl_at`) ; disjoncteur + budget par fournisseur (admin).
5. **Liste de suppression** (hash) vérifiée avant toute collecte/affichage ; page publique « Vous figurez dans notre base ? » + adresse d'opposition ; procédure de suppression + inscription dans la liste.
6. Bouton **« Voir le contact »** actif : déclenche une tâche à la demande (jamais dans le pipeline automatique, R8) ; affichage avec provenance et statut.
7. Mesure : taux d'emails valides, crédits consommés par clic (par fournisseur) sur ≈ 10 entreprises annotées ; **décider l'ordre Hunter/Apollo** d'après le test des deux comptes.
8. Tests (fixtures, aucun réseau) : cascade, suppression respectée, catch-all, revérification, pas d'appel hors action utilisateur.

## Contraintes
- **Aucun envoi d'email.** L'étudiant copie ou utilise l'adresse lui-même.
- Minimiser les données (pas de détails inutiles sur la personne).
- Hunter/Apollo = responsables de traitement de leurs bases : conserver la provenance, répercuter les oppositions.

## Sorties attendues
Adaptateurs `hunter`, `apollo`, `zerobounce`, `reoon`, `contact_finder` (pages), migrations, page publique d'information, procédure d'opposition, `docs/evaluation-contacts.md`, ADR sur l'ordre Hunter/Apollo, `docs/reports/part-11.md`.

## Critères de terminé
- [ ] Taux d'emails valides et crédits par clic mesurés et publiés.
- [ ] Un contact supprimé n'est jamais recollecté (test).
- [ ] Aucun appel contact/email dans le pipeline automatique (test).

## Questions à poser avant de coder
Comptes ouverts ; adresse email de contact RGPD ; durée TTL des contacts.

## Hors périmètre
Envoi, séquences d'emails, téléphones.
