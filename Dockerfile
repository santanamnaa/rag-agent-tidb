FROM python:3.10-slim AS api

WORKDIR /app
COPY . /app
RUN pip install -U pip && pip install -e .[full]

ENV HOST=0.0.0.0 PORT=8000
EXPOSE 8000
CMD ["uvicorn", "scripts.api:app", "--host", "0.0.0.0", "--port", "8000"]

FROM node:20-alpine AS frontend-build
WORKDIR /web
COPY frontend /web
RUN npm install && npm run build

FROM nginx:alpine AS frontend
COPY --from=frontend-build /web/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]


