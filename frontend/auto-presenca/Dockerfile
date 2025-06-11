# Fase de Build: Usar uma imagem Node.js para construir a aplicação Vue (com Vite)
FROM node:lts-alpine as builder

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos de configuração do projeto (package.json e package-lock.json)
COPY package*.json ./

# Instala as dependências do projeto
RUN npm install

# Copia o restante dos arquivos do projeto (incluindo src/, public/, .env.production etc.)
COPY . .

# Compila a aplicação Vite para produção
# O Vite usará o .env.production para embutir a VITE_API_BASE_URL
RUN npm run build

# Fase de Produção: Usar uma imagem Nginx para servir os arquivos estáticos da aplicação
FROM nginx:alpine

# Copia os arquivos estáticos da aplicação construída (output da fase 'builder')
COPY --from=builder /app/dist /usr/share/nginx/html

# Opcional: Copia uma configuração Nginx personalizada para Single Page Applications (SPAs)
# Se você tiver um arquivo nginx.conf personalizado na raiz da sua pasta auto-presenca, descomente:
# COPY ./nginx.conf /etc/nginx/conf.d/default.conf
# Um exemplo de nginx.conf para SPAs que roteia todas as requisições não encontradas para index.html:
# events { }
# http {
#   include /etc/nginx/mime.types;
#   default_type application/octet-stream;
#   server {
#     listen 80;
#     server_name localhost; # Pode ser o domínio da sua aplicação
#     location / {
#       root /usr/share/nginx/html;
#       index index.html index.htm;
#       try_files $uri $uri/ /index.html;
#     }
#   }
# }

# Expõe a porta 80 do Nginx
EXPOSE 80

# Comando para iniciar o Nginx
CMD ["nginx", "-g", "daemon off;"]