<template>
  <div class="home">
    <h1>Bem-vindo ao Sistema de Frequência Escolar</h1>
    <p>Por favor, selecione sua função:</p>

    <div class="homepage-links">
        <router-link to="/admin" class="button">Painel Administrativo (Cadastro)</router-link>
        <router-link to="/recognition" class="button">Tela de Reconhecimento (Alunos)</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomeView',
};
</script>

<style scoped>
/* Estilos específicos para a HomeView */
.homepage-links {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 50px;
}
.homepage-links a {
    background-color: #007bff;
    color: white;
    padding: 15px 30px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 20px;
    text-decoration: none;
    margin-bottom: 20px;
    transition: background-color 0.3s ease;
    width: 300px;
    text-align: center;
}
.homepage-links a:hover {
    background-color: #0056b3;
}
</style>