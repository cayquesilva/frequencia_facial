<template>
    <div class="logs">
      <h1>Sistema de Frequência Escolar - Logs de Acesso</h1>
  
      <div class="section">
        <h2>Registros de Frequência</h2>
  
        <div class="filters-container">
          <div>
            <label for="startDate">Data Início:</label>
            <input type="date" id="startDate" v-model="filters.startDate">
          </div>
          <div>
            <label for="endDate">Data Fim:</label>
            <input type="date" id="endDate" v-model="filters.endDate">
          </div>
          <div>
            <label for="filterTurma">Turma:</label>
            <select id="filterTurma" v-model="filters.turma">
              <option value="">Todas</option>
              <option value="anos_iniciais">Anos Iniciais</option>
              <option value="anos_finais">Anos Finais</option>
              <option value="eja">EJA</option>
            </select>
          </div>
          <div>
            <label for="filterSchoolUnit">Unidade Escolar:</label>
            <select id="filterSchoolUnit" v-model.number="filters.school_unit_id">
              <option value="">Todas</option>
              <option v-for="unit in schoolUnits" :key="unit.id" :value="unit.id">
                {{ unit.name }}
              </option>
            </select>
          </div>
          <div>
            <label for="searchQuery">Pesquisar (Matrícula/Nome):</label>
            <input type="text" id="searchQuery" v-model="filters.searchQuery" placeholder="Ex: 12345 ou João">
          </div>
          <button @click="fetchAttendances">Aplicar Filtros</button>
          <button @click="exportCsv">Exportar CSV</button>
        </div>
  
        <table class="logs-table">
          <thead>
            <tr>
              <th>ID Reg.</th>
              <th>Nome Aluno</th>
              <th>Matrícula</th>
              <th>Turma</th>
              <th>Turno</th>
              <th>Unidade Escolar</th>
              <th>Data/Hora</th>
              <th>IP Cliente</th>
            </tr>
          </thead>
          <tbody id="attendanceLogsBody">
            <tr v-if="loadingLogs">
              <td colspan="8" class="no-records">Carregando registros...</td>
            </tr>
            <tr v-else-if="attendances.length === 0">
              <td colspan="8" class="no-records">Nenhum registro encontrado.</td>
            </tr>
            <tr v-else v-for="log in attendances" :key="log.id">
              <td>{{ log.id }}</td>
              <td>{{ log.name }}</td>
              <td>{{ log.matricula }}</td>
              <td>{{ log.turma }}</td>
              <td>{{ log.turno }}</td>
              <td>{{ log.school_unit_name || 'N/A' }}</td>
              <td>{{ new Date(log.timestamp).toLocaleString('pt-BR') }}</td>
              <td>{{ log.client_ip || 'N/A' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </template>
  
  <script>
    import { ref, reactive, onMounted } from 'vue';
    // Importar as funções de API, incluindo a nova para exportação CSV
    import { fetchSchoolUnits, fetchAttendances, exportAttendancesCsv } from '../api/backendApi'; // <-- AQUI A MUDANÇA
  
  export default {
    name: 'LogsView',
    setup() {
      const attendances = ref([]);
      const schoolUnits = ref([]);
      const loadingLogs = ref(true);
      const filters = reactive({
        startDate: '',
        endDate: '',
        turma: '',
        school_unit_id: null,
        searchQuery: ''
      });
  
      const loadSchoolUnitsForFilter = async () => {
        try {
          schoolUnits.value = await fetchSchoolUnits();
        } catch (error) {
          alert('Erro ao carregar unidades escolares para filtro. Verifique o console.'+error);
        }
      };
  
      const fetchAttendancesData = async () => {
        loadingLogs.value = true;
        try {
          const params = {
            start_date: filters.startDate,
            end_date: filters.endDate,
            turma: filters.turma,
            school_unit_id: filters.school_unit_id,
            search_query: filters.searchQuery
          };
          // Filtra parâmetros vazios para não enviar para a API
          const cleanedParams = Object.fromEntries(
            Object.entries(params).filter(([, value]) => value !== '' && value !== null)
          );
  
          attendances.value = await fetchAttendances(cleanedParams);
        } catch (error) {
          console.error('Erro ao buscar logs de frequência:', error);
          alert('Erro ao carregar logs de frequência. Verifique o console.');
          attendances.value = []; // Limpa os logs em caso de erro
        } finally {
          loadingLogs.value = false;
        }
      };
  
      const exportCsv = () => {
        const params = {
          start_date: filters.startDate,
          end_date: filters.endDate,
          turma: filters.turma,
          school_unit_id: filters.school_unit_id,
          search_query: filters.searchQuery
        };

        // Chama a função exportada do backendApi.js
        exportAttendancesCsv(params); // <-- AQUI A MUDANÇA PRINCIPAL
      };
  
      onMounted(() => {
        loadSchoolUnitsForFilter();
        fetchAttendancesData(); // Carrega os logs ao carregar a página
      });
  
      return {
        attendances,
        schoolUnits,
        loadingLogs,
        filters,
        fetchAttendances: fetchAttendancesData, // Renomeado para evitar conflito com a função de API
        exportCsv
      };
    }
  };
  </script>
  
  <style scoped>
  /* Estilos específicos para logs.html */
  .section {
    margin-top: 30px;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background-color: #f9f9f9;
  }
  
  .filters-container {
      display: flex;
      flex-wrap: wrap;
      gap: 15px;
      margin-bottom: 20px;
      padding: 15px;
      border: 1px solid #e0e0e0;
      border-radius: 5px;
      background-color: #f9f9f9;
  }
  .filters-container label {
      font-weight: bold;
      margin-right: 5px;
  }
  .filters-container input[type="date"],
  .filters-container input[type="text"],
  .filters-container select {
      padding: 8px;
      border: 1px solid #ccc;
      border-radius: 4px;
  }
  .filters-container button {
      padding: 10px 15px;
      background-color: #007bff;
      color: white;
      border: none;
      border-radius: 5px;
      cursor: pointer;
      font-size: 14px;
  }
  .filters-container button:hover {
      background-color: #0056b3;
  }
  .logs-table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
  }
  .logs-table th, .logs-table td {
      border: 1px solid #ddd;
      padding: 8px;
      text-align: left;
  }
  .logs-table th {
      background-color: #f2f2f2;
      font-weight: bold;
  }
  .no-records {
      text-align: center;
      padding: 20px;
      color: #555;
  }
  </style>