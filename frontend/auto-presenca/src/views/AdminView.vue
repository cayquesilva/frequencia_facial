<template>
    <div class="admin">
      <h1>Sistema de Frequência Escolar - Painel Administrativo</h1>
  
      <div class="admin-actions">
          <router-link to="/logs" class="button logs">Ver Logs de Acesso</router-link>
          <router-link to="/school-units" class="button units">Gerenciar Unidades Escolares</router-link>
      </div>
  
      <div class="section">
          <h2>Cadastro de Aluno</h2>
          <form @submit.prevent="saveStudent" style="margin-top: 20px;">
              <div class="form-group">
                  <label for="studentName">Nome:</label>
                  <input type="text" id="studentName" v-model="student.name" required>
              </div>
              <div class="form-group">
                  <label for="studentMatricula">Matrícula:</label>
                  <input type="text" id="studentMatricula" v-model="student.matricula" required>
              </div>
              <div class="form-group">
                  <label for="studentClass">Turma:</label>
                  <select id="studentClass" v-model="student.turma" required>
                      <option value="">Selecione</option>
                      <option value="anos_iniciais">Anos Iniciais</option>
                      <option value="anos_finais">Anos Finais</option>
                      <option value="eja">EJA</option>
                  </select>
              </div>
              <div class="form-group">
                  <label for="studentShift">Turno:</label>
                  <select id="studentShift" v-model="student.turno" required>
                      <option value="">Selecione</option>
                      <option value="manha">Manhã</option>
                      <option value="tarde">Tarde</option>
                      <option value="integral">Integral</option>
                  </select>
              </div>
              <div class="form-group">
                  <label for="studentAge">Idade:</label>
                  <input type="number" id="studentAge" v-model.number="student.idade" min="0" required>
              </div>
              <div class="form-group">
                  <label for="studentSchoolUnit">Unidade Escolar:</label>
                  <select id="studentSchoolUnit" v-model.number="student.school_unit_id">
                      <option value="">Nenhuma</option>
                      <option v-for="unit in schoolUnits" :key="unit.id" :value="unit.id">
                          {{ unit.name }}
                      </option>
                  </select>
              </div>
              <div class="webcam-container">
                  <video id="webcamFeedCadastro" ref="webcamFeed" autoplay playsinline></video>
                  <canvas id="canvasPhoto" ref="canvasPhoto" style="display: none;"></canvas>
              </div>
              <button type="button" @click="captureImage">Capturar Imagem</button>
              <div class="captured-image-preview" style="margin-top: 20px;">
                  <h3>Pré-visualização da Imagem:</h3>
                  <img id="capturedImage" :src="capturedImageDataURL" style="max-width: 300px; border: 1px solid #ccc;" v-show="capturedImageDataURL">
              </div>
              <button type="submit" :disabled="!capturedImageDataURL">Salvar Cadastro</button>
          </form>
      </div>
    </div>
  </template>
  
  <script>
    import { onMounted, ref, reactive } from 'vue';
    // Importe as funções de API do seu módulo centralizado
    import { fetchSchoolUnits, registerStudent } from '../api/backendApi'; // <-- AQUI ESTÁ A MUDANÇA PRINCIPAL

    // Funções utilitárias (speak) podem permanecer aqui ou em um módulo separado
    function speak(text) {
        const synth = window.speechSynthesis;
        if (synth) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'pt-BR';
            utterance.rate = 1.1;
            synth.speak(utterance);
        } else {
            console.warn("API SpeechSynthesis não suportada neste navegador.");
        }
    }
  
    export default {
        name: 'AdminView',
        setup() {
            // Data properties
            const webcamFeed = ref(null);
            const canvasPhoto = ref(null);
            const capturedImageDataURL = ref(null);
            const schoolUnits = ref([]);
            const student = reactive({
                name: '',
                matricula: '',
                turma: '',
                turno: '',
                idade: null,
                school_unit_id: null,
            });
            let streamCadastro = null;
        
            // Methods
            const startWebcamCadastro = async () => {
                try {
                if (streamCadastro) {
                    streamCadastro.getTracks().forEach(track => track.stop());
                }
                streamCadastro = await navigator.mediaDevices.getUserMedia({ video: true });
                if (webcamFeed.value) {
                    webcamFeed.value.srcObject = streamCadastro;
                    webcamFeed.value.style.display = 'block';
                }
                console.log("Webcam de cadastro iniciada com sucesso!");
                } catch (err) {
                console.error("Erro ao acessar a webcam de cadastro: ", err);
                alert("Não foi possível acessar a webcam de cadastro. Verifique as permissões do navegador e se outra aba/app está usando a câmera.");
                }
            };
        
            const loadSchoolUnits = async () => {
                try {
                    schoolUnits.value = await fetchSchoolUnits(); // <-- CHAMA A FUNÇÃO IMPORTADA
                } catch (error) {
                    alert('Erro ao carregar unidades escolares. Verifique o console.'+error.message);
                }
            };
        
            const captureImage = () => {
                if (!streamCadastro) {
                    alert("A webcam de cadastro não está ativa. Por favor, inicie a webcam primeiro.");
                    return;
                }
        
                const video = webcamFeed.value;
                const canvas = canvasPhoto.value;
        
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
        
                const context = canvas.getContext('2d');
                context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
                capturedImageDataURL.value = canvas.toDataURL('image/png');
                console.log("Imagem capturada e exibida para cadastro!");
            };
        
            const saveStudent = async () => {
                if (!capturedImageDataURL.value) {
                    alert("Por favor, capture uma imagem antes de salvar o cadastro.");
                    return;
                }
        
                // O 'image' property is added here directly from capturedImageDataURL
                const studentDataToSend = { ...student, image: capturedImageDataURL.value };
        
                console.log("Tentando enviar dados do aluno para cadastro:", studentDataToSend);
        
                try {
                    const response = await registerStudent(studentDataToSend); // <-- CHAMA A FUNÇÃO IMPORTADA
                    console.log('Sucesso no cadastro:', response);
                    alert('Aluno cadastrado com sucesso!');
                    // Reset form and image preview
                    Object.assign(student, { name: '', matricula: '', turma: '', turno: '', idade: null, school_unit_id: null });
                    capturedImageDataURL.value = null;
                // Optionally restart webcam or just keep it running
                } catch (error) {
                    alert('Erro ao cadastrar aluno: ' + error.message);
                }
            };
        
            // Lifecycle Hook
            onMounted(() => {
                startWebcamCadastro();
                loadSchoolUnits();
            });
        
            // Return reactive properties and methods
            return {
                webcamFeed,
                canvasPhoto,
                capturedImageDataURL,
                schoolUnits,
                student,
                captureImage,
                saveStudent,
            };
        }
    };
  </script>
  
  <style scoped>
  /* Estilos para admin.html (mantidos aqui, mas podem ser globais ou em outros arquivos .css) */
  .admin-actions {
      margin-top: 20px;
      text-align: center;
  }
  .admin-actions a.button {
      display: inline-block;
      background-color: #007bff; /* Cor azul padrão */
      color: white;
      padding: 10px 20px;
      border: none;
      border-radius: 5px;
      cursor: pointer;
      font-size: 16px;
      text-decoration: none;
      margin: 5px;
      transition: background-color 0.3s ease;
  }
  .admin-actions a.button.logs {
      background-color: #28a745;
  }
  .admin-actions a.button.logs:hover {
      background-color: #218838;
  }
  .admin-actions a.button.units {
      background-color: #ffc107;
      color: #333;
  }
  .admin-actions a.button.units:hover {
      background-color: #e0a800;
  }
  
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
  
  .form-group input[type="text"],
  .form-group input[type="number"],
  .form-group select {
      width: calc(100% - 22px); /* Ajuste para padding e border */
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
      max-width: 640px; /* Adapte ao tamanho da sua webcam */
      margin-left: auto;
      margin-right: auto;
  }
  
  .webcam-container video {
      width: 100%;
      height: auto;
      display: block; /* Garante que o video não tenha espaço extra abaixo */
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
  
  .captured-image-preview img {
      margin-top: 10px;
  }
  </style>