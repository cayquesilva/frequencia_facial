# Usa uma imagem base Python oficial (garanta que a versão seja compatível com TensorFlow, ex: 3.11)
FROM python:3.11-slim-buster

# Instala as dependências do sistema necessárias para OpenCV/DeepFace
# libgl1-mesa-glx: Fornece a biblioteca libGL.so.1
# libglib2.0-0: Outra dependência comum para muitas aplicações gráficas
# libsm6, libxext6, libxrender1: Outras dependências comuns para OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de requisitos e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia toda a pasta 'app' para dentro do container, mantendo a estrutura 'app/'
COPY app /app/app

# Cria os diretórios 'data' e seus subdiretórios se não existirem
RUN mkdir -p /app/data/student_images /app/data/temp_recognition_images

# Expõe a porta que o Gunicorn vai usar
EXPOSE 5000

# Comando para iniciar a aplicação Flask com Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app.main:app"]