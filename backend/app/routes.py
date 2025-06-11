from flask import request, jsonify, send_file, Blueprint
import os
import base64
import uuid
import json
from datetime import datetime, date
from io import StringIO, BytesIO
import traceback

# Importar serviços
from app.services.database import (
    add_student_to_db, get_all_students, get_attendances_from_db,
    register_attendance_in_db, is_duplicate_attendance,
    add_school_unit_to_db, get_all_school_units, update_school_unit_in_db,
    delete_school_unit_from_db
)
from app.services.face_recognition import (
    generate_embedding, add_student_embedding,
    recognize_face_from_image, REGISTERED_STUDENTS_EMBEDDINGS,
    IMG_SAVE_PATH, TEMP_IMG_DIR
)

# Crie um Blueprint para suas rotas
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/')
def home():
    return "Backend do Sistema de Frequência Escolar está rodando!"

@api_bp.route('/students', methods=['POST'])
def register_student():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Nenhum dado JSON recebido"}), 400

    name = data.get('name')
    matricula = data.get('matricula')
    turma = data.get('turma')
    turno = data.get('turno')
    idade = data.get('idade')
    image_data_url = data.get('image')
    school_unit_id = data.get('school_unit_id')

    if not all([name, matricula, turma, turno, idade, image_data_url]):
        return jsonify({"error": "Dados incompletos. Nome, matrícula, turma, turno, idade e imagem são obrigatórios."}), 400

    image_bytes = None
    final_image_path = None
    try:
        header, encoded_data = image_data_url.split(',', 1)
        image_bytes = base64.b64decode(encoded_data)
        
        student_img_dir = os.path.join(IMG_SAVE_PATH, matricula)
        if not os.path.exists(student_img_dir):
            os.makedirs(student_img_dir)
        
        image_filename = f"{matricula}_{uuid.uuid4().hex}.png"
        final_image_path = os.path.join(student_img_dir, image_filename)
        
        with open(final_image_path, 'wb') as f:
            f.write(image_bytes)
        print(f"Imagem de cadastro salva em: {final_image_path}")

    except Exception as e:
        print(f"Erro ao salvar imagem para cadastro: {e}")
        return jsonify({"error": "Erro ao processar imagem."}), 500

    # Adicionar aluno ao DB
    student_added = add_student_to_db(name, matricula, turma, turno, idade, final_image_path, school_unit_id)
    if not student_added:
        # Se add_student_to_db retornar False (por matrícula duplicada ou outro erro)
        if os.path.exists(final_image_path):
            os.remove(final_image_path) # Remove a imagem se o DB não aceitar
        return jsonify({"error": f"Matrícula '{matricula}' já existe ou erro no DB."}), 409
    
    # Gerar e salvar embedding
    try:
        embedding = generate_embedding(final_image_path)
        
        if embedding is not None:
            add_student_embedding(name, matricula, embedding, final_image_path, school_unit_id)
            print(f"Embedding para {name} ({matricula}) gerado e salvo. Total de alunos com embedding: {len(REGISTERED_STUDENTS_EMBEDDINGS)}")
        else:
            print(f"Atenção: Não foi possível gerar embedding para {name} na imagem de cadastro.")

    except Exception as e_deepface:
        print(f"Erro ao gerar embedding DeepFace para {name}: {e_deepface}")

    print(f"Aluno {name} ({matricula}) cadastrado com sucesso.")
    return jsonify({"message": "Aluno cadastrado com sucesso!", "image_path": final_image_path}), 201


@api_bp.route('/recognize', methods=['POST'])
def recognize_face():
    client_ip = request.remote_addr 
    print(f"Requisição de reconhecimento recebida do IP: {client_ip}")

    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({"error": "Nenhum dado de imagem recebido."}), 400

    image_data_url = data['image']
    try:
        header, encoded_data = image_data_url.split(',', 1)
        image_bytes = base64.b64decode(encoded_data)
        
        recognition_result = recognize_face_from_image(image_bytes)
        
        if recognition_result["recognized"]:
            recognized_student = recognition_result["student"]

            # --- VERIFICAÇÃO DE DUPLICIDADE NO BACKEND ---
            if is_duplicate_attendance(recognized_student["matricula"]):
                print(f"Frequência duplicada detectada para {recognized_student['matricula']} dentro do período de cooldown.")
                return jsonify({
                    "recognized": True,
                    "name": recognized_student["name"],
                    "matricula": recognized_student["matricula"],
                    "attendance_recorded": False, 
                    "message": "Frequência já registrada recentemente."
                }), 200
            # --- FIM DA VERIFICAÇÃO DE DUPLICIDADE ---
            
            attendance_recorded = register_attendance_in_db(recognized_student["matricula"], client_ip) 
            return jsonify({
                "recognized": True,
                "name": recognized_student["name"],
                "matricula": recognized_student["matricula"],
                "attendance_recorded": attendance_recorded,
                "message": "Frequência registrada com sucesso!" if attendance_recorded else "Erro ao registrar frequência."
            }), 200
        else:
            return jsonify({"recognized": False, "message": recognition_result.get("message", "Nenhum aluno reconhecido.")}), 200

    except Exception as e:
        print(f"Erro no reconhecimento facial na rota: {e}")
        traceback.print_exc() 
        return jsonify({"error": f"Erro interno no reconhecimento: {str(e)}"}), 500

