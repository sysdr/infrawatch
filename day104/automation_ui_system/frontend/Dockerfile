FROM node:18-alpine AS builder

WORKDIR /app

# Build args for API URLs (baked into bundle - browser uses these)
ARG REACT_APP_API_URL=http://localhost:8000/api/v1
ARG REACT_APP_WS_URL=http://localhost:8000
ENV REACT_APP_API_URL=$REACT_APP_API_URL
ENV REACT_APP_WS_URL=$REACT_APP_WS_URL

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Production stage: serve static files
FROM node:18-alpine

WORKDIR /app

RUN npm install -g serve

COPY --from=builder /app/build ./build

EXPOSE 3000

# Bind to 0.0.0.0 so accessible from host (WSL2/Windows)
CMD ["serve", "-s", "build", "-l", "3000"]
