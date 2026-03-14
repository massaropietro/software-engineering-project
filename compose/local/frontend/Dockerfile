FROM node:22-bullseye-slim

# --- Build args / defaults ---
ARG NODE_ENV=development
ARG DEV_PORT=5173
ARG APP_HOME=/app

ENV NODE_ENV=${NODE_ENV}
ENV PORT=${DEV_PORT}
ENV CHOKIDAR_USEPOLLING=true
ENV BROWSER=none
ENV PATH=/app/node_modules/.bin:$PATH

WORKDIR ${APP_HOME}

# --- Copia solo package files per installare dipendenze ---
COPY frontend/package*.json .

# --- Installa dipendenze in modo deterministico ---
RUN npm ci

# --- Copia tutto il resto del progetto ---
COPY frontend/ .

# --- Esponi porta dev server ---
EXPOSE ${PORT}

# --- Comando di default per sviluppo con Vite ---
CMD ["npm", "run", "dev", "--", "--host"]
