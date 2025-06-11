<template>
  <nav>
    <router-link to="/">Home</router-link> |
    <router-link to="/admin">Administrativo</router-link> |
    <router-link to="/recognition">Reconhecimento</router-link> |
    <router-link to="/logs">Logs</router-link> |
    <router-link to="/school-units">Unidades</router-link>
  </nav>
  <router-view /> </template>

<script>
// Você pode adicionar lógicas globais aqui, mas a maioria da lógica irá para os componentes de view.
export default {
  name: 'App',
};
</script>

<style>
/* Estilos globais para a aplicação Vue */
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

nav {
  padding: 30px;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
  text-decoration: none;
}

nav a.router-link-exact-active {
  color: #42b983;
}
</style>