# --- Endpoints de Unidades Escolares ---
@api_bp.route('/school_units', methods=['POST'])
def create_school_unit():
    data = request.get_json()
    name = data.get('name')
    ip_range_start = data.get('ip_range_start')
    ip_range_end = data.get('ip_range_end')

    if not name:
        return jsonify({"error": "Nome da unidade escolar é obrigatório."}), 400
    
    unit_id = add_school_unit_to_db(name, ip_range_start, ip_range_end)
    if unit_id is None:
        return jsonify({"error": f"Unidade escolar '{name}' já existe ou erro no DB."}), 409
    
    return jsonify({"message": "Unidade escolar cadastrada com sucesso!", "id": unit_id}), 201

@api_bp.route('/school_units', methods=['GET'])
def get_school_units():
    units = get_all_school_units()
    return jsonify([dict(unit) for unit in units]), 200

@api_bp.route('/school_units/<int:unit_id>', methods=['PUT'])
def update_school_unit_route(unit_id):
    data = request.get_json()
    name = data.get('name')
    ip_range_start = data.get('ip_range_start')
    ip_range_end = data.get('ip_range_end')

    if not name:
        return jsonify({"error": "Nome da unidade escolar é obrigatório."}), 400

    updated = update_school_unit_in_db(unit_id, name, ip_range_start, ip_range_end)
    if not updated:
        return jsonify({"error": "Unidade escolar não encontrada ou erro ao atualizar."}), 404
    return jsonify({"message": "Unidade escolar atualizada com sucesso!"}), 200

@api_bp.route('/school_units/<int:unit_id>', methods=['DELETE'])
def delete_school_unit_route(unit_id):
    deleted = delete_school_unit_from_db(unit_id)
    if not deleted:
        return jsonify({"error": "Unidade escolar não encontrada ou erro ao deletar."}), 404
    return jsonify({"message": "Unidade escolar deletada com sucesso!"}), 200


@api_bp.route('/attendances', methods=['GET'])
def get_attendances():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    turma = request.args.get('turma')
    search_query = request.args.get('search_query')
    school_unit_id = request.args.get('school_unit_id')

    try:
        attendances = get_attendances_from_db(start_date_str, end_date_str, turma, search_query, school_unit_id)
        return jsonify(attendances), 200
    except Exception as e:
        print(f"Erro ao consultar frequências: {e}")
        traceback.print_exc() 
        return jsonify({"error": "Erro ao consultar frequências."}), 500

@api_bp.route('/attendances/export_csv', methods=['GET'])
def export_attendances_csv():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    turma = request.args.get('turma')
    search_query = request.args.get('search_query')
    school_unit_id = request.args.get('school_unit_id')

    try:
        attendances_data = get_attendances_from_db(start_date_str, end_date_str, turma, search_query, school_unit_id)

        si = StringIO(newline='') 
        cw = csv.writer(si)

        cw.writerow(['ID Registro', 'Nome Aluno', 'Matricula', 'Turma', 'Turno', 'Data/Hora', 'IP Cliente', 'Unidade Escolar'])

        for att in attendances_data:
            row_data = [
                str(att['id']),
                str(att['name']),
                str(att['matricula']),
                str(att['turma']),
                str(att['turno']),
                str(att['timestamp']),
                str(att['client_ip'] or 'N/A'),
                str(att['school_unit_name'] or 'N/A')
            ]
            cw.writerow(row_data)
        
        output_string = si.getvalue()
        output_bytes_buffer = BytesIO(output_string.encode('utf-8'))
        
        return send_file(
            output_bytes_buffer,
            mimetype='text/csv; charset=utf-8', 
            as_attachment=True,
            download_name=f'frequencias_{date.today().isoformat()}.csv'
        )
    except Exception as e:
        print(f"Erro ao exportar frequências para CSV: {e}")
        traceback.print_exc() 
        return jsonify({"error": "Erro ao exportar frequências."}), 500