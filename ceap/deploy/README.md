# Running the CEAP demonstration

A meeting-minutes extraction system: upload a transcript, the knowledge
service extracts what the assembly specification asks for, the assembly is
validated against a policy, and the result is published.

```bash
cp .env.example .env     # add your ANTHROPIC_API_KEY
docker compose up --build
```

- API: http://localhost:8000 (docs at `/docs`)
- UI: http://localhost:3000
- Temporal UI: http://localhost:8080
- MinIO console: http://localhost:9001

The stack runs PostgreSQL and Temporal, MinIO for object storage, and three
images built from this kit: the API, the worker and the demo UI (whose
source is in `../demo-ui/`).

The API and worker images install the kit itself (`pip install .`), so they
need a released julee the kit can resolve. Until julee 0.3.0 is published,
build them against a checkout instead.
