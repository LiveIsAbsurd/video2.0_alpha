FROM node:14 as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
RUN npm run build
COPY . .

FROM nginx:alpine
COPY --from=build-stage /app/dist /usr/share/nginx/html