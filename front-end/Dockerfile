FROM node:14.17.0 as build

WORKDIR /aime/front-end

COPY . .

RUN npm install

EXPOSE 3000

CMD ["npm", "start"]
