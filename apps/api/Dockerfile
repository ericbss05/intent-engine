# Image du backend. Build depuis apps/api : docker build -t stage-finder-api apps/api
FROM python:3.12-slim

# uv installé depuis PyPI avec une version fixée (reproductible).
RUN pip install --no-cache-dir uv==0.13.10

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PYTHONUNBUFFERED=1
WORKDIR /srv

# 1) Dépendances d'abord : cette couche est mise en cache tant que uv.lock ne change pas.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# 2) Code ensuite.
COPY app ./app

# Utilisateur non-root : si le service est compromis, il a peu de droits.
RUN useradd --system --uid 10001 appuser
USER appuser

ENV PATH="/srv/.venv/bin:$PATH" APP_ENV=production PORT=8080
EXPOSE 8080

# Les plateformes imposent le port via $PORT ; forme "shell" pour que la variable soit lue.
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
