FROM node:18-alpine

WORKDIR /app

COPY package.json .
RUN npm install

COPY . .

# Listen on 0.0.0.0 so the dev server is reachable from host when using Docker
ENV HOST=0.0.0.0
ENV DANGEROUSLY_DISABLE_HOST_CHECK=true
# Use npx to avoid "react-scripts: Permission denied" on some systems
CMD ["npx", "react-scripts", "start"]
