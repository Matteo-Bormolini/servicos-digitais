/* =====================================================================
   S.D — BASE DOS PERFIS (componentes/perfil-base/perfil-base.js)
   Tudo o que é IGUAL nos 4 perfis (Administrador, Cliente CPF,
   Cliente CNPJ e Prestador) fica aqui, em um lugar só:
     1. Preencher dados na tela        5. Formulário "Editar perfil"
     2. Abas com rolagem lateral       6. Foto de perfil opcional
     3. Telefones (principal + extras) 7. Pop-up "Excluir perfil"
     4. Sanfona + olho da senha
   Cada perfil (pasta perfil-<tipo>, arquivo perfil-<tipo>.js) só guarda o que é exclusivo dele.
   Depende de: componentes/utilidades/utilidades.js.
   IMPORTANTE: tudo roda só no navegador (demonstração). Salvar, excluir
   e enviar fotos de verdade dependem do servidor (etapa futura).
   ===================================================================== */
(function () {
  "use strict";
  const U = window.SDUtil;
  if (!U) { console.error("[S.D] perfil-base.js: carregue componentes/utilidades/utilidades.js antes."); return; }

  /* ---------- 0. PADRÕES (cada perfil pode trocar no seu CONFIG) ---------- */
  const PADRAO = {
    maxTelefonesSecundarios: 4,
    tamanhoMaxFotoMB: 5,
    tiposFoto: ["image/jpeg", "image/png", "image/webp"]
  };

  const $ = (sel) => document.querySelector(sel);
  const ICONES = {
    x: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg>',
    olho: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/></svg>',
    olhoRiscado: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M3 3l18 18"/><path d="M10.6 5.1A10 10 0 0 1 12 5c6.5 0 10 7 10 7a17 17 0 0 1-3.2 4.1M6.6 6.6A17 17 0 0 0 2 12s3.5 7 10 7a9.7 9.7 0 0 0 5.4-1.6"/><path d="M9.9 9.9a3 3 0 0 0 4.2 4.2"/></svg>'
  };

  // Altura do painel: as funções abaixo chamam atualizarAltura() sempre que o
  // conteúdo muda. Antes das abas existirem, não faz nada.
  let controleAbas = null;
  const atualizarAltura = () => { if (controleAbas) controleAbas.atualizarAltura(); };

  /* ---------- 1. PREENCHER DADOS NA TELA ---------- */
  // <td data-campo="email"> recebe valores.email (sempre como texto, nunca HTML)
  function preencherCampos(valores) {
    document.querySelectorAll("[data-campo]").forEach((el) => {
      el.textContent = valores[el.dataset.campo] ?? "";
    });
  }
  // Placeholders do formulário = valores atuais (mostra o que será mantido)
  function preencherPlaceholders(mapa) {
    Object.entries(mapa).forEach(([id, val]) => { const el = document.getElementById(id); if (el) el.placeholder = val || ""; });
  }
  // Lista de seleção: a 1ª opção ("Manter atual") mantém o valor que já existe
  function preencherSelect(select, textoAtual, opcoes) {
    select.innerHTML = "";
    select.append(new Option(`Manter atual (${textoAtual})`, ""));
    opcoes.forEach((o) => (typeof o === "string" ? select.append(new Option(o, o)) : select.append(new Option(o.texto, o.valor))));
  }
  // Valores padrão quando o campo está vazio
  const ouTraco = (v) => (v ? v : "—");

  /* ---------- 2. ABAS COM ROLAGEM LATERAL ----------
     opcoes.abas: seletores das abas (ex.: ["#aba-perfil", "#aba-servicos"])
     opcoes.navegaveis(): abas que podem ser escolhidas agora (padrão: todas)
     opcoes.semArrasto(): true = não troca de aba arrastando (ex.: visão do cliente) */
  function iniciarAbas(opcoes) {
    const trilho = $("#perfil-trilho");
    const todas = opcoes.abas.map((s) => $(s));
    const navegaveis = opcoes.navegaveis || (() => todas);
    const semArrasto = opcoes.semArrasto || (() => false);
    let ativo = 0;

    // A altura do trilho acompanha o painel visível (evita espaço vazio)
    function ajustarAltura() {
      const painel = trilho.children[ativo];
      if (painel) trilho.style.height = painel.scrollHeight + "px";
    }

    function ativar(indice, rolar) {
      ativo = indice;
      todas.forEach((aba, i) => {
        const sim = i === indice;
        aba.setAttribute("aria-selected", String(sim));
        aba.tabIndex = sim ? 0 : -1;
        // Painel fora da tela não recebe foco por Tab
        document.getElementById(aba.getAttribute("aria-controls")).inert = !sim;
      });
      if (rolar) trilho.scrollTo({ left: indice * trilho.clientWidth });
      ajustarAltura();
    }

    // Clique e teclado (← → Home End) nas abas
    todas.forEach((aba, i) => {
      aba.addEventListener("click", () => ativar(i, true));
      aba.addEventListener("keydown", (e) => {
        const total = navegaveis().length;
        let novo = null;
        if (e.key === "ArrowRight") novo = (i + 1) % total;
        if (e.key === "ArrowLeft") novo = (i - 1 + total) % total;
        if (e.key === "Home") novo = 0;
        if (e.key === "End") novo = total - 1;
        if (novo !== null) { e.preventDefault(); ativar(novo, true); todas[novo].focus(); }
      });
    });

    // Mouse: arrastar o conteúdo para os lados (no celular o deslize já é nativo).
    // Dentro do carrossel o arrasto troca a FOTO; no quadro de serviços move o CARTÃO.
    let arrasto = null;
    trilho.addEventListener("pointerdown", (e) => {
      if (semArrasto() || e.pointerType !== "mouse" || e.button !== 0 ||
          e.target.closest("input, button, a, label, textarea, select, summary, .carrossel, .kanban")) return;
      arrasto = { x: e.clientX, inicio: trilho.scrollLeft, moveu: false };
    });
    window.addEventListener("pointermove", (e) => {
      if (!arrasto) return;
      const dx = e.clientX - arrasto.x;
      if (Math.abs(dx) > 8) {
        arrasto.moveu = true;
        trilho.style.scrollSnapType = "none"; trilho.style.scrollBehavior = "auto";
        trilho.scrollLeft = arrasto.inicio - dx;
      }
    });
    window.addEventListener("pointerup", (e) => {
      if (!arrasto) return;
      const dx = e.clientX - arrasto.x, moveu = arrasto.moveu;
      arrasto = null;
      trilho.style.scrollSnapType = ""; trilho.style.scrollBehavior = "";
      if (moveu) {
        const limite = trilho.clientWidth * 0.15;   // arrastar 15% troca de seção
        let novo = ativo;
        if (dx < -limite) novo = Math.min(navegaveis().length - 1, ativo + 1);
        if (dx > limite) novo = Math.max(0, ativo - 1);
        ativar(novo, true);
      }
    });

    // Deslizar com o dedo/trackpad também troca a aba
    let espera;
    trilho.addEventListener("scroll", () => {
      // O trilho só rola para os lados. Durante a animação de altura o navegador pode
      // rolá-lo para baixo ao focar um campo — isso esconderia o topo do painel.
      if (trilho.scrollTop) trilho.scrollTop = 0;
      clearTimeout(espera);
      espera = setTimeout(() => {
        const i = Math.min(navegaveis().length - 1, Math.round(trilho.scrollLeft / trilho.clientWidth));
        if (i !== ativo) ativar(i, false);
      }, 80);
    }, { passive: true });

    // Recalcula ao redimensionar a janela ou quando o conteúdo muda
    window.addEventListener("resize", () => { trilho.scrollLeft = ativo * trilho.clientWidth; ajustarAltura(); });
    if ("ResizeObserver" in window) {
      const ro = new ResizeObserver(ajustarAltura);
      [...trilho.children].forEach((p) => ro.observe(p));
    }

    controleAbas = { ativar, atualizarAltura: ajustarAltura, get ativo() { return ativo; } };
    ativar(0, false);
    return controleAbas;
  }

  /* ---------- 3. TELEFONES (principal + secundários) ----------
     perfil.telefones = [{ numero: "11900000000", principal: true }, ...] */
  function iniciarTelefones(perfil, opcoes = {}) {
    const max = opcoes.max ?? PADRAO.maxTelefonesSecundarios;
    const classeRemover = "btn-remover" + (opcoes.classeRemover ? " " + opcoes.classeRemover : "");
    const lista = $("#lista-telefones");
    const btn = $("#btn-add-telefone"), caixa = $("#add-telefone"), input = $("#novo-telefone"), erro = $("#erro-novo-telefone");

    function renderizar() {
      lista.innerHTML = "";
      perfil.telefones.forEach((t, i) => {
        const li = document.createElement("li");
        const num = document.createElement("span");
        num.textContent = U.formatarTelefone(t.numero);
        const tipo = document.createElement("span");
        tipo.className = "tipo-tel";
        tipo.textContent = t.principal ? "(principal)" : "(secundário)";
        li.append(num, tipo);
        if (!t.principal) {
          const rem = document.createElement("button");
          rem.type = "button";
          rem.className = classeRemover;
          rem.innerHTML = ICONES.x;
          rem.setAttribute("aria-label", "Remover telefone " + U.formatarTelefone(t.numero));
          rem.addEventListener("click", () => { perfil.telefones.splice(i, 1); renderizar(); btn.focus(); });
          li.append(rem);
        }
        lista.append(li);
      });
      const cheio = perfil.telefones.filter((t) => !t.principal).length >= max;
      btn.disabled = cheio;
      btn.title = cheio ? `Limite de ${max} telefones secundários` : "Adicionar telefone secundário";
      atualizarAltura();
    }

    const abrir = (sim) => {
      caixa.hidden = !sim;
      btn.setAttribute("aria-expanded", String(sim));
      if (sim) input.focus(); else { input.value = ""; erro.textContent = ""; input.removeAttribute("aria-invalid"); btn.focus(); }
      atualizarAltura();
    };
    const salvar = () => {
      const d = U.soDigitos(input.value);
      let msg = "";
      if (!U.telefoneValido(d)) msg = "Informe DDD + número (10 ou 11 dígitos).";
      else if (perfil.telefones.some((t) => t.numero === d)) msg = "Este telefone já está cadastrado.";
      if (msg) { erro.textContent = msg; input.setAttribute("aria-invalid", "true"); input.focus(); return; }
      perfil.telefones.push({ numero: d, principal: false });
      renderizar();
      abrir(false);
    };
    btn.addEventListener("click", () => abrir(caixa.hidden));
    $("#btn-cancelar-telefone").addEventListener("click", () => abrir(false));
    $("#btn-salvar-telefone").addEventListener("click", salvar);
    input.addEventListener("input", () => { input.value = U.formatarTelefone(input.value); });
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") { e.preventDefault(); salvar(); }
      if (e.key === "Escape") abrir(false);
    });

    renderizar();
    return { renderizar };
  }

  /* ---------- 4. SANFONA "EDITAR PERFIL" + OLHO DA LINHA "SENHA" ----------
     A sanfona só esconde/mostra: o que foi digitado permanece até confirmar. */
  function abrirSanfona(abrir) {
    $("#sanfona-editar").hidden = !abrir;
    $("#btn-editar").setAttribute("aria-expanded", String(abrir));
    atualizarAltura();
  }
  function iniciarSanfona() {
    $("#btn-editar").addEventListener("click", () => abrirSanfona($("#sanfona-editar").hidden));
    // A senha real nunca pode ser exibida (fica criptografada no servidor);
    // o olho mostra/esconde o aviso que explica isso.
    const olho = $("#btn-ver-senha"), aviso = $("#aviso-senha");
    if (!olho || !aviso) return;
    olho.innerHTML = ICONES.olho;
    olho.addEventListener("click", () => {
      const abrir = aviso.hidden;
      aviso.hidden = !abrir;
      olho.innerHTML = abrir ? ICONES.olhoRiscado : ICONES.olho;
      olho.setAttribute("aria-pressed", String(abrir));
      olho.setAttribute("aria-label", abrir ? "Ocultar aviso da senha" : "Visualizar senha");
      atualizarAltura();
    });
  }

  /* ---------- 5. FORMULÁRIO "EDITAR PERFIL" ----------
     Regras: só valida e aplica o que foi PREENCHIDO; vazio mantém o valor atual.
     Máscaras automáticas pelo atributo data-mascara no <input>:
       telefone · cep · login (minúsculas, sem espaço) · ano (4 dígitos)
     opcoes:
       perfil       → objeto com os dados atuais
       coletar()    → { campo: valor } lido do formulário
       camposTexto  → campos simples copiados para o perfil se preenchidos
       validar(dados, marcar) → regras exclusivas da página (opcional)
       aplicarExtra(dados, alterados) → campos especiais (listas, números…) (opcional)
       aoConcluir() → redesenha a tela depois de aplicar */
  const MASCARAS = {
    telefone: (v) => U.formatarTelefone(v),
    cep: (v) => U.formatarCep(v),
    login: (v) => v.toLowerCase().replace(/\s/g, ""),
    ano: (v) => U.soDigitos(v).slice(0, 4)
  };

  function erroCampo(id, msg) {
    const input = document.getElementById(id);
    const span = document.getElementById("e-" + id.replace("f-", ""));
    if (span) span.textContent = msg || "";
    if (msg) input.setAttribute("aria-invalid", "true"); else input.removeAttribute("aria-invalid");
  }

  // Validações que valem para TODOS os perfis
  function validarComuns(d, marcar) {
    if (d.login && !/^[a-z0-9._]{3,30}$/.test(d.login)) marcar("f-login", "Use 3 a 30 caracteres: letras minúsculas, números, ponto ou _.");
    if (d.email && !U.emailValido(d.email)) marcar("f-email", "E-mail inválido.");
    if (d.telefone && !U.telefoneValido(d.telefone)) marcar("f-telefone", "Informe DDD + número (10 ou 11 dígitos).");
    if (d.numero && !/^[0-9A-Za-z\s/-]{1,10}$/.test(d.numero)) marcar("f-numero", "Número inválido.");
    if (d.cep && d.cep.length !== 8) marcar("f-cep", "O CEP deve ter 8 dígitos.");
    if (d.senha || d.senha2) {
      if (d.senha.length < 8 || !/[A-Za-z]/.test(d.senha) || !/\d/.test(d.senha)) marcar("f-senha", "A senha precisa de 8+ caracteres, com letras e números.");
      else if (d.senha !== d.senha2) marcar("f-senha2", "As senhas não coincidem.");
    }
  }

  // Botões de mostrar/ocultar a senha digitada (campos "Nova senha")
  function ligarOlhosDeSenha(raiz) {
    raiz.querySelectorAll(".btn-olho[data-alvo]").forEach((b) => {
      b.innerHTML = ICONES.olho;
      b.addEventListener("click", () => {
        const input = document.getElementById(b.dataset.alvo);
        const mostrar = input.type === "password";
        input.type = mostrar ? "text" : "password";
        b.innerHTML = mostrar ? ICONES.olhoRiscado : ICONES.olho;
        b.setAttribute("aria-label", mostrar ? "Ocultar senha" : "Mostrar senha");
        b.setAttribute("aria-pressed", String(mostrar));
      });
    });
  }

  function iniciarFormulario(opcoes) {
    const { perfil, coletar, camposTexto = [], validar, aplicarExtra, aoConcluir } = opcoes;
    const form = $("#form-editar"), msg = $("#msg-form");

    form.querySelectorAll("[data-mascara]").forEach((input) => {
      const mascara = MASCARAS[input.dataset.mascara];
      if (mascara) input.addEventListener("input", () => { input.value = mascara(input.value); });
    });
    ligarOlhosDeSenha(form);

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      U.limparMensagem(msg);
      form.querySelectorAll(".campo-erro").forEach((el) => (el.textContent = ""));
      form.querySelectorAll("[aria-invalid]").forEach((el) => el.removeAttribute("aria-invalid"));

      // Campos comuns + os da página
      const valor = (id) => { const el = document.getElementById(id); return el ? el.value.trim() : ""; };
      const dados = Object.assign({
        login: valor("f-login"), email: valor("f-email"), telefone: U.soDigitos(valor("f-telefone")),
        endereco: valor("f-endereco"), numero: valor("f-numero"), complemento: valor("f-complemento"),
        bairro: valor("f-bairro"), cep: U.soDigitos(valor("f-cep")),
        senha: $("#f-senha").value, senha2: $("#f-senha2").value
      }, coletar ? coletar(valor) : {});

      // Validação
      const erros = [];
      const marcar = (id, m) => { if (!erros.includes(id)) { erroCampo(id, m); erros.push(id); } };
      validarComuns(dados, marcar);
      if (validar) validar(dados, marcar);
      if (erros.length) {
        U.mostrarMensagem(msg, "erro", "Corrija os campos destacados. Nada foi alterado.");
        document.getElementById(erros[0]).focus();
        return;
      }

      // Aplica somente os campos preenchidos; vazios mantêm o anterior
      const alterados = [];
      ["login", "email", "endereco", "numero", "complemento", "bairro", "cep", ...camposTexto].forEach((c) => {
        if (dados[c] && dados[c] !== perfil[c]) { perfil[c] = dados[c]; alterados.push(c); }
      });
      if (dados.telefone) {
        const p = perfil.telefones.find((t) => t.principal);
        if (p && p.numero !== dados.telefone) { p.numero = dados.telefone; alterados.push("telefone"); }
      }
      if (aplicarExtra) aplicarExtra(dados, alterados);
      if (dados.senha) alterados.push("senha");  // a senha real é enviada só ao servidor (nunca exibida)

      if (!alterados.length) {
        U.mostrarMensagem(msg, "info", "Nenhuma alteração informada. Os dados atuais foram mantidos.");
        return;
      }

      form.reset();
      if (aoConcluir) aoConcluir();
      form.querySelectorAll(".btn-olho[data-alvo]").forEach((b) => { if (b.getAttribute("aria-pressed") === "true") b.click(); });
      U.mostrarMensagem(msg, "atencao",
        `Alteração aplicada nesta tela (${alterados.length} ${alterados.length === 1 ? "campo" : "campos"}). ` +
        "Demonstração: ainda não foi salva no servidor.");
      atualizarAltura();
    });
  }

  /* ---------- 6. FOTOS ---------- */
  // Confere tipo e tamanho do arquivo escolhido
  function validarArquivo(arq, config = PADRAO) {
    const tipos = config.tiposFoto || PADRAO.tiposFoto, maxMB = config.tamanhoMaxFotoMB || PADRAO.tamanhoMaxFotoMB;
    if (!tipos.includes(arq.type)) return `"${arq.name}": use JPG, PNG ou WEBP.`;
    if (arq.size > maxMB * 1024 * 1024) return `"${arq.name}": máximo de ${maxMB} MB.`;
    return "";
  }

  // Foto de perfil OPCIONAL (Cliente CPF e CNPJ): sem foto → foto padrão do sistema.
  // "Remover foto" só aparece quando existe foto própria.
  function iniciarFotoOpcional({ perfil, padrao, tipoIcone, textoAlt, config = PADRAO }) {
    const img = $("#foto-perfil"), msg = $("#msg-foto"), remover = $("#btn-remover-foto");
    function renderizar() {
      U.aplicarFoto(img, perfil.foto, padrao, tipoIcone);
      img.alt = textoAlt(!!perfil.foto);
      remover.hidden = !perfil.foto;
      atualizarAltura();
    }
    $("#btn-foto").addEventListener("click", () => $("#input-foto").click());
    $("#input-foto").addEventListener("change", (e) => {
      const arq = e.target.files[0];
      e.target.value = "";
      if (!arq) return;
      const erro = validarArquivo(arq, config);
      if (erro) { U.mostrarMensagem(msg, "erro", erro); return; }
      if (perfil.foto) URL.revokeObjectURL(perfil.foto);
      perfil.foto = URL.createObjectURL(arq);
      renderizar();
      U.mostrarMensagem(msg, "atencao", "Pré-visualização atualizada (ainda não enviada ao servidor).");
    });
    remover.addEventListener("click", () => {
      if (perfil.foto) URL.revokeObjectURL(perfil.foto);
      perfil.foto = null;
      renderizar();
      $("#btn-foto").focus();
      U.mostrarMensagem(msg, "atencao", "Foto removida nesta tela; será usada a foto padrão (ainda não salvo no servidor).");
    });
    renderizar();
    return { renderizar };
  }

  /* ---------- 7. POP-UP DE EXCLUSÃO ---------- */
  function iniciarExclusao() {
    const modal = $("#modal-excluir");
    $("#btn-excluir").addEventListener("click", () => modal.showModal());
    $("#modal-cancelar").addEventListener("click", () => modal.close());
    modal.addEventListener("click", (e) => { if (e.target === modal) modal.close(); });   // clique fora fecha
    modal.addEventListener("close", () => $("#btn-excluir").focus());
    $("#modal-confirmar").addEventListener("click", () => {
      modal.close();
      // A exclusão real será feita pelo servidor; aqui não apagamos nada
      U.mostrarMensagem($("#msg-geral"), "atencao", "Exclusão não executada: esta é uma demonstração sem servidor. Na versão final, o perfil será apagado e você sairá da conta.");
      atualizarAltura();
    });
  }

  /* ---------- 8. LINK DE AVALIAÇÕES (estrelas + média) ---------- */
  function preencherLinkAvaliacoes(link, avaliacao, href) {
    const media = U.decimal(avaliacao.media);
    link.href = href;
    link.innerHTML = U.estrelasSVG(avaliacao.media) +
      `<span>${media} (${avaliacao.total} ${avaliacao.total === 1 ? "avaliação" : "avaliações"})</span>`;
    link.setAttribute("aria-label", `Avaliação ${media} de 5, ${avaliacao.total} avaliações. Ver avaliações`);
  }

  window.SDPerfil = Object.freeze({
    PADRAO, ICONES, $, ouTraco, atualizarAltura,
    preencherCampos, preencherPlaceholders, preencherSelect, preencherLinkAvaliacoes,
    iniciarAbas, iniciarTelefones, iniciarSanfona, abrirSanfona,
    iniciarFormulario, ligarOlhosDeSenha, validarArquivo, iniciarFotoOpcional, iniciarExclusao
  });
})();
