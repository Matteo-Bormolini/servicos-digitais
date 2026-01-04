// ===CONTROLE DE VISUALIZAÇÃO DE SENHA===
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


// ===FOCO AUTOMÁTICO NO PRIMEIRO ALERTA===
// Leva o foco para a primeira mensagem de alerta da página
document.addEventListener('DOMContentLoaded', function () {

    const primeiroAlerta = document.querySelector('.alert');

    if (primeiroAlerta) {
        setTimeout(function () {
            primeiroAlerta.focus();
        }, 100);
    }

});

// ===OCULTAR DADOS DO PERFIL===
// Alterna a visibilidade de dados sensíveis sem recarregar a página
document.addEventListener('DOMContentLoaded', function () {

    const botao = document.getElementById('botao-ocultar-dados');
    if (!botao) {
        return;
    }

    const aviso = document.getElementById('aviso-ocultacao');
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

    botao.addEventListener('click', function () {

        const userId = botao.dataset.userId;

        fetch(`/perfil/${userId}/toggle_ocultar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        })
            .then(response => response.json())
            .then(data => {

                if (data.ocultar_dados === true) {
                    botao.textContent = 'Mostrar Dados';
                    aviso.classList.remove('d-none');
                }

                if (data.ocultar_dados === false) {
                    botao.textContent = 'Ocultar Dados';
                    aviso.classList.add('d-none');
                }

            })
            .catch(() => {
                console.error('Erro ao alternar ocultação de dados');
            });

    });

});

// ===JS PARA MOSTRAR FORMULÁRIO EDITAR PERFIL===
// Exibe o formulário e oculta o botão de editar
function mostrarFormularioPerfil() {
    const container = document.getElementById('container-editar-perfil');
    const botao = document.getElementById('botao-editar');
    if (container && botao) {
        container.style.display = 'block';
        botao.style.display = 'none';
        container.scrollIntoView({ behavior: 'smooth' });
    }
}

// === DOWN SLIDE EDITAR PERFIL ===
// Mostra/oculta o formulário de edição e rola suavemente até ele
document.addEventListener("DOMContentLoaded", () => {
    // tenta localizar pelos ids esperados
    let btn = document.getElementById("btn-editar-perfil");
    let container = document.getElementById("form-editar-perfil");

    // fallback: procura por alternativas (caso ids tenham sido trocados)
    if (!btn) btn = document.querySelector("[data-toggle='editar-perfil']") || document.querySelector(".btn-editar-perfil");
    if (!container) container = document.querySelector("#container-editar") || document.querySelector(".form-editar-perfil");

    // se não encontrou, registra para debug e aborta (evita erros JS)
    if (!btn) {
        console.warn("JS editar-perfil: botão não encontrado (id='#btn-editar-perfil').");
        return;
    }
    if (!container) {
        console.warn("JS editar-perfil: container do formulário não encontrado (id='#form-editar-perfil').");
        return;
    }

    // garante estado inicial consistente
    container.classList.add("d-none");
    container.setAttribute("aria-hidden", "true");
    btn.setAttribute("aria-expanded", "false");

    // handler do clique
    btn.addEventListener("click", (e) => {
        e.preventDefault();

        const aberto = !container.classList.contains("d-none");

        if (!aberto) {
            // abrir: remove d-none, atualiza aria, rola suavemente
            container.classList.remove("d-none");
            container.setAttribute("aria-hidden", "false");
            btn.setAttribute("aria-expanded", "true");

            // pequeno delay para garantir layout antes do scroll
            setTimeout(() => {
                container.scrollIntoView({ behavior: "smooth", block: "start" });
                // se houver foco em primeiro input, colocar foco
                const primeiroInput = container.querySelector("input, textarea, select");
                if (primeiroInput) primeiroInput.focus({ preventScroll: true });
            }, 50);
        } else {
            // fechar: adiciona d-none e atualiza aria
            container.classList.add("d-none");
            container.setAttribute("aria-hidden", "true");
            btn.setAttribute("aria-expanded", "false");

            // opcional: rolar para o botão
            btn.scrollIntoView({ behavior: "smooth", block: "center" });
        }
    });
});



