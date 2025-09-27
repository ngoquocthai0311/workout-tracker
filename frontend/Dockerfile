FROM node:22.18.0-slim AS build

WORKDIR /frontend

COPY package.json package-lock.json ./

COPY . .

# Clean install of dependencies leveraging Docker build cache
RUN --mount=type=cache,target=/root/.npm npm ci

# Trigger Angular Compatibility Compiler to make sure 3rd-party node modules compatible with Angular's Ivy renderer
RUN npx ngcc --properties es2023 browser module main --first-only --create-ivy-entry-points

RUN npm run build --configuration=production

FROM nginx:stable AS final

COPY --from=build /frontend/dist/frontend/browser  /usr/share/nginx/html

# Using configuration file to set up nginx server. Already include set up for proxy 
COPY /nginx.conf  /etc/nginx/conf.d/default.conf

# NOTE: expose here is for documentation purpose
EXPOSE 80