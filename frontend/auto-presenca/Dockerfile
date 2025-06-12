# Fase de Build: Usar uma imagem Node.js para construir a aplicação Vue (com Vite)
FROM node:lts-alpine AS builder

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos de configuração do projeto (package.json e package-lock.json)
# Copiar package*.json primeiro para otimizar o cache da camada npm install
COPY package*.json ./

# Copia os arquivos de ambiente AGORA, ANTES do npm install e npm run build
# Isso garante que eles estejam disponíveis para o Vite
COPY .env.production ./.env.production
# Se você tiver um .env geral que não deve ser sobrescrito pelo .env.production, copie-o também aqui
# COPY .env ./.env

# Instala as dependências do projeto
RUN npm install

# Copia o restante dos arquivos do projeto (src/, public/ etc.)
COPY . .

# Compila a aplicação Vite para produção
# O Vite agora terá acesso ao .env.production copiado
RUN npm run build

# Fase de Produção: Usar uma imagem Nginx para servir os arquivos estáticos
FROM nginx:alpine

# Copia os arquivos estáticos da aplicação construída (output da fase 'builder')
COPY --from=builder /app/dist /usr/share/nginx/html

# Expõe a porta 80 do Nginx
EXPOSE 80

# Comando para iniciar o Nginx
CMD ["nginx", "-g", "daemon off;"]