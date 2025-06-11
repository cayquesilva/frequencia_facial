# Usa uma imagem base Python oficial (escolha a versão que você usou)
FROM python:3.11-slim-buster

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de requisitos e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia toda a pasta 'app' para dentro do container
COPY app /app/app

# Cria os diretórios 'data' e seus subdiretórios se não existirem
RUN mkdir -p /app/data/student_images /app/data/temp_recognition_images

# Expõe a porta que o Gunicorn vai usar
EXPOSE 5000

# Comando para iniciar a aplicação Flask com Gunicorn
# 'app.main:app' refere-se ao módulo 'app/main.py' e à instância 'app' do Flask dentro dele
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app.main:app"]