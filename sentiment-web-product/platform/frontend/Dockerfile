ARG NODE_IMAGE=node:22-alpine
ARG NGINX_IMAGE=nginx:1.27-alpine

FROM ${NODE_IMAGE} AS deps

WORKDIR /app

COPY package.json package-lock.json* /app/
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

FROM ${NODE_IMAGE} AS dev

WORKDIR /app
ENV PATH="/app/node_modules/.bin:${PATH}"

COPY --from=deps /app/node_modules /app/node_modules
COPY package.json /app/package.json

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

FROM deps AS build

COPY . /app
RUN npm run build

FROM ${NGINX_IMAGE} AS production

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
