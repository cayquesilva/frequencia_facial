import sqlite3
import os
from datetime import datetime, timedelta

# Definições de caminho para o DB
# DATA_DIR precisa ser acessível de forma consistente
# Como services está dentro de app, vamos para 'app/..' (volta para 'backend/')
# e depois para 'data'
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data')
DATABASE = os.path.join(DATA_DIR, 'attendance.db')

# Garante que o diretório de dados exista
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

COOLDOWN_PERIOD_MINUTES = 30 # Período em minutos para evitar presenças duplicadas

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row # Permite acessar colunas por nome
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            matricula TEXT UNIQUE NOT NULL,
            turma TEXT NOT NULL,
            turno TEXT NOT NULL,
            idade INTEGER NOT NULL,
            image_path TEXT NOT NULL,
            school_unit_id INTEGER,
            FOREIGN KEY (school_unit_id) REFERENCES school_units (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_matricula TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            client_ip TEXT,
            FOREIGN KEY (student_matricula) REFERENCES students (matricula)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS school_units (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            ip_range_start TEXT,
            ip_range_end TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("Banco de dados inicializado/verificado (services/database.py)!")

def register_attendance_in_db(matricula, client_ip=None):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        current_time = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO attendances (student_matricula, timestamp, client_ip)
            VALUES (?, ?, ?)
        ''', (matricula, current_time, client_ip))
        conn.commit()
        print(f"Frequência registrada para {matricula} de IP {client_ip} em {current_time} (services/database.py)")
        return True
    except Exception as e:
        conn.rollback()
        print(f"Erro ao registrar frequência para {matricula} (services/database.py): {e}")
        return False
    finally:
        conn.close()

def is_duplicate_attendance(matricula, cooldown_minutes=COOLDOWN_PERIOD_MINUTES):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        limit_time = datetime.now() - timedelta(minutes=cooldown_minutes)
        
        cursor.execute('''
            SELECT COUNT(*) FROM attendances
            WHERE student_matricula = ? AND timestamp >= ?
        ''', (matricula, limit_time.isoformat()))
        
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        print(f"Erro ao verificar duplicidade de frequência (services/database.py) para {matricula}: {e}")
        return False
    finally:
        conn.close()

# Funções para consultar alunos e unidades, se necessário para outras partes do backend
def get_student_by_matricula(matricula):
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE matricula = ?', (matricula,)).fetchone()
    conn.close()
    return student

def get_all_students():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()
    return students

def add_student_to_db(name, matricula, turma, turno, idade, image_path, school_unit_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO students (name, matricula, turma, turno, idade, image_path, school_unit_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, matricula, turma, turno, idade, image_path, school_unit_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # Matrícula já existe
    except Exception as e:
        print(f"Erro ao adicionar aluno ao DB: {e}")
        return False
    finally:
        conn.close()

def get_students_by_school_unit(school_unit_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = '''
        SELECT 
            s.id, 
            s.name, 
            s.matricula, 
            s.turma, 
            s.turno, 
            s.idade, 
            s.image_path,
            su.name AS school_unit_name
        FROM students AS s
        LEFT JOIN school_units AS su ON s.school_unit_id = su.id
        WHERE s.school_unit_id = ?
    '''
    students = cursor.execute(query, (school_unit_id,)).fetchall()
    conn.close()
    return [dict(s) for s in students]

def get_student_details_by_matricula(matricula):
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE matricula = ?', (matricula,)).fetchone()
    conn.close()
    return dict(student) if student else None

def update_student_image_path(matricula, new_image_path):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE students SET image_path = ? WHERE matricula = ?
        ''', (new_image_path, matricula))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Erro ao atualizar imagem do aluno {matricula} no DB: {e}")
        return False
    finally:
        conn.close()

def update_student_data(matricula, name, turma, turno, idade, school_unit_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE students SET name = ?, turma = ?, turno = ?, idade = ?, school_unit_id = ?
            WHERE matricula = ?
        ''', (name, turma, turno, idade, school_unit_id, matricula))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Erro ao atualizar dados do aluno {matricula} no DB: {e}")
        return False
    finally:
        conn.close()

# Pode precisar de uma função para deletar aluno, se desejar
def delete_student_by_matricula(matricula):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM students WHERE matricula = ?', (matricula,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Erro ao deletar aluno {matricula} do DB: {e}")
        return False
    finally:
        conn.close()
        
def get_school_unit(unit_id):
    conn = get_db_connection()
    unit = conn.execute('SELECT * FROM school_units WHERE id = ?', (unit_id,)).fetchone()
    conn.close()
    return unit

def get_all_school_units():
    conn = get_db_connection()
    units = conn.execute('SELECT * FROM school_units ORDER BY name').fetchall()
    conn.close()
    return units

def add_school_unit_to_db(name, ip_range_start, ip_range_end):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO school_units (name, ip_range_start, ip_range_end)
            VALUES (?, ?, ?)
        ''', (name, ip_range_start, ip_range_end))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None # Unidade já existe
    except Exception as e:
        print(f"Erro ao adicionar unidade escolar ao DB: {e}")
        return None
    finally:
        conn.close()

def update_school_unit_in_db(unit_id, name, ip_range_start, ip_range_end):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE school_units
            SET name = ?, ip_range_start = ?, ip_range_end = ?
            WHERE id = ?
        ''', (name, ip_range_start, ip_range_end, unit_id))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao atualizar unidade escolar no DB: {e}")
        return False
    finally:
        conn.close()

def delete_school_unit_from_db(unit_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM school_units WHERE id = ?', (unit_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao deletar unidade escolar do DB: {e}")
        return False
    finally:
        conn.close()

def get_attendances_from_db(start_date_str, end_date_str, turma, search_query, school_unit_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
        SELECT 
            a.id, 
            s.name, 
            s.matricula, 
            s.turma, 
            s.turno,
            a.timestamp,
            a.client_ip,
            su.name AS school_unit_name
        FROM attendances AS a
        JOIN students AS s ON a.student_matricula = s.matricula
        LEFT JOIN school_units AS su ON s.school_unit_id = su.id
        WHERE 1=1
    '''
    params = []

    if start_date_str:
        start_datetime = datetime.strptime(start_date_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
        query += " AND a.timestamp >= ?"
        params.append(start_datetime.isoformat())

    if end_date_str:
        end_datetime = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
        query += " AND a.timestamp <= ?"
        params.append(end_datetime.isoformat())
    
    if turma:
        query += " AND s.turma = ?"
        params.append(turma)

    if search_query:
        query += " AND (s.matricula LIKE ? OR s.name LIKE ?)"
        params.append(f"%{search_query}%")
        params.append(f"%{search_query}%")
    
    if school_unit_id:
        query += " AND s.school_unit_id = ?"
        params.append(school_unit_id)

    query += " ORDER BY a.timestamp DESC"

    attendances = cursor.execute(query, params).fetchall()
    conn.close()
    return [dict(att) for att in attendances]