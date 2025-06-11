import os
import pickle
from deepface import DeepFace
import uuid

# Definições de caminho para imagens e embeddings
# EMBEDDINGS_PATH e IMG_SAVE_PATH precisam ser acessíveis de forma consistente
# Como services está dentro de app, vamos para 'app/..' (volta para 'backend/')
# e depois para 'data'
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data')
IMG_SAVE_PATH = os.path.join(DATA_DIR, 'student_images')
TEMP_IMG_DIR = os.path.join(DATA_DIR, 'temp_recognition_images')
EMBEDDINGS_PATH = os.path.join(DATA_DIR, 'embeddings.pkl')

if not os.path.exists(IMG_SAVE_PATH):
    os.makedirs(IMG_SAVE_PATH)
if not os.path.exists(TEMP_IMG_DIR):
    os.makedirs(TEMP_IMG_DIR)

RECOGNITION_MODEL = "ArcFace"
DETECTOR_MODEL = "ssd"

# Lista global para armazenar os embeddings em memória
REGISTERED_STUDENTS_EMBEDDINGS = []

def load_embeddings():
    global REGISTERED_STUDENTS_EMBEDDINGS
    try:
        if os.path.exists(EMBEDDINGS_PATH):
            with open(EMBEDDINGS_PATH, 'rb') as f:
                REGISTERED_STUDENTS_EMBEDDINGS = pickle.load(f)
            print(f"Embeddings carregados de {EMBEDDINGS_PATH} (services/face_recognition.py)")
        else:
            print("Nenhum arquivo de embeddings encontrado. Será criado ao cadastrar o primeiro aluno (services/face_recognition.py).")
    except Exception as e:
        print(f"Erro ao carregar embeddings (services/face_recognition.py): {e}. Iniciando lista vazia.")
        REGISTERED_STUDENTS_EMBEDDINGS = []

def save_embeddings():
    try:
        with open(EMBEDDINGS_PATH, 'wb') as f:
            pickle.dump(REGISTERED_STUDENTS_EMBEDDINGS, f)
        print(f"Embeddings salvos em {EMBEDDINGS_PATH} (services/face_recognition.py)")
    except Exception as e:
        print(f"Erro ao salvar embeddings (services/face_recognition.py): {e}")

def generate_embedding(image_path):
    try:
        embeddings = DeepFace.represent(
            img_path=image_path,
            model_name=RECOGNITION_MODEL,
            detector_backend=DETECTOR_MODEL,
            enforce_detection=True
        )
        if embeddings:
            return embeddings[0]["embedding"]
        return None
    except Exception as e:
        print(f"Erro ao gerar embedding DeepFace para {image_path} (services/face_recognition.py): {e}")
        return None

def add_student_embedding(name, matricula, embedding, image_path, school_unit_id):
    global REGISTERED_STUDENTS_EMBEDDINGS
    REGISTERED_STUDENTS_EMBEDDINGS.append({
        "name": name,
        "matricula": matricula,
        "embedding": embedding,
        "image_path": image_path,
        "school_unit_id": school_unit_id
    })
    save_embeddings()

def recognize_face_from_image(image_bytes):
    temp_img_path = None
    try:
        temp_img_path = os.path.join(TEMP_IMG_DIR, f"temp_recognition_{uuid.uuid4().hex}.png")
        with open(temp_img_path, 'wb') as f:
            f.write(image_bytes)
        print(f"Imagem temporária de reconhecimento salva em: {temp_img_path} (services/face_recognition.py)")

        if not REGISTERED_STUDENTS_EMBEDDINGS:
            return {"recognized": False, "message": "Nenhum aluno cadastrado para reconhecimento."}

        # Tenta detectar faces na imagem de entrada
        detected_faces = DeepFace.represent(
            img_path=temp_img_path,
            model_name=RECOGNITION_MODEL,
            detector_backend=DETECTOR_MODEL,
            enforce_detection=False # Permite que o DeepFace continue mesmo que não detecte um rosto com alta confiança
        )
        
        recognized_student = None
        if detected_faces:
            # Para cada rosto detectado na imagem de entrada (poderia ser mais de um, embora o foco seja um por vez)
            for face_data in detected_faces:
                # Compara o embedding do rosto detectado com todos os alunos registrados
                # DeepFace.find é mais eficiente para procurar em um banco de dados de rostos
                # No seu caso, REGISTERED_STUDENTS_EMBEDDINGS já tem os embeddings pré-computados
                # Então, podemos fazer a verificação direta
                
                # Para simplificar a migração e manter a lógica de `verify` com `img1_path` e `img2_path`
                # vamos usar a mesma lógica que estava no main.py, mas mais otimizada se você tiver muitos alunos.
                
                # Uma abordagem mais otimizada seria criar um DataFrame de embeddings e usar DeepFace.find
                # df = pd.DataFrame(REGISTERED_STUDENTS_EMBEDDINGS)
                # results = DeepFace.find(img_path=temp_img_path, db_path=IMG_SAVE_PATH, model_name=RECOGNITION_MODEL, detector_backend=DETECTOR_MODEL, distance_metric="cosine", enforce_detection=False)
                # No entanto, a lógica atual de loop e verify também funciona para um número moderado de alunos.

                min_distance = float('inf')
                best_match = None
                
                for student_rec in REGISTERED_STUDENTS_EMBEDDINGS:
                    # Verifica se a imagem do aluno cadastrado existe
                    if not os.path.exists(student_rec["image_path"]):
                        print(f"AVISO: Imagem do aluno {student_rec['matricula']} não encontrada em: {student_rec['image_path']} (services/face_recognition.py)")
                        continue # Pula este aluno se a imagem não for encontrada

                    verification_result = DeepFace.verify(
                        img1_path=temp_img_path,
                        img2_path=student_rec["image_path"],
                        model_name=RECOGNITION_MODEL,
                        detector_backend=DETECTOR_MODEL,
                        enforce_detection=False # Já detectamos uma face, mas podemos relaxar para o segundo img
                    )
                    
                    if verification_result["verified"]:
                        distance = verification_result["distance"]
                        if distance < min_distance: # Queremos o menor distance para o melhor match
                            min_distance = distance
                            best_match = student_rec
                            # Assim que encontrar um match verificado, pode parar ou continuar buscando o melhor.
                            # Se você quer apenas o primeiro match verificado, adicione 'break' aqui
                            recognized_student = best_match
                            break # Encontrou um match, não precisa verificar os outros
            
        if recognized_student:
            return {"recognized": True, "student": recognized_student}
        else:
            return {"recognized": False, "message": "Nenhum aluno reconhecido."}

    except Exception as e:
        print(f"Erro no reconhecimento facial (services/face_recognition.py): {e}")
        import traceback
        traceback.print_exc()
        return {"recognized": False, "error": f"Erro interno no reconhecimento: {str(e)}"}
    finally:
        if temp_img_path and os.path.exists(temp_img_path):
            os.remove(temp_img_path)

# Carrega os embeddings quando o módulo é importado
load_embeddings()