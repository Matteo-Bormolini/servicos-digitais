/* =====================================================================
   S.D — LOGIN E CADASTRO (login-cadastro/login-cadastro.js)
   "Fazer login" e "Criar login" (Cliente CPF, Cliente CNPJ, Prestador).
   NavBar, Rodapé, cores e campos seguem o padrão do site.

   DEMONSTRAÇÃO (sem servidor): nenhuma senha é guardada ou enviada.
   Ao entrar/criar conta, guarda só { tipo, nome } nesta aba do navegador
   (configuracoes/config.js → SD.sessaoDemo) e leva para a página certa,
   para dar para testar a navegação logado entre as páginas.
   Na versão final: o SERVIDOR confere login e senha, cria a sessão segura
   (cookie HttpOnly) e devolve o tipo de usuário.
   ===================================================================== */
(function () {
  "use strict";
  const SD = window.SD, U = window.SDUtil;
  if (!SD || !U) { console.error("[S.D] login-cadastro.js: carregue config.js e utilidades.js antes."); return; }
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => document.querySelectorAll(s);
  const parametros = new URLSearchParams(location.search);

  /* ---------- 1. CONFIGURAÇÃO DOS 3 CADASTROS (edite rótulos e campos aqui) ---------- */
  const CAMPOS_SENHA = [
    { chave: "senha", rotulo: "Senha", obrigatorio: true, senha: true, dica: "Mínimo de 8 caracteres, com letras e números", auto: "new-password" },
    { chave: "senha2", rotulo: "Confirmação de senha", obrigatorio: true, senha: true, auto: "new-password" }
  ];
  const DICA_ENDERECO = "Rua, número, complemento, bairro, cidade – UF, CEP";

  // perfil = tipo de usuário usado em todo o site (seguranca/acesso.js)
  const TIPOS = {
    cpf: {
      perfil: "cliente-cpf",
      titulo: "Cadastro – Cliente CPF",
      sub: "Pessoa física (casas e apartamentos)",
      botao: "Criar login de Cliente CPF",
      campos: [
        { chave: "nome", rotulo: "Nome completo", obrigatorio: true, largo: true, auto: "name" },
        { chave: "login", rotulo: "Nome de login", obrigatorio: true, auto: "username" },
        { chave: "cpf", rotulo: "CPF", obrigatorio: true, mascara: "cpf", ph: "000.000.000-00" },
        { chave: "tel", rotulo: "Telefone", obrigatorio: true, mascara: "tel", ph: "(00) 00000-0000", tipo: "tel", auto: "tel" },
        { chave: "end", rotulo: "Endereço completo", largo: true, ph: DICA_ENDERECO, auto: "street-address" },
        ...CAMPOS_SENHA
      ],
      privTexto: "Autorizo que prestadores vejam meu primeiro nome e bairro quando eu solicitar um serviço.",
      privNota: "Seu CPF, telefone e endereço completo nunca são exibidos publicamente. Nada é compartilhado sem a sua autorização, e você pode mudar isso a qualquer momento."
    },
    cnpj: {
      perfil: "cliente-cnpj",
      titulo: "Cadastro – Cliente CNPJ",
      sub: "Empresas e condomínios",
      botao: "Criar login de Cliente CNPJ",
      campos: [
        { chave: "cnpj", rotulo: "CNPJ", obrigatorio: true, mascara: "cnpj", ph: "00.000.000/0000-00" },
        { chave: "nome", rotulo: "Nome da empresa / condomínio", auto: "organization" },
        { chave: "resp", rotulo: "Responsável principal", dica: "Opcional – pode mudar com o tempo" },
        { chave: "tel", rotulo: "Telefone", obrigatorio: true, mascara: "tel", ph: "(00) 00000-0000", tipo: "tel", auto: "tel" },
        { chave: "end", rotulo: "Endereço completo", obrigatorio: true, largo: true, ph: DICA_ENDERECO, auto: "street-address" },
        ...CAMPOS_SENHA
      ],
      privTexto: "Autorizo exibir o nome da empresa/condomínio para prestadores.",
      privNota: "Telefone, endereço e responsável só são compartilhados com sua autorização. Clientes CPF não veem seus dados."
    },
    prest: {
      perfil: "prestador",
      titulo: "Cadastro – Prestador",
      sub: "Atende casas, condomínios e empresas",
      botao: "Criar login de Prestador",
      campos: [
        { chave: "cnpj", rotulo: "CNPJ", obrigatorio: true, mascara: "cnpj", ph: "00.000.000/0000-00" },
        { chave: "nome", rotulo: "Nome da empresa", auto: "organization" },
        { chave: "resp", rotulo: "Responsável principal", dica: "Opcional – pode mudar com o tempo" },
        { chave: "tel", rotulo: "Telefone", obrigatorio: true, mascara: "tel", ph: "(00) 00000-0000", tipo: "tel", auto: "tel" },
        { chave: "end", rotulo: "Endereço completo", obrigatorio: true, largo: true, ph: DICA_ENDERECO, auto: "street-address" },
        ...CAMPOS_SENHA
      ],
      privTexto: "Autorizo exibir o perfil da minha empresa nas buscas de clientes.",
      privNota: "Telefone, endereço e responsável só são mostrados a clientes com sua autorização."
    }
  };

  // "?perfil=" aceito na URL → cadastro que abre
  const PERFIL_URL = { prestador: "prest", cpf: "cpf", "cliente-cpf": "cpf", cliente_cpf: "cpf", cnpj: "cnpj", "cliente-cnpj": "cnpj", cliente_cnpj: "cnpj" };

  /* ---------- 2. ESTADO DA TELA ---------- */
  const estado = { loginAberto: true, criarAberto: true, tipoAberto: null };   // tipoAberto: cpf | cnpj | prest | null

  /* ---------- 3. UTILIDADES ---------- */
  const ICONE_OLHO = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/></svg>';
  const ICONE_OLHO_RISCADO = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M3 3l18 18"/><path d="M10.6 5.1A10 10 0 0 1 12 5c6.5 0 10 7 10 7a17 17 0 0 1-3.2 4.1M6.6 6.6A17 17 0 0 0 2 12s3.5 7 10 7a9.7 9.7 0 0 0 5.4-1.6"/><path d="M9.9 9.9a3 3 0 0 0 4.2 4.2"/></svg>';

  // Cria elemento: el("div", { class: "x" }, [filhos ou texto])
  function el(tag, atributos = {}, filhos = []) {
    const elemento = document.createElement(tag);
    for (const [nome, valor] of Object.entries(atributos)) {
      if (valor === undefined || valor === null || valor === false) continue;
      elemento.setAttribute(nome, valor === true ? "" : valor);
    }
    for (const filho of [].concat(filhos)) elemento.append(filho instanceof Node ? filho : document.createTextNode(filho));
    return elemento;
  }

  // Aplica um padrão como "000.000.000-00" aos dígitos digitados
  function formatar(digitos, padrao) {
    let saida = "", i = 0;
    for (const c of padrao) {
      if (i >= digitos.length) break;
      if (c === "0") { saida += digitos[i]; i++; } else saida += c;
    }
    return saida;
  }
  function aplicarMascara(tipo, valor) {
    const d = U.soDigitos(valor);
    if (tipo === "cpf") return formatar(d.slice(0, 11), "000.000.000-00");
    if (tipo === "cnpj") return formatar(d.slice(0, 14), "00.000.000/0000-00");
    if (tipo === "tel") return U.formatarTelefone(d);
    return valor;
  }

  // Botão de ver/ocultar senha
  function ligarOlho(botao, campo) {
    botao.innerHTML = ICONE_OLHO;
    botao.addEventListener("click", () => {
      const mostrar = campo.type === "password";
      campo.type = mostrar ? "text" : "password";
      botao.innerHTML = mostrar ? ICONE_OLHO_RISCADO : ICONE_OLHO;
      botao.setAttribute("aria-label", mostrar ? "Ocultar senha" : "Mostrar senha");
      botao.setAttribute("aria-pressed", String(mostrar));
    });
  }

  // Erros dos campos (usa .campo-erro do formulario.css)
  function mostrarErro(input, mensagem) {
    const span = document.getElementById(input.getAttribute("aria-describedby").split(" ").pop());
    input.setAttribute("aria-invalid", "true");
    span.textContent = mensagem;
  }
  function limparErro(input) {
    const ids = (input.getAttribute("aria-describedby") || "").split(" ");
    const span = document.getElementById(ids[ids.length - 1]);
    input.removeAttribute("aria-invalid");
    if (span && span.classList.contains("campo-erro")) span.textContent = "";
  }

  /* ---------- 4. MONTA OS 3 FORMULÁRIOS DE CADASTRO ---------- */
  function montarCadastros() {
    const destino = $("#cadastros");
    for (const [id, tipo] of Object.entries(TIPOS)) {
      const grade = el("div", { class: "form-grade" });

      for (const c of tipo.campos) {
        const idCampo = `${id}-${c.chave}`;
        const descricao = [c.dica ? `${idCampo}-dica` : null, `${idCampo}-erro`].filter(Boolean).join(" ");
        const input = el("input", {
          id: idCampo, name: c.chave,
          type: c.senha ? "password" : (c.tipo || "text"),
          placeholder: c.ph, autocomplete: c.auto || "off",
          inputmode: c.mascara ? "numeric" : undefined,
          required: c.obrigatorio || undefined,
          "aria-describedby": descricao
        });
        if (c.mascara) input.addEventListener("input", () => { input.value = aplicarMascara(c.mascara, input.value); });
        input.addEventListener("input", () => limparErro(input));

        const rotulo = el("label", { for: idCampo }, [c.rotulo]);
        if (c.obrigatorio) rotulo.append(el("span", { class: "obrigatorio", "aria-hidden": "true" }, [" *"]));

        let caixa = input;
        if (c.senha) {
          const olho = el("button", { type: "button", class: "btn-olho", "aria-label": "Mostrar senha", "aria-pressed": "false" });
          caixa = el("div", { class: "senha-caixa" }, [input, olho]);
          ligarOlho(olho, input);
        }

        const bloco = el("div", { class: c.largo ? "campo largura-total" : "campo" }, [rotulo, caixa]);
        if (c.dica) bloco.append(el("span", { class: "nota", id: `${idCampo}-dica` }, [c.dica]));
        bloco.append(el("span", { class: "campo-erro", id: `${idCampo}-erro` }));
        grade.append(bloco);
      }

      const privacidade = el("div", { class: "privacidade" }, [
        el("div", { class: "campo campo-check" }, [
          el("input", { id: `${id}-priv`, name: "autorizacao", type: "checkbox" }),
          el("label", { for: `${id}-priv` }, [tipo.privTexto])
        ]),
        el("p", { class: "nota" }, [tipo.privNota])
      ]);

      const msg = el("div", { class: "mensagem", role: "alert" });
      const form = el("form", { novalidate: true }, [grade, privacidade, msg, el("button", { type: "submit", class: "btn btn-grande" }, [tipo.botao])]);
      form.addEventListener("submit", (e) => { e.preventDefault(); enviarCadastro(id, form, msg); });

      const subtitulo = el("p", { class: "login-texto" }, [tipo.sub + " · ", el("span", { class: "obrigatorio" }, ["*"]), " obrigatório"]);
      destino.append(el("div", { id: `cadastro-${id}`, class: "cadastro", hidden: true }, [el("h3", {}, [tipo.titulo]), subtitulo, form]));
    }
  }

  /* ---------- 5. VALIDAÇÃO E ENVIO DO CADASTRO ---------- */
  function enviarCadastro(id, form, msg) {
    const tipo = TIPOS[id];
    const pegar = (chave) => document.getElementById(`${id}-${chave}`);
    let primeiroErro = null;
    const erro = (input, texto) => { mostrarErro(input, texto); primeiroErro = primeiroErro || input; };

    for (const c of tipo.campos) {
      const input = pegar(c.chave), valor = input.value.trim();
      limparErro(input);
      if (c.obrigatorio && !valor) { erro(input, "Campo obrigatório."); continue; }
      if (!valor) continue;
      if (c.mascara === "cpf" && U.soDigitos(valor).length !== 11) erro(input, "CPF incompleto.");
      if (c.mascara === "cnpj" && U.soDigitos(valor).length !== 14) erro(input, "CNPJ incompleto.");
      if (c.mascara === "tel" && !U.telefoneValido(valor)) erro(input, "Telefone incompleto.");
    }
    const senha = pegar("senha"), senha2 = pegar("senha2");
    // Mesma regra de senha usada no "Editar perfil": 8+ caracteres com letras e números
    if (senha.value && (senha.value.length < 8 || !/[A-Za-z]/.test(senha.value) || !/\d/.test(senha.value))) erro(senha, "A senha precisa de 8+ caracteres, com letras e números.");
    if (senha2.value && senha2.value !== senha.value) erro(senha2, "As senhas não conferem.");

    if (primeiroErro) {
      U.mostrarMensagem(msg, "erro", "Confira os campos destacados.");
      primeiroErro.focus();
      return;
    }
    U.limparMensagem(msg);

    // Aqui entrará o envio ao servidor. Senhas NUNCA são guardadas no navegador.
    const nome = id === "cpf" ? pegar("login").value.trim() : (pegar("nome").value.trim() || SD_ACESSO_NOME(tipo.perfil));
    senha.value = ""; senha2.value = "";
    entrar(tipo.perfil, nome);
  }

  const SD_ACESSO_NOME = (perfil) => (window.SD_ACESSO ? window.SD_ACESSO.nomePerfil(perfil) : perfil);

  /* ---------- 6. FAZER LOGIN ---------- */
  function enviarLogin(e) {
    e.preventDefault();
    const id = $("#login-id"), senha = $("#login-senha"), msg = $("#msg-login");
    [id, senha].forEach(limparErro);
    U.limparMensagem(msg);
    if (!id.value.trim()) mostrarErro(id, "Informe seu e-mail, CPF/CNPJ ou telefone.");
    if (!senha.value) mostrarErro(senha, "Informe a senha.");
    if (!id.value.trim() || !senha.value) {
      U.mostrarMensagem(msg, "erro", "Preencha os campos destacados.");
      (id.value.trim() ? senha : id).focus();
      return;
    }
    if (!SD.config.modoDemonstracao) {
      // Sem servidor e sem demonstração: não há como conferir a senha
      U.mostrarMensagem(msg, "atencao", "O login ainda não está disponível: o servidor não foi conectado.");
      return;
    }
    // Aqui entrará a consulta ao servidor, que devolve o tipo real do usuário.
    senha.value = "";
    entrar($("#login-demo-tipo").value, id.value.trim());
  }

  // Guarda a sessão de demonstração e leva para o destino (se permitido) ou para o início
  function entrar(perfil, nome) {
    if (!SD.config.modoDemonstracao || !SD.sessaoDemo.entrar(perfil, nome)) {
      U.mostrarMensagem($("#aviso"), "atencao", "Cadastro validado, mas o login ainda depende do servidor (não conectado).");
      return;
    }
    const destino = parametros.get("destino");
    const item = SD.config.menu.find((m) => m.id === destino);
    const permitido = item && window.SD_ACESSO && window.SD_ACESSO.pode(perfil, item.id);
    location.href = permitido ? SD.caminho(item.href) : SD.urlPagina("inicio");
  }

  /* ---------- 7. ATUALIZA O QUE APARECE ---------- */
  function atualizarTela() {
    $("#btn-abrir-login").setAttribute("aria-expanded", String(estado.loginAberto));
    $("#form-login").hidden = !estado.loginAberto;
    $("#btn-abrir-criar").setAttribute("aria-expanded", String(estado.criarAberto));
    $("#corpo-criar").hidden = !estado.criarAberto;
    $$(".tipo-conta").forEach((b) => b.setAttribute("aria-expanded", String(estado.tipoAberto === b.dataset.tipo)));
    for (const id of Object.keys(TIPOS)) $(`#cadastro-${id}`).hidden = estado.tipoAberto !== id;
  }

  // Já está logado (sessão de demonstração)? Mostra atalhos em vez dos formulários.
  function mostrarJaConectado() {
    if (!SD.logado()) return false;
    const nome = document.body.dataset.nome;
    $("#texto-conectado").textContent = `Conectado como ${SD_ACESSO_NOME(SD.tipoUsuario())}${nome ? ` (${nome})` : ""}. Para entrar com outra conta, saia primeiro.`;
    $("#btn-ir-inicio").href = SD.urlPagina("inicio");
    $("#btn-ir-perfil").href = SD.urlPerfil();
    $("#btn-sair-conta").href = SD.urlPagina("sair");
    $("#ja-conectado").hidden = false;
    $("#login-colunas").hidden = true;
    return true;
  }

  // Abre a parte certa conforme o endereço (links da Home e da NavBar)
  function lerEndereco() {
    if (parametros.get("acao") === "criar-conta") {
      estado.loginAberto = false;          // economiza tela: mostra só o cadastro
      estado.criarAberto = true;
      estado.tipoAberto = PERFIL_URL[parametros.get("perfil")] || null;   // "cliente" sozinho: a pessoa escolhe CPF ou CNPJ
    }
    if (parametros.get("sair") === "1") U.mostrarMensagem($("#aviso"), "sucesso", "Você saiu da sua conta.");
    else if (parametros.has("destino")) U.mostrarMensagem($("#aviso"), "info", "Entre na sua conta para acessar essa área.");
  }

  /* ---------- 8. INÍCIO ---------- */
  function iniciar() {
    // A demonstração (escolher o tipo de conta) só aparece no modo demonstração
    $("#bloco-demo").hidden = !SD.config.modoDemonstracao;
    if (mostrarJaConectado()) return;

    montarCadastros();
    ligarOlho($('[data-alvo="login-senha"]'), $("#login-senha"));
    $("#form-login").addEventListener("submit", enviarLogin);
    $("#login-id").addEventListener("input", (e) => limparErro(e.target));
    $("#login-senha").addEventListener("input", (e) => limparErro(e.target));

    $("#btn-abrir-login").addEventListener("click", () => { estado.loginAberto = !estado.loginAberto; atualizarTela(); });
    $("#btn-abrir-criar").addEventListener("click", () => { estado.criarAberto = !estado.criarAberto; atualizarTela(); });
    // Tipos de conta: clicar abre; clicar no mesmo recolhe; clicar em outro troca
    $$(".tipo-conta").forEach((b) => b.addEventListener("click", () => {
      estado.tipoAberto = estado.tipoAberto === b.dataset.tipo ? null : b.dataset.tipo;
      atualizarTela();
    }));
    // Recuperação de acesso: depende do servidor
    $$("[data-recuperar]").forEach((b) => b.addEventListener("click", () => {
      U.mostrarMensagem($("#msg-login"), "info", `A recuperação ${b.dataset.recuperar === "senha" ? "de senha" : "do login"} ainda não está disponível: depende do servidor (envio por e-mail/SMS).`);
    }));

    lerEndereco();
    atualizarTela();
    if (parametros.get("acao") === "criar-conta") requestAnimationFrame(() => $("#cartao-criar").scrollIntoView({ block: "start" }));
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar);
  else iniciar();
})();
