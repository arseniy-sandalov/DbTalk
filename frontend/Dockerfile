FROM node:20-alpine

WORKDIR /app

COPY package.json .

RUN npm install

COPY . .

EXPOSE 3000
EXPOSE 5173

CMD cd app; ls; npm run dev -- --host
