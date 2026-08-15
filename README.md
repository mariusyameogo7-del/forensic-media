# Forensic Media — Plateforme africaine de vérification numérique

> **Plateforme africaine d'analyse de provenance, d'intégrité et de contexte des médias numériques.**

---

## 1. Philosophie et Principes directeurs

$$\text{Preuve} \longrightarrow \text{Sources} \longrightarrow \text{Explication} \longrightarrow \text{Conclusion prudente}$$

- **Aucun score global de vérité** : La plateforme ne prétend pas qu'un algorithme détecte la vérité absolue.
- **Détection d'IA $\neq$ Détection de désinformation** : Une vraie image peut être décontextualisée, une image générée par IA peut être utilisée loyalement.
- **Transparence et Explicabilité** : Chaque conclusion est justifiée dans la section **« Pourquoi cette conclusion ? »** adossée à des faits vérifiables (preuves techniques, informations déclarées, correspondances externes, estimations).
- **Privacy-first** : Le média original n'est pas conservé par défaut ; suppression conjointe des miniatures et dérivés après analyse.

---

## 2. Architecture et 4 Dimensions d'analyse

```text
                                  +-----------------------+
                                  |  Next.js 16 Frontend  | (Vercel)
                                  +-----------+-----------+
                                              | HTTPS
                                  +-----------v-----------+
                                  |   FastAPI Backend     | (Render Frankfurt)
                                  +-----+-----------+-----+
                                        |           |
            +---------------------------+           +---------------------------+
            |                                                                   |
+-----------v-----------+                                           +-----------v-----------+
| PostgreSQL 17 / Auth  |                                           |     Redis Broker      |
| Supabase Storage      | (Supabase Frankfurt)                      +-----------+-----------+
+-----------------------+                                                       |
                                                                    +-----------v-----------+
                                                                    | Celery Analysis Worker|
                                                                    +-----------+-----------+
                                                                                |
                                     +------------------------------------------+------------------------------------------+
                                     |                    |                     |                    |                     |
                               +-----v-----+        +-----v-----+         +-----v-----+        +-----v-----+         +-----v-----+
                               | C2PA / CC |        |  ExifTool |         |  Hive AI  |        | Google Vis|         | FactChecks|
                               +-----------+        +-----------+         +-----------+        +-----------+         +-----------+
```

### Les 4 indicateurs indépendants :
1. **Provenance** : `verified` | `partial` | `unknown` | `inconsistent`
2. **Intégrité** : `clear` | `review` | `major_anomaly`
3. **IA** : `indeterminate` | `low` | `moderate` | `high` | `declared`
4. **Contexte** : `coherent` | `review` | `potential_decontextualization`

### Niveau de conclusion synthétique :
- `no_major_alert`
- `review_recommended`
- `important_attention`

---

## 3. Structure du Monorepo

```text
forensic-media/
├── apps/
│   ├── api/                      # Backend FastAPI (Python 3.12, SQLAlchemy 2, Alembic, Pydantic v2)
│   │   ├── app/
│   │   │   ├── api/v1/           # Endpoints REST (/analyses, /progress, /result, /reports, /auth)
│   │   │   ├── core/             # Config, DB, Security, Errors
│   │   │   ├── models/           # 15 entités PostgreSQL
│   │   │   ├── schemas/          # Schémas Pydantic v2
│   │   │   └── services/         # Upload, Storage, Analysis, Reports, Cleanup
│   │   └── alembic/              # Migrations de base de données
│   └── web/                      # Frontend Next.js 16 (TypeScript, Tailwind CSS 4)
│       └── src/
│           ├── app/              # 6 Écrans (Upload, Progress, Résultat, Historique, Rapport, Compte)
│           ├── components/       # Composants UI, Dropzone, Badges, Cartes moteurs, Preuves
│           └── lib/              # Client API, Token storage, Types
├── workers/
│   └── analysis/                 # Worker Celery 5.6 & Moteurs d'analyse
│       └── worker/
│           ├── adapters/         # AIProvider, WebContextProvider, FactCheckProvider
│           ├── engines/          # C2PA, ExifTool, Hashes, AI, Web, FactCheck, Synthesis
│           └── orchestrator.py   # Orchestrateur d'analyse asynchrone
├── packages/
│   └── shared-contracts/         # Définitions TypeScript / Contrats partagés
├── infra/
│   └── docker/                   # Dockerfiles API, Worker, Web
├── tests/                        # Suites de tests automatisés (Upload, Accès, Synthèse, Privacy, Rapports)
├── docker-compose.yml            # Environnement complet local (Postgres 17, Redis 7, API, Worker, Web)
└── .env.example
```

---

## 4. Démarrage Rapide

### Option A : Avec Docker Compose
```bash
docker-compose up --build
```
- Frontend Web : `http://localhost:3000`
- Backend API : `http://localhost:8000`
- Documentation API interactive : `http://localhost:8000/docs`

### Option B : En local (Développement)
1. **Lancer le Backend API :**
   ```bash
   python -m uvicorn apps.api.app.main:app --reload --port 8000
   ```
2. **Lancer le Worker Celery :**
   ```bash
   celery -A workers.analysis.worker.celery_app:celery_app worker --loglevel=info
   ```
3. **Lancer les tests unitaires :**
   ```bash
   python -m pytest
   ```
