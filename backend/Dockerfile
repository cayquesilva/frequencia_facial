# Usa uma imagem base Python oficial (garanta que a versão seja compatível com TensorFlow, ex: 3.11)
FROM python:3.11-slim-buster

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de requisitos e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia toda a pasta 'app' para dentro do container, mantendo a estrutura 'app/'
COPY app /app/app

# Cria os diretórios 'data' e seus subdiretórios no container se não existirem
# Isso é importante para o primeiro boot, antes do volume ser montado/populado
RUN mkdir -p /app/data/student_images /app/data/temp_recognition_images

# Expõe a porta que o Gunicorn vai usar (a mesma que Flask escuta)
EXPOSE 5000

# Comando para iniciar a aplicação Flask com Gunicorn
# 'app.main:app' significa: no módulo 'app/main.py', encontre a instância 'app' do Flask
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app.main:app"]