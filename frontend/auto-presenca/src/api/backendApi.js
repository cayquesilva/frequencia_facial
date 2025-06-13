// A variável de ambiente VITE_API_BASE_URL será injetada pelo Vite durante o build de produção.
// Em desenvolvimento (npm run dev), import.meta.env.VITE_API_BASE_URL pode ser undefined,
// então usamos um fallback para o localhost.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000/api';

export async function fetchSchoolUnits() {
    try {
        const response = await fetch(`${API_BASE_URL}/school_units`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Erro ao carregar unidades escolares:', error);
        throw error;
    }
}

export async function createSchoolUnit(unitData) {
    try {
        const response = await fetch(`${API_BASE_URL}/school_units`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(unitData)
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Erro desconhecido ao criar unidade escolar.');
        }
        return data;
    } catch (error) {
        console.error('Erro ao criar unidade escolar:', error);
        throw error;
    }
}

export async function registerStudent(studentData) {
    try {
        const response = await fetch(`${API_BASE_URL}/students`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(studentData)
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Erro desconhecido ao cadastrar.');
        }
        return data;
    } catch (error) {
        console.error('Erro de rede ou ao enviar cadastro:', error);
        throw error;
    }
}

export async function recognizeFace(imageDataURL) {
    try {
        const response = await fetch(`${API_BASE_URL}/recognize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageDataURL })
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Erro desconhecido ao reconhecer.');
        }
        return data;
    } catch (error) {
        console.error('Erro de rede ou ao enviar frame para reconhecimento:', error);
        throw error;
    }
}

export async function fetchAttendances(params) {
    const query = new URLSearchParams(params).toString();
    try {
        const response = await fetch(`${API_BASE_URL}/attendances?${query}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Erro ao buscar logs de frequência:', error);
        throw error;
    }
}

export async function exportAttendancesCsv(params) {
    const query = new URLSearchParams(params).toString();
    // Abre em uma nova aba para iniciar o download
    window.open(`<span class="math-inline">\{API\_BASE\_URL\}/attendances/export\_csv?</span>{query}`, '_blank');
}

export async function fetchStudentsBySchool(schoolUnitId) {
    try {
        const response = await fetch(`${API_BASE_URL}/students_by_school/${schoolUnitId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Erro ao carregar alunos por unidade escolar:', error);
        throw error;
    }
}

export async function getStudentDetails(matricula) {
    try {
        const response = await fetch(`${API_BASE_URL}/students/${matricula}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Erro ao buscar detalhes do aluno:', error);
        throw error;
    }
}

export async function updateStudentImage(matricula, imageDataURL) {
    try {
        const response = await fetch(`${API_BASE_URL}/students/${matricula}/image`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageDataURL })
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Erro desconhecido ao atualizar foto.');
        }
        return data;
    } catch (error) {
        console.error('Erro de rede ou ao enviar nova foto:', error);
        throw error;
    }
}

export async function updateStudentInfo(matricula, studentData) {
    try {
        const response = await fetch(`${API_BASE_URL}/students/${matricula}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(studentData)
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Erro desconhecido ao atualizar dados do aluno.');
        }
        return data;
    } catch (error) {
        console.error('Erro de rede ou ao atualizar dados do aluno:', error);
        throw error;
    }
}

export async function deleteStudent(matricula) {
    try {
        const response = await fetch(`${API_BASE_URL}/students/${matricula}`, {
            method: 'DELETE'
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Erro desconhecido ao deletar aluno.');
        }
        return data;
    } catch (error) {
        console.error('Erro de rede ou ao deletar aluno:', error);
        throw error;
    }
}

export function getStudentImageUrl(matricula, relativePathIncludingFilename) {
    // Retorna a URL completa para a imagem do estudante
    // Ex: https://apifreq.simplisoft.com.br/api/student_images/12345/foto.png
    return `${API_BASE_URL}/student_images/${relativePathIncludingFilename}`;
}