# Multi-stage build for the EpiVirus full-stack application

# Stage 1: build the React frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend, serving the built frontend
FROM python:3.11-slim
WORKDIR /app

ENV PYTHONUNBUFFERED=1     PYTHONDONTWRITEBYTECODE=1     PIP_NO_CACHE_DIR=1     PORT=8000

# Every runtime dependency ships a manylinux wheel, so no C toolchain is
# needed. gcc/g++ were only required by the matplotlib and pandas builds that
# are no longer part of this service.
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./

# The built frontend is served by FastAPI's catch-all route
COPY --from=frontend-builder /app/frontend/dist ./static

# Run as an unprivileged user
RUN useradd --create-home --uid 10001 epivirus && chown -R epivirus:epivirus /app
USER epivirus

EXPOSE 8000

CMD ["python", "api_server.py"]
