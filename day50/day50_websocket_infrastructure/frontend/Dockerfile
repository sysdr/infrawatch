FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY public/ ./public/
COPY src/ ./src/
COPY .env .env

EXPOSE 3000

CMD ["npm", "start"]
