# syntax=docker/dockerfile:1

# Build from the repository root (the tests are in tests/frontend/):
#   docker build -f frontend/Dockerfile --target test -t synapseitu-frontend:test .
#   docker build -f frontend/Dockerfile -t synapseitu-frontend .

FROM node:22.19.0-alpine AS base
WORKDIR /app/frontend
ENV NEXT_TELEMETRY_DISABLED=1

# ---- deps: install from the lockfile only ----
FROM base AS deps
COPY frontend/package.json frontend/package-lock.json frontend/.npmrc ./
RUN npm ci

# ---- test: lint + typecheck + tests; fails the build on any error ----
FROM base AS test
COPY --from=deps /app/frontend/node_modules ./node_modules
COPY frontend/ ./
COPY tests/frontend/ /app/tests/frontend/
RUN npm run lint && npm run typecheck && npm test

# ---- build: produces .next/standalone ----
FROM base AS build
# NEXT_PUBLIC_* values are inlined at build time, so pass them as build args.
ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL
COPY --from=deps /app/frontend/node_modules ./node_modules
COPY frontend/ ./
RUN npm run build

# ---- runner: minimal, non-root runtime serving the standalone server ----
FROM node:22.19.0-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0

RUN addgroup -S -g 1001 nodejs && adduser -S -u 1001 -G nodejs nextjs

COPY --from=build --chown=nextjs:nodejs /app/frontend/public ./public
COPY --from=build --chown=nextjs:nodejs /app/frontend/.next/standalone ./
COPY --from=build --chown=nextjs:nodejs /app/frontend/.next/static ./.next/static

USER nextjs
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://127.0.0.1:3000/api/health || exit 1

CMD ["node", "server.js"]
