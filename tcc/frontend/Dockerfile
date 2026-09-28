# Stage 1: Build
FROM node:18-alpine as build-stage
WORKDIR /app
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve
FROM nginx:stable-alpine as production-stage

# Copiar configurações antes de mudar para non-root
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Segurança: Rodar como non-root
RUN touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid /var/cache/nginx /var/log/nginx /etc/nginx/conf.d /usr/share/nginx/html

USER nginx

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
