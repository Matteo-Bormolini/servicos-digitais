// =========================================================
// CONTROLE DE VISUALIZAÇÃO DE SENHA
// =========================================================
// Alterna entre mostrar e esconder a senha do campo
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

    // Marca visualmente o botão como ativo
    botao.classList.toggle('ativo');
}


// =========================================================
// FOCO AUTOMÁTICO NO PRIMEIRO ALERTA
// =========================================================
// Leva o foco para a primeira mensagem de alerta da página
document.addEventListener('DOMContentLoaded', function () {

    const primeiroAlerta = document.querySelector('.alert');

    if (primeiroAlerta) {
        setTimeout(function () {
            primeiroAlerta.focus();
        }, 100);
    }

});



