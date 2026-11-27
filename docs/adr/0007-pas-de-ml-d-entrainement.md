# ADR 0007 — Pas de ML d'entraînement dans ce projet

- **Statut** : accepté (27 nov. 2026)
- **Contexte** : l'utilisateur a indiqué qu'il n'y avait pas forcément besoin de ML. Sans volume d'utilisateurs, un modèle appris n'apporterait rien de fiable (démarrage à froid).
- **Décision** : pas de modèle entraîné ; scoring à règles explicable, éventuellement complété par un jugement LLM sur shortlist (ADR 0002). Le consentement « entraînement » est retiré du périmètre.
- **Conséquences** : ce projet n'est pas présenté comme « le projet ML en Python » ; un projet ML séparé reste possible. À reconsidérer seulement si assez de données d'usage sont collectées **avec consentement**, ce qui rouvrirait l'AIPD et l'analyse AI Act.
