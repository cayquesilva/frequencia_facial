<template>
    <div class="recognition">
      <h1>Sistema de Frequência Escolar - Reconhecimento Facial</h1>
      <div class="section">
        <h2>Tela de Reconhecimento</h2>
        <div class="webcam-container">
          <video id="recognitionWebcamFeed" ref="recognitionWebcamFeed" autoplay playsinline></video>
          <canvas id="recognitionCanvas" ref="recognitionCanvas" style="display: none;"></canvas>
        </div>
        <p id="processingIndicator" v-show="isProcessingRecognition">Processando...</p>
        <h3 id="recognitionStatus">{{ recognitionStatus }}</h3>
        <p id="recognizedStudentInfo" :style="{ color: recognizedStudentInfoColor }">{{ recognizedStudentInfo }}</p>
      </div>
    </div>
  </template>
  
  <script>
  import { onMounted, ref, onBeforeUnmount } from 'vue';
  
  // Funções utilitárias e de API (mantenha em um arquivo separado como src/api/backendApi.js)
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
  
  async function recognizeFaceApi(imageDataURL) {
      try {
          const response = await fetch('http://127.0.0.1:5000/api/recognize', {
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
  
  export default {
    name: 'RecognitionView',
    setup() {
        const recognitionWebcamFeed = ref(null);
        const recognitionCanvas = ref(null);
        const recognitionStatus = ref("Aguardando reconhecimento...");
        const recognizedStudentInfo = ref("");
        const recognizedStudentInfoColor = ref('#333');
        const isProcessingRecognition = ref(false);

        let streamReconhecimento = null; // Mantenha a referência ao stream da webcam
        let lastRecognitionTime = 0;
        const RECOGNITION_INTERVAL = 5000;
        const recognizedStudentsInSession = {};

        let animationFrameId = null; // Para controlar o loop requestAnimationFrame

        const startWebcamReconhecimento = async () => {
        try {
            if (streamReconhecimento) {
            // Parar qualquer stream existente antes de iniciar um novo
            streamReconhecimento.getTracks().forEach(track => track.stop());
            }
            streamReconhecimento = await navigator.mediaDevices.getUserMedia({ video: true });
            if (recognitionWebcamFeed.value) {
            recognitionWebcamFeed.value.srcObject = streamReconhecimento;
            recognitionWebcamFeed.value.style.display = 'block';
            // Iniciar o loop de envio de frames APENAS quando a webcam estiver pronta
            if (animationFrameId) { // Cancela qualquer loop anterior
                cancelAnimationFrame(animationFrameId);
            }
            animationFrameId = requestAnimationFrame(sendFrameForRecognition);
            }
            console.log("Webcam de reconhecimento iniciada com sucesso!");
        } catch (err) {
            console.error("Erro ao acessar a webcam de reconhecimento: ", err);
            alert("Não foi possível acessar a webcam de reconhecimento. Verifique as permissões do navegador e se outra aba/app está usando a câmera.");
        }
        };

        const sendFrameForRecognition = async (timestamp) => {
            // Verifique se o stream ainda está ativo antes de processar
            if (!streamReconhecimento || !streamReconhecimento.active) {
                console.warn("Stream de reconhecimento não ativo, parando o loop.");
                isProcessingRecognition.value = false;
                // Não chame requestAnimationFrame novamente se o stream não estiver ativo
                return;
            }

            if (timestamp - lastRecognitionTime < RECOGNITION_INTERVAL || isProcessingRecognition.value) {
                animationFrameId = requestAnimationFrame(sendFrameForRecognition); // Continua o loop
                return;
            }
            lastRecognitionTime = timestamp;
            isProcessingRecognition.value = true;

            recognitionStatus.value = "Processando...";
            recognizedStudentInfo.value = "";
            recognizedStudentInfoColor.value = '#333';

            const video = recognitionWebcamFeed.value;
            const canvas = recognitionCanvas.value;

            if (!video || !canvas || video.readyState !== 4) { // readyState === 4 means have enough data
                console.warn("Webcam não está pronta para capturar quadro.");
                isProcessingRecognition.value = false;
                animationFrameId = requestAnimationFrame(sendFrameForRecognition);
                return;
            }

            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const context = canvas.getContext('2d');
            context.drawImage(video, 0, 0, canvas.width, canvas.height);

            const imageDataURL = canvas.toDataURL('image/jpeg', 0.8);

            try {
                const data = await recognizeFaceApi(imageDataURL);

                if (data.recognized) {
                // A lógica de cooldown do frontend ainda é útil para evitar spam de requisições,
                // mas a mensagem final virá do backend.
                const currentTime = Date.now();
                const matricula = data.matricula;

                // A VERIFICAÇÃO DE COOLDOWN DO FRONTEND PODE CONTINUAR AQUI SE DESEJAR MINIMIZAR REQUISIÇÕES
                // OU PODE SER REMOVIDA SE O BACKEND FOR O ÚNICO RESPONSÁVEL.
                // Se você mantiver, certifique-se de que a mensagem no frontend seja clara.

                if (data.attendance_recorded) { // O backend confirmou que registrou
                    recognizedStudentsInSession[matricula] = currentTime; // Atualiza o cooldown local
                    recognitionStatus.value = `Presença Registrada!`;
                    recognizedStudentInfo.value = `Nome: ${data.name}, Matrícula: ${data.matricula}`;
                    recognizedStudentInfoColor.value = 'green';
                    speak(`Presença registrada para ${data.name}.`);
                    console.log('Reconhecido e Frequência Salva:', data);
                } else { // O backend indicou que não registrou (provavelmente por duplicidade)
                    recognitionStatus.value = `Atenção!`;
                    recognizedStudentInfo.value = `${data.name}: ${data.message || "Frequência não registrada."}`;
                    recognizedStudentInfoColor.value = 'orange'; // Cor laranja para indicar que não foi gravado
                    speak(`${data.name}, ${data.message || "frequência não registrada."}`);
                    console.log('Reconhecido, mas frequência não salva (backend):', data);
                    }
                } else {
                    recognitionStatus.value = "Nenhum rosto reconhecido.";
                    recognizedStudentInfo.value = data.message || "Tente se posicionar melhor.";
                    recognizedStudentInfoColor.value = '#333';
                    console.log('Não Reconhecido:', data.message);
                }
            } catch (error) {
                recognitionStatus.value = "Erro de conexão.";
                recognizedStudentInfo.value = "Verifique se o backend está rodando. Detalhes: " + error.message; // Mensagem mais específica
                recognizedStudentInfoColor.value = 'red'; // Usar a ref para mudar a cor
                console.error('Erro de rede ou ao enviar frame para reconhecimento:', error);
            } finally {
                isProcessingRecognition.value = false;
            }

            animationFrameId = requestAnimationFrame(sendFrameForRecognition); // Continua o loop
        };

        onMounted(() => {
        console.log('RecognitionView montado. Iniciando webcam...');
        startWebcamReconhecimento();
        });

        onBeforeUnmount(() => {
            // Parar o stream da webcam
            if (streamReconhecimento) {
                streamReconhecimento.getTracks().forEach(track => track.stop());
                console.log("Webcam de reconhecimento parada.");
                streamReconhecimento = null; // Limpa a referência
            }
            // Cancelar o loop de requestAnimationFrame
            if (animationFrameId) {
                cancelAnimationFrame(animationFrameId);
                console.log("Loop de reconhecimento cancelado.");
                animationFrameId = null; // Limpa a referência
            }
            // Resetar o estado do componente
            recognitionStatus.value = "Aguardando reconhecimento...";
            recognizedStudentInfo.value = "";
            recognizedStudentInfoColor.value = '#333';
            isProcessingRecognition.value = false;
            lastRecognitionTime = 0;
            // Limpar recognizedStudentsInSession se desejar (para que o cooldown resete ao sair da página)
            for (const key in recognizedStudentsInSession) {
                delete recognizedStudentsInSession[key];
            }
            console.log('RecognitionView desmontado. Recursos liberados.');
        });

        return {
        recognitionWebcamFeed,
        recognitionCanvas,
        recognitionStatus,
        recognizedStudentInfo,
        recognizedStudentInfoColor,
        isProcessingRecognition,
        };
    }
    };
    </script>
  
  <style scoped>
  /* Estilos para recognition.html */
  .section {
      margin-top: 30px;
      padding: 20px;
      border: 1px solid #ddd;
      border-radius: 8px;
      background-color: #f9f9f9;
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
      display: block;
  }
  
  #processingIndicator {
      font-style: italic;
      color: #555;
  }
  #recognitionStatus {
      font-size: 1.5em;
      margin-top: 15px;
      color: #007bff;
  }
  #recognizedStudentInfo {
      font-size: 1.2em;
      color: green;
  }
  </style>