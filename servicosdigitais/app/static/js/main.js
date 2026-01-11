// ======================================================
// CONTROLE DE VISUALIZAÇÃO DE SENHA
// Alterna entre mostrar e esconder a senha do campo
// ======================================================
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

    botao.classList.toggle('ativo');
}


// ======================================================
// FOCO AUTOMÁTICO NO PRIMEIRO ALERTA
// ======================================================
document.addEventListener('DOMContentLoaded', function () {

    const primeiroAlerta = document.querySelector('.alert');

    if (primeiroAlerta) {
        setTimeout(function () {
            primeiroAlerta.focus();
        }, 100);
    }

});


// ======================================================
// OCULTAR DADOS DO PERFIL (SEM RECARREGAR)
// ======================================================
document.addEventListener('DOMContentLoaded', function () {

    const botao = document.getElementById('botao-ocultar-dados');
    if (!botao) {
        return;
    }

    const aviso = document.getElementById('aviso-ocultacao');
    const csrfToken = document
        .querySelector('meta[name="csrf-token"]')
        ?.getAttribute('content');

    botao.addEventListener('click', function () {

        const userId = botao.dataset.userId;

        fetch(`/perfil/${userId}/toggle_ocultar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        })
            .then(resposta => resposta.json())
            .then(dados => {

                if (dados.ocultar_dados === true) {
                    botao.textContent = 'Mostrar Dados';
                    aviso.classList.remove('d-none');
                }

                if (dados.ocultar_dados === false) {
                    botao.textContent = 'Ocultar Dados';
                    aviso.classList.add('d-none');
                }

            })
            .catch(() => {
                console.error('Erro ao alternar ocultação de dados');
            });

    });

});


// ======================================================
// EDITAR PERFIL — SLIDE DOWN / SLIDE UP
// Mostra ou oculta o formulário de edição
// ======================================================
document.addEventListener("DOMContentLoaded", function () {

    const botaoEditar = document.getElementById("btn-editar-perfil");
    const formulario = document.getElementById("form-editar-perfil");

    if (!botaoEditar || !formulario) {
        return;
    }

    // garante estado inicial
    formulario.classList.add("d-none");
    formulario.setAttribute("aria-hidden", "true");
    botaoEditar.setAttribute("aria-expanded", "false");

    botaoEditar.addEventListener("click", function () {

        const estaOculto = formulario.classList.contains("d-none");

        formulario.classList.toggle("d-none");
        formulario.setAttribute("aria-hidden", String(!estaOculto));
        botaoEditar.setAttribute("aria-expanded", String(estaOculto));

        if (estaOculto) {
            setTimeout(function () {
                formulario.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

                const primeiroCampo = formulario.querySelector(
                    "input, textarea, select"
                );

                if (primeiroCampo) {
                    primeiroCampo.focus({ preventScroll: true });
                }
            }, 50);
        } else {
            botaoEditar.scrollIntoView({
                behavior: "smooth",
                block: "center"
            });
        }

    });

});
