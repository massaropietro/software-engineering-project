# Stage 1: Build the frontend
FROM node:22-alpine AS frontend-build-stage

WORKDIR /app/frontend

COPY ./frontend/package.json ./frontend/package-lock.json ./
RUN npm ci

COPY ./frontend ./

ARG VITE_API_BASE_URL
ARG VITE_EVENT_VISITA_UUID
ARG VITE_EVENT_ALLENAMENTO_UUID

ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_EVENT_VISITA_UUID=$VITE_EVENT_VISITA_UUID
ENV VITE_EVENT_ALLENAMENTO_UUID=$VITE_EVENT_ALLENAMENTO_UUID

RUN npm run build

# Stage 2: Serve with Nginx
FROM docker.io/nginx:1.27-alpine

COPY --from=frontend-build-stage /app/frontend/dist /usr/share/nginx/html
COPY ./compose/production/nginx/default.conf /etc/nginx/conf.d/default.conf
