# Partie 1 — Compte, base, isolation, droits (≈ 4 j)

## Contexte
Partie 0 validée. Lis `docs/03-modele-de-donnees.md`, `docs/04` (R2, R3, R4, R5, R13), `docs/adr/0003`.

## Tâche
1. Clerk côté front (connexion, déconnexion) ; **vérification du jeton côté backend** à chaque requête (middleware/dépendance FastAPI) ; rôle `admin` géré dans Clerk et vérifié **côté serveur**.
2. PostgreSQL (Neon, **région Frankfurt**) ; SQLAlchemy 2 + Alembic ; première migration : `user_profile`, `consents`.
3. **Couche d'accès aux données** : toutes les fonctions d'accès aux données d'un étudiant exigent `user_id` (pas d'accès direct aux modèles depuis les routes).
4. Webhook Clerk : création du profil à l'inscription, **suppression en cascade** à la suppression du compte (vérifier la signature du webhook).
5. Endpoints `GET /me/export` (JSON de toutes les données de l'utilisateur) et `DELETE /me` (suppression en cascade) + boutons dans l'UI.
6. Case **18 ans minimum** à l'inscription (journaliser `adult_confirmed_at`, ne pas consigner la minorité).
7. Page admin vide protégée par rôle (test : un non-admin reçoit 403 côté serveur).
8. Tests : **isolation entre utilisateurs** (lecture/écriture/suppression), suppression en cascade, export complet, rôle admin.

## Contraintes
- Pas de colonnes interdites (voir `docs/03`).
- Logs sans donnée personnelle.
- Base de test jetable pour les tests d'intégration ; pas de données réelles.
- Pas encore de RLS (prévue plus tard) ; prévoir la structure pour l'ajouter.

## Sorties attendues
Migration Alembic, modules `core/security`, `domain`, `services` d'accès aux données, routes `/me/*`, webhook, pages front d'auth, tests, `docs/reports/part-01.md`.

## Critères de terminé
- [ ] Un utilisateur crée un compte, se connecte, voit uniquement ses données.
- [ ] Test d'isolation vert (A ne voit jamais B).
- [ ] Suppression du compte supprime toutes ses lignes (test table par table) ; export JSON complet.
- [ ] Page admin inaccessible sans rôle (403 serveur).

## Questions à poser avant de coder
Méthode de rôle admin dans Clerk ; stratégie de connexions poolées sur Neon ; durée de session.

## Hors périmètre
Questionnaire, CV, recherches.
