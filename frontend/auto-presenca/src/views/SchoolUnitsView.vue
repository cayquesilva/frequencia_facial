<template>
    <div class="school-units">
      <h1>Sistema de Frequência Escolar - Gerenciar Unidades Escolares</h1>
  
      <div class="section">
        <h2>Cadastrar Nova Unidade Escolar</h2>
        <form @submit.prevent="saveSchoolUnit" style="margin-top: 20px;">
          <div class="form-group">
            <label for="unitName">Nome da Unidade:</label>
            <input type="text" id="unitName" v-model="unit.name" required>
          </div>
          <div class="form-group">
            <label for="ipRangeStart">IP Inicial (Opcional):</label>
            <input type="text" id="ipRangeStart" v-model="unit.ip_range_start" placeholder="Ex: 192.168.1.1">
          </div>
          <div class="form-group">
            <label for="ipRangeEnd">IP Final (Opcional):</label>
            <input type="text" id="ipRangeEnd" v-model="unit.ip_range_end" placeholder="Ex: 192.168.1.254">
          </div>
          <button type="submit">Salvar Unidade</button>
        </form>
      </div>
  
      <div class="section" style="margin-top: 30px;">
        <h2>Unidades Escolares Cadastradas</h2>
        <table class="school-units-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nome da Unidade</th>
              <th>IP Inicial</th>
              <th>IP Final</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loadingUnits">
              <td colspan="5" class="no-records">Carregando unidades...</td>
            </tr>
            <tr v-else-if="schoolUnits.length === 0">
              <td colspan="5" class="no-records">Nenhuma unidade escolar cadastrada.</td>
            </tr>
            <tr v-else v-for="unit in schoolUnits" :key="unit.id">
              <td>{{ unit.id }}</td>
              <td>{{ unit.name }}</td>
              <td>{{ unit.ip_range_start || 'N/A' }}</td>
              <td>{{ unit.ip_range_end || 'N/A' }}</td>
              <td>
                <button @click="alert('Funcionalidade de Edição (MVP futuro)!')">Editar</button>
                <button @click="alert('Funcionalidade de Exclusão (MVP futuro)!')">Excluir</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, reactive, onMounted } from 'vue';
  import { fetchSchoolUnits, createSchoolUnit } from '../api/backendApi'; // Importar as funções de API
  
  export default {
    name: 'SchoolUnitsView',
    setup() {
      const schoolUnits = ref([]);
      const loadingUnits = ref(true);
      const unit = reactive({
        name: '',
        ip_range_start: '',
        ip_range_end: ''
      });
  
      const fetchSchoolUnitsData = async () => {
        loadingUnits.value = true;
        try {
          schoolUnits.value = await fetchSchoolUnits();
        } catch (error) {
          console.error('Erro ao buscar unidades escolares:', error);
          alert('Erro ao carregar unidades escolares. Verifique o console.');
          schoolUnits.value = []; // Limpa as unidades em caso de erro
        } finally {
          loadingUnits.value = false;
        }
      };
  
      const saveSchoolUnit = async () => {
        if (!unit.name) {
          alert('O nome da unidade é obrigatório.');
          return;
        }
  
        try {
          const response = await createSchoolUnit({
            name: unit.name,
            ip_range_start: unit.ip_range_start || null, // Envia null se vazio
            ip_range_end: unit.ip_range_end || null     // Envia null se vazio
          });
          alert('Unidade escolar cadastrada com sucesso!');
          console.log('Unidade cadastrada:', response);
          // Limpar o formulário
          unit.name = '';
          unit.ip_range_start = '';
          unit.ip_range_end = '';
          fetchSchoolUnitsData(); // Recarrega a lista
        } catch (error) {
          alert('Erro ao cadastrar unidade: ' + error.message);
        }
      };
  
      onMounted(() => {
        fetchSchoolUnitsData(); // Carrega as unidades ao carregar a página
      });
  
      return {
        schoolUnits,
        loadingUnits,
        unit,
        fetchSchoolUnits: fetchSchoolUnitsData, // Renomeado para evitar conflito com a função de API
        saveSchoolUnit
      };
    }
  };
  </script>
  
  <style scoped>
  /* Estilos específicos para school_units.html */
  .section {
    margin-top: 30px;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background-color: #f9f9f9;
  }
  
  .form-group {
      margin-bottom: 15px;
      text-align: left;
  }
  
  .form-group label {
      display: block;
      margin-bottom: 5px;
      font-weight: bold;
  }
  
  .form-group input[type="text"] {
      width: calc(100% - 22px);
      padding: 10px;
      border: 1px solid #ccc;
      border-radius: 4px;
      font-size: 16px;
  }
  
  button {
      background-color: #007bff;
      color: white;
      padding: 10px 20px;
      border: none;
      border-radius: 5px;
      cursor: pointer;
      font-size: 16px;
      margin-top: 15px;
      transition: background-color 0.3s ease;
  }
  
  button:hover:not(:disabled) {
      background-color: #0056b3;
  }
  
  button:disabled {
      background-color: #cccccc;
      cursor: not-allowed;
  }
  
  .school-units-table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
  }
  .school-units-table th, .school-units-table td {
      border: 1px solid #ddd;
      padding: 8px;
      text-align: left;
  }
  .school-units-table th {
      background-color: #f2f2f2;
      font-weight: bold;
  }
  .no-records {
      text-align: center;
      padding: 20px;
      color: #555;
  }
  </style>