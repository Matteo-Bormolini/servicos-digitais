// Este arquivo contém o JavaScript personalizado para o site, que pode ser utilizado para adicionar interatividade aos componentes.

// Controla a visualização da senha
function alternarSenha(idCampo, botao) {

    const campo = document.getElementById(idCampo);
    const icone = botao.querySelector('i');

    if (!campo || !icone) {
        return;
    }

    if (campo.type === 'password') {
        campo.type = 'text';
        icone.classList.remove('bi-eye');
        icone.classList.add('bi-eye-slash');
    } else {
        campo.type = 'password';
        icone.classList.remove('bi-eye-slash');
        icone.classList.add('bi-eye');
    }

    // Aplica estilo ativo (vermelho vinho)
    botao.classList.toggle('ativo');
}


