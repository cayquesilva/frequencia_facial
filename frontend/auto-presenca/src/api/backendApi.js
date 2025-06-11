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

// ... adicione mais funções para exportar CSV, atualizar/deletar unidades, etc.