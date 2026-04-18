FROM node:22-bookworm-slim

WORKDIR /workspace/frontend

RUN corepack enable

COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install --immutable

COPY frontend ./

ENV VITE_API_BASE_URL=http://127.0.0.1:8000

EXPOSE 5173

CMD ["yarn", "dev", "--host", "0.0.0.0", "--port", "5173"]
