FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

# Vite runs on 5173 by default. Use --host to expose it to Docker network.
CMD ["npm", "run", "dev", "--", "--host"]
