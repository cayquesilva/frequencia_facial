# app/main.py
from flask import Flask
from flask_cors import CORS
import os

# Importar serviços e rotas
from app.services.database import init_db
from app.services.face_recognition import load_embeddings
from app.routes import api_bp # Importa o Blueprint das rotas

app = Flask(__name__)

# Configurar CORS para todas as rotas da API
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Registrar o Blueprint das rotas
app.register_blueprint(api_bp)

# Rota Home da aplicação (acessível em http://localhost:5000/)
@app.route('/')
def home():
    return "Servidor Backend Principal está rodando! Acesse /api para os endpoints."

# Inicializar o banco de dados e carregar embeddings ao iniciar o app
# Use app.before_first_request ou chame diretamente para garantir inicialização
# app.before_first_request é mais adequado para a primeira requisição real.
# Para garantir que seja executado na inicialização, podemos chamar diretamente.
with app.app_context(): # Garante que estamos no contexto da aplicação Flask
    init_db()
    load_embeddings()

if __name__ == '__main__':
    # Flask em modo debug (apenas para desenvolvimento)
    # host='0.0.0.0' permite que o servidor seja acessível de fora do localhost
    app.run(debug=True, host='0.0.0.0', port=5000)