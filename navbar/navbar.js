/* =====================================================================
   S.D — NAVBAR (navbar/navbar.js)
   Monta a barra do topo a partir de configuracoes/config.js (window.SD),
   controla o tema claro/escuro e o menu compacto.
   Itens do menu: visitante vê todos (com cadeado nos que pedem login);
   logado vê só os liberados para o seu tipo (seguranca/acesso.js).
   Precisa de: <header id="sd-navbar"></header> na página.
   ===================================================================== */
(function () {
  "use strict";

  if (!window.SD) {
    console.error("[S.D] navbar.js: carregue configuracoes/config.js antes deste arquivo.");
    return;
  }
  const SD = window.SD;
  const I = SD.icones;

  /* ---------- 1. MONTAR A BARRA ---------- */
  function montar() {
    const alvo = document.getElementById("sd-navbar");
    if (!alvo) return false;
    alvo.classList.add("navbar");

    const ehPerfil = SD.paginaAtual() === "perfil" ? ' aria-current="page"' : "";
    const conta = SD.logado()
      ? `<a class="nav-btn" href="${SD.esc(SD.urlPerfil())}" aria-label="Meu perfil"${ehPerfil}>${I.usuario}<span class="rotulo-oculto-celular">Meu perfil</span></a>
         <a class="nav-btn" href="${SD.esc(SD.urlPagina("sair"))}" aria-label="Sair da conta">${I.sair}<span class="rotulo-oculto-celular">Sair</span></a>`
      : `<a class="nav-btn" href="${SD.esc(SD.urlPagina("login"))}" aria-label="Entrar">${I.entrar}<span class="rotulo-oculto-celular">Entrar</span></a>
         <a class="nav-btn nav-btn-destaque" href="${SD.esc(SD.urlPagina("cadastro"))}"><span>Criar conta</span></a>`;

    alvo.innerHTML = `
      <a class="pular-conteudo" href="#conteudo">Pular para o conteúdo</a>
      <nav class="navbar-conteudo" aria-label="Navegação principal">
        <a class="marca" href="${SD.esc(SD.urlPagina("inicio"))}" aria-label="${SD.esc(SD.config.nome)} — página inicial">
          ${I.logo}<span class="marca-texto" aria-hidden="true">Serviços<br>Digitais</span>
        </a>
        <ul class="menu" id="sd-menu">
          ${SD.config.menu.filter(SD.itemVisivel).map((item) => `<li>${SD.linkMenu(item, true)}</li>`).join("")}
        </ul>
        <div class="nav-direita">
          <button type="button" class="nav-btn" id="sd-btn-tema" aria-pressed="false" aria-label="Ativar tema escuro">${I.lua}</button>
          ${conta}
          <button type="button" class="nav-btn btn-menu" id="sd-btn-menu" aria-expanded="false" aria-controls="sd-menu" aria-label="Abrir menu">${I.menu}</button>
        </div>
      </nav>`;
    return true;
  }

  /* ---------- 2. TEMA (sempre abre no claro; escuro só se o usuário escolher) ---------- */
  function iniciarTema() {
    const btn = document.getElementById("sd-btn-tema");
    if (!btn) return;
    const html = document.documentElement;
    html.setAttribute("data-tema", "claro");
    btn.addEventListener("click", () => {
      const escuro = html.getAttribute("data-tema") !== "escuro";
      html.setAttribute("data-tema", escuro ? "escuro" : "claro");
      btn.innerHTML = escuro ? I.sol : I.lua;
      btn.setAttribute("aria-pressed", String(escuro));
      btn.setAttribute("aria-label", escuro ? "Ativar tema claro" : "Ativar tema escuro");
    });
  }

  /* ---------- 3. MENU COMPACTO (3 riscos) ---------- */
  function iniciarMenu() {
    const btn = document.getElementById("sd-btn-menu");
    const menu = document.getElementById("sd-menu");
    const barra = document.getElementById("sd-navbar");
    if (!btn || !menu || !barra) return;

    const definir = (aberto) => {
      menu.classList.toggle("aberto", aberto);
      btn.setAttribute("aria-expanded", String(aberto));
      btn.setAttribute("aria-label", aberto ? "Fechar menu" : "Abrir menu");
      btn.innerHTML = aberto ? I.fechar : I.menu;
    };
    const aberto = () => menu.classList.contains("aberto");

    btn.addEventListener("click", () => definir(!aberto()));
    // Esc fecha e devolve o foco ao botão
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && aberto()) { definir(false); btn.focus(); }
    });
    // Clique fora da barra fecha (composedPath: funciona mesmo depois que o ícone do botão foi trocado)
    document.addEventListener("click", (e) => {
      if (aberto() && !e.composedPath().includes(barra)) definir(false);
    });
    // Clicar num item (ex.: "Serviços" com #) fecha o menu
    menu.addEventListener("click", (e) => { if (e.target.closest("a")) definir(false); });
    // Ao aumentar a tela, o menu volta ao normal
    window.addEventListener("resize", () => { if (aberto() && getComputedStyle(btn).display === "none") definir(false); });
  }

  /* ---------- 4. INÍCIO ---------- */
  function iniciar() {
    if (!montar()) return;
    iniciarTema();
    iniciarMenu();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar);
  else iniciar();
})();
