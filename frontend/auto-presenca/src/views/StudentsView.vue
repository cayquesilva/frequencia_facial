<template>
    <div class="students-management">
      <h1>Sistema de Frequência Escolar - Gerenciar Estudantes</h1>
  
      <div class="section">
        <h2>Filtrar por Unidade Escolar</h2>
        <div class="filter-controls">
          <label for="filterStudentSchoolUnit">Unidade Escolar:</label>
          <select id="filterStudentSchoolUnit" v-model.number="selectedSchoolUnitId" @change="loadStudents">
            <option value="">Todas as Unidades</option>
            <option v-for="unit in schoolUnits" :key="unit.id" :value="unit.id">
              {{ unit.name }}
            </option>
          </select>
          <button @click="loadStudents">Buscar Alunos</button>
        </div>
  
        <table class="students-table" style="margin-top: 20px;">
          <thead>
            <tr>
              <th>Matrícula</th>
              <th>Nome</th>
              <th>Turma</th>
              <th>Turno</th>
              <th>Unidade Escolar</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loadingStudents">
              <td colspan="6" class="no-records">Carregando alunos...</td>
            </tr>
            <tr v-else-if="students.length === 0">
              <td colspan="6" class="no-records">Nenhum aluno encontrado para os filtros.</td>
            </tr>
            <tr v-else v-for="student in students" :key="student.matricula">
              <td>{{ student.matricula }}</td>
              <td>{{ student.name }}</td>
              <td>{{ student.turma }}</td>
              <td>{{ student.turno }}</td>
              <td>{{ student.school_unit_name || 'N/A' }}</td>
              <td>
                <button @click="openEditModal(student)">Editar</button>
                <button @click="confirmDeleteStudent(student)">Excluir</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
  
      <div v-if="showEditModal" class="modal-overlay">
        <div class="modal-content">
          <h3>Editar Aluno: {{ currentStudent.name }} ({{ currentStudent.matricula }})</h3>
          <form @submit.prevent="saveEditedStudent">
            <div class="form-group">
              <label for="editStudentName">Nome:</label>
              <input type="text" id="editStudentName" v-model="currentStudent.name" required>
            </div>
            <div class="form-group">
              <label for="editStudentClass">Turma:</label>
              <select id="editStudentClass" v-model="currentStudent.turma" required>
                <option value="anos_iniciais">Anos Iniciais</option>
                <option value="anos_finais">Anos Finais</option>
                <option value="eja">EJA</option>
              </select>
            </div>
            <div class="form-group">
              <label for="editStudentShift">Turno:</label>
              <select id="editStudentShift" v-model="currentStudent.turno" required>
                <option value="manha">Manhã</option>
                <option value="tarde">Tarde</option>
                <option value="integral">Integral</option>
              </select>
            </div>
            <div class="form-group">
              <label for="editStudentAge">Idade:</label>
              <input type="number" id="editStudentAge" v-model.number="currentStudent.idade" min="0" required>
            </div>
            <div class="form-group">
                <label for="editStudentSchoolUnit">Unidade Escolar:</label>
                <select id="editStudentSchoolUnit" v-model.number="currentStudent.school_unit_id">
                    <option value="">Nenhuma</option>
                    <option v-for="unit in schoolUnits" :key="unit.id" :value="unit.id">
                        {{ unit.name }}
                    </option>
                </select>
            </div>
            
            <h4>Atualizar Foto (Opcional):</h4>
            <div class="webcam-container" v-if="showWebcamForEdit">
              <video id="webcamFeedEdit" ref="webcamFeedEdit" autoplay playsinline></video>
              <canvas id="canvasPhotoEdit" ref="canvasPhotoEdit" style="display: none;"></canvas>
            </div>
            <button type="button" @click="toggleWebcamForEdit">
              {{ showWebcamForEdit ? 'Parar Webcam' : 'Abrir Webcam para Nova Foto' }}
            </button>
            <button type="button" @click="captureImageForEdit" :disabled="!streamEdit">Capturar Nova Foto</button>
            <div class="captured-image-preview" style="margin-top: 10px;">
                <h5 >Pré-visualização da Nova Imagem:</h5>
                <img v-if="capturedEditImageDataURL" :src="capturedEditImageDataURL" style="max-width: 200px; border: 1px solid #ccc;" v-show="capturedEditImageDataURL">
                <p v-else>Nenhuma nova imagem capturada.</p>
            </div>
  
            <div class="modal-actions">
              <button type="submit">Salvar Alterações</button>
              <button type="button" @click="closeEditModal">Cancelar</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, reactive, onMounted, onBeforeUnmount } from 'vue';
  import { fetchSchoolUnits, fetchStudentsBySchool, getStudentDetails, updateStudentInfo, updateStudentImage, deleteStudent } from '../api/backendApi';
  
  export default {
    name: 'StudentsView',
    setup() {
      const students = ref([]);
      const schoolUnits = ref([]);
      const selectedSchoolUnitId = ref('');
      const loadingStudents = ref(true);
  
      const showEditModal = ref(false);
      const currentStudent = reactive({}); // Para armazenar os dados do aluno em edição
      const showWebcamForEdit = ref(false);
      const webcamFeedEdit = ref(null);
      const canvasPhotoEdit = ref(null);
      const capturedEditImageDataURL = ref(null);
      let streamEdit = null; // Stream da webcam para edição
  
      // --- Funções de Carregamento ---
      const loadSchoolUnits = async () => {
        try {
          schoolUnits.value = await fetchSchoolUnits();
        } catch (error) {
          console.error('Erro ao carregar unidades escolares:', error);
          alert('Erro ao carregar unidades escolares. Verifique o console.');
        }
      };
  
      const loadStudents = async () => {
        loadingStudents.value = true;
        try {
          if (selectedSchoolUnitId.value) {
            students.value = await fetchStudentsBySchool(selectedSchoolUnitId.value);
          } else {
            // Se "Todas as Unidades" for selecionado, pode-se buscar todos os alunos ou limpar
            // No momento, seu backend não tem um endpoint para "todos os alunos".
            // Se precisar, adicione get_all_students() no backend e a rota correspondente.
            // Por enquanto, limpa a lista se "Todas" for selecionado e não há endpoint para isso.
            students.value = []; 
            alert('Selecione uma unidade escolar para listar os alunos.');
          }
        } catch (error) {
          console.error('Erro ao buscar alunos:', error);
          alert('Erro ao carregar alunos. Verifique o console.');
          students.value = [];
        } finally {
          loadingStudents.value = false;
        }
      };
  
      // --- Funções do Modal de Edição ---
      const openEditModal = async (studentToEdit) => {
        try {
          // Fetch para garantir que temos os dados mais recentes do aluno, incluindo image_path se necessário
          const studentDetails = await getStudentDetails(studentToEdit.matricula);
          if (studentDetails) {
              Object.assign(currentStudent, studentDetails);
              capturedEditImageDataURL.value = null; // Limpa pré-visualização de foto anterior
              showEditModal.value = true;
              showWebcamForEdit.value = false; // Garante que a webcam não abre automaticamente
              streamEdit = null; // Limpa stream anterior
          } else {
              alert('Não foi possível carregar os detalhes do aluno.');
          }
        } catch (error) {
            console.error('Erro ao abrir modal de edição:', error);
            alert('Erro ao carregar detalhes do aluno para edição.');
        }
      };
  
      const closeEditModal = () => {
        showEditModal.value = false;
        Object.keys(currentStudent).forEach(key => delete currentStudent[key]); // Limpa o objeto reativo
        stopWebcamEdit(); // Para a webcam se estiver ativa
        capturedEditImageDataURL.value = null; // Limpa a imagem capturada
      };
  
      const saveEditedStudent = async () => {
        try {
          // Salva as informações textuais do aluno
          const infoUpdated = await updateStudentInfo(currentStudent.matricula, {
            name: currentStudent.name,
            turma: currentStudent.turma,
            turno: currentStudent.turno,
            idade: currentStudent.idade,
            school_unit_id: currentStudent.school_unit_id,
          });
  
          // Salva a nova imagem se uma foi capturada
          let imageUpdated = true; // Assume true se não houver nova imagem para atualizar
          if (capturedEditImageDataURL.value) {
            imageUpdated = await updateStudentImage(currentStudent.matricula, capturedEditImageDataURL.value);
          }
  
          if (infoUpdated && imageUpdated) {
            alert('Aluno atualizado com sucesso!');
            closeEditModal();
            loadStudents(); // Recarrega a lista para mostrar as alterações
          } else {
            alert('Erro ao atualizar aluno. Verifique o console.');
          }
        } catch (error) {
          console.error('Erro ao salvar alterações do aluno:', error);
          alert('Erro ao salvar alterações do aluno: ' + error.message);
        }
      };
  
      const confirmDeleteStudent = async (studentToDelete) => {
        if (confirm(`Tem certeza que deseja excluir o aluno ${studentToDelete.name} (${studentToDelete.matricula})?`)) {
          try {
            await deleteStudent(studentToDelete.matricula);
            alert('Aluno excluído com sucesso!');
            loadStudents(); // Recarrega a lista
          } catch (error) {
            console.error('Erro ao excluir aluno:', error);
            alert('Erro ao excluir aluno: ' + error.message);
          }
        }
      };
  
      // --- Funções da Webcam para Edição ---
      const toggleWebcamForEdit = async () => {
        if (showWebcamForEdit.value) {
          stopWebcamEdit();
        } else {
          await startWebcamEdit();
        }
      };
  
      const startWebcamEdit = async () => {
        try {
          if (streamEdit) {
            streamEdit.getTracks().forEach(track => track.stop());
          }
          streamEdit = await navigator.mediaDevices.getUserMedia({ video: true });
          if (webcamFeedEdit.value) {
            webcamFeedEdit.value.srcObject = streamEdit;
            webcamFeedEdit.value.style.display = 'block';
            showWebcamForEdit.value = true;
            console.log("Webcam de edição iniciada.");
          }
        } catch (err) {
          console.error("Erro ao acessar a webcam de edição: ", err);
          alert("Não foi possível acessar a webcam para edição. Verifique as permissões.");
        }
      };
  
      const stopWebcamEdit = () => {
        if (streamEdit) {
          streamEdit.getTracks().forEach(track => track.stop());
          streamEdit = null;
          if (webcamFeedEdit.value) {
            webcamFeedEdit.value.srcObject = null;
          }
          showWebcamForEdit.value = false;
          console.log("Webcam de edição parada.");
        }
      };
  
      const captureImageForEdit = () => {
        if (!streamEdit) {
          alert("Webcam não está ativa para captura.");
          return;
        }
        const video = webcamFeedEdit.value;
        const canvas = canvasPhotoEdit.value;
  
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
  
        const context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
  
        capturedEditImageDataURL.value = canvas.toDataURL('image/png');
        console.log("Nova imagem capturada para edição!");
        // stopWebcamEdit(); // Opcional: parar a webcam após capturar
      };
  
      // --- Ciclo de Vida ---
      onMounted(() => {
        loadSchoolUnits();
        // Inicialmente não carrega alunos, espera seleção de unidade ou pode buscar todos se houver endpoint
      });
  
      onBeforeUnmount(() => {
        stopWebcamEdit(); // Garante que a webcam seja parada ao sair da página
      });
  
      return {
        students,
        schoolUnits,
        selectedSchoolUnitId,
        loadingStudents,
        loadStudents,
        
        showEditModal,
        currentStudent,
        openEditModal,
        closeEditModal,
        saveEditedStudent,
        confirmDeleteStudent,
  
        showWebcamForEdit,
        webcamFeedEdit,
        canvasPhotoEdit,
        capturedEditImageDataURL,
        toggleWebcamForEdit,
        captureImageForEdit,
      };
    }
  };
  </script>
  
  <style scoped>
  /* Estilos para students.html (adaptados do seu CSS existente) */
  .students-management {
    padding: 20px;
  }
  
  .section {
    margin-top: 30px;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background-color: #f9f9f9;
  }
  
  .filter-controls {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    align-items: center;
    margin-bottom: 20px;
  }
  
  .students-table {
    width: 100%;
    border-collapse: collapse;
  }
  
  .students-table th,
  .students-table td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
  }
  
  .students-table th {
    background-color: #f2f2f2;
    font-weight: bold;
  }
  
  .students-table button {
    padding: 5px 10px;
    margin-right: 5px;
    cursor: pointer;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
  }
  .students-table button:hover {
    background-color: #0056b3;
  }
  
  /* Modal Styles */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }
  
  .modal-content {
    background: white;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    width: 90%;
    max-width: 600px;
    max-height: 90vh; /* Limita a altura do modal */
    overflow-y: auto; /* Adiciona scroll se o conteúdo for maior */
  }
  
  .modal-content h3, .modal-content h4 {
    text-align: center;
    margin-bottom: 20px;
  }
  
  .modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 20px;
  }
  
  .modal-actions button {
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
  }
  
  .modal-actions button[type="submit"] {
    background-color: #28a745;
    color: white;
    border: none;
  }
  .modal-actions button[type="submit"]:hover {
    background-color: #218838;
  }
  
  .modal-actions button[type="button"] {
    background-color: #dc3545;
    color: white;
    border: none;
  }
  .modal-actions button[type="button"]:hover {
    background-color: #c82333;
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
  
  .form-group input[type="text"],
  .form-group input[type="number"],
  .form-group select {
      width: calc(100% - 22px);
      padding: 10px;
      border: 1px solid #ccc;
      border-radius: 4px;
      font-size: 16px;
  }
  
  .webcam-container {
      margin-top: 20px;
      display: flex;
      justify-content: center;
      align-items: center;
      background-color: #eee;
      border: 1px solid #ccc;
      border-radius: 5px;
      overflow: hidden;
      width: 100%;
      max-width: 400px; /* Adapte ao tamanho da sua webcam */
      margin-left: auto;
      margin-right: auto;
  }
  
  .webcam-container video {
      width: 100%;
      height: auto;
      display: block;
  }
  </style>