# ADR 0004 — Cascades de fournisseurs, disjoncteurs et budgets

- **Statut** : accepté (27 nov. 2026)
- **Contexte** : l'outil d'origine tirait sa force de nombreux plans B (Hunter/Apollo, scraping de pages), mais échouait en silence et ne revérifiait pas les emails de fournisseurs. Les offres gratuites sont petites.
- **Décision** : pour chaque besoin, une **cascade du moins cher au plus cher**, qui **s'arrête au premier résultat fiable** ; provenance conservée ; emails de fournisseurs revérifiés ; **disjoncteur** par fournisseur ; **budget mensuel** par fournisseur ; ordre et activation **configurables depuis l'admin** ; pas de scraping de moteurs de recherche.
- **Cascades** : voir `docs/01-architecture.md`.
- **Conséquences** : adaptateurs + interfaces ; table `provider_usage` ; tests avec fixtures ; l'ordre Hunter/Apollo est décidé après test des deux comptes sur 10 entreprises annotées ; quotas jamais codés en dur.
