/* =====================================================================
   S.D SERVIÇOS DIGITAIS — CONFIGURAÇÃO ÚNICA (configuracoes/config.js)
   Ordem dos scripts em TODA página (todos com "defer"):
     1. ../seguranca/acesso.js   → regras de quem vê o quê
     2. ../configuracoes/config.js (este arquivo)
     3. ../navbar/navbar.js  e  ../rodape/rodape.js
     4. componentes e o script da própria página
   Aqui ficam: caminhos das páginas, menu, rodapé, lojas, ícones,
   sessão de demonstração e funções usadas pela NavBar e pelo Rodapé.

   Cada página informa no <body>:
     data-pagina="inicio"   → id do item do menu que fica destacado
     data-logado="nao|sim"  → o SERVIDOR preenche (só muda a TELA)
     data-tipo="cliente-cpf|cliente-cnpj|prestador|adm" (quando logado)
     data-raiz="../"        → caminho até a pasta SDOnline
   ATENÇÃO: esconder/mostrar na tela NÃO é segurança. O controle de
   acesso real tem de ser feito no servidor.
   ===================================================================== */
(function () {
  "use strict";

  /* ---------- 1. CONFIGURAÇÃO (editar aqui) ---------- */
  const CONFIG = {
    nome: "S.D Serviços Digitais",
    descricao: "Conectando clientes a prestadores de serviço.",
    logo: "fotos/marca/logo.svg",            // usado como ícone da aba

    // DEMONSTRAÇÃO (sem servidor): o login de teste fica guardado só nesta aba
    // do navegador (sessionStorage) para dar para navegar logado entre as páginas.
    // Quando o servidor existir: trocar para false.
    modoDemonstracao: true,

    // Caminhos a partir da pasta SDOnline (cada página = <pasta>/index.html)
    paginas: {
      inicio:      "home/index.html",
      login:       "login-cadastro/index.html",
      cadastro:    "login-cadastro/index.html?acao=criar-conta",
      sair:        "login-cadastro/index.html?sair=1",
      avaliacoes:  "avaliacoes/index.html",
      privacidade: "politica-privacidade/index.html",
      termos:      "termos/index.html"
    },

    // "Meu perfil" abre a página do tipo de usuário (data-tipo no <body>)
    perfilPorTipo: {
      "adm":          "perfil-adm/index.html",
      "cliente-cpf":  "perfil-cliente-cpf/index.html",
      "cliente-cnpj": "perfil-cliente-cnpj/index.html",
      "prestador":    "perfil-prestador/index.html"
    },

    // Itens da NavBar (7). requerLogin: cadeado + vai ao login até a pessoa entrar.
    // Depois do login, o item só aparece se seguranca/acesso.js permitir.
    menu: [
      { id: "inicio",    texto: "Início",            href: "home/index.html" },
      { id: "servicos",  texto: "Serviços",          href: "home/index.html#servicos" },
      { id: "clientes",  texto: "Para clientes",     href: "localizar-prestador/index.html",   requerLogin: true },
      { id: "prestador", texto: "Seja um prestador", href: "localizar-condominios/index.html", requerLogin: true },
      { id: "sobre",     texto: "Sobre nós",         href: "sobre/index.html" },
      { id: "politicas", texto: "Políticas",         href: "politicas/index.html" },
      { id: "suporte",   texto: "Suporte",           href: "suporte/index.html" }
    ],

    // Rodapé
    rodapeLinks: ["servicos", "clientes", "prestador", "sobre", "suporte"],
    rodapePoliticas: [
      { texto: "Política da empresa",       href: "politicas/index.html" },
      { texto: "Termos de uso",             href: "termos/index.html" },
      { texto: "Termo de responsabilidade", href: "responsabilidade/index.html" }
    ],
    // Lojas: deixar href vazio até o app ser publicado (mostra "Em breve")
    lojas: [
      { nome: "Google Play", href: "" },
      { nome: "App Store",   href: "" }
    ]
  };

  /* ---------- 2. ÍCONES (SVG, cor herdada) ---------- */
  const svg = (conteudo, traco = 2) =>
    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${traco}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">${conteudo}</svg>`;
  const ICONES = {
    // Logo provisória: engrenagem com capacete (trocar pelo arquivo oficial)
    logo: '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true" focusable="false"><circle cx="24" cy="29" r="9"/><circle cx="24" cy="29" r="3.5"/><path d="M24 16v3M24 39v3M11 29h3M34 29h3M14.8 19.8l2.1 2.1M31.1 36.1l2.1 2.1M14.8 38.2l2.1-2.1M31.1 21.9l2.1-2.1"/><path d="M12 15a12 9 0 0 1 24 0Z" fill="currentColor" stroke="none"/><path d="M9 15.5h30"/></svg>',
    cadeado: svg('<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>', 2.2).replace("<svg ", '<svg class="cadeado" '),
    lua:     svg('<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z"/>'),
    sol:     svg('<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>'),
    usuario: svg('<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>'),
    sair:    svg('<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>'),
    entrar:  svg('<path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M15 12H3"/>'),
    menu:    svg('<path d="M4 6h16M4 12h16M4 18h16"/>', 2.2),
    fechar:  svg('<path d="M18 6 6 18M6 6l12 12"/>', 2.2),
    celular: svg('<rect x="6" y="2" width="12" height="20" rx="2"/><path d="M11 18h2"/>')
  };

  /* ---------- 3. SESSÃO DE DEMONSTRAÇÃO (sem servidor) ----------
     Guarda só { tipo, nome } nesta aba do navegador. NUNCA guarda senha.
     Na versão final quem diz se a pessoa está logada é o SERVIDOR. */
  const CHAVE_SESSAO = "sd-sessao-demonstracao";
  const acesso = window.SD_ACESSO;
  const sessaoDemo = {
    ler() {
      if (!CONFIG.modoDemonstracao) return null;
      try {
        const s = JSON.parse(sessionStorage.getItem(CHAVE_SESSAO) || "null");
        return s && acesso && acesso.perfilValido(s.tipo) && s.tipo !== "visitante" ? s : null;
      } catch (_) { return null; }
    },
    entrar(tipo, nome) {
      if (!CONFIG.modoDemonstracao) return false;
      try { sessionStorage.setItem(CHAVE_SESSAO, JSON.stringify({ tipo, nome: String(nome || "").slice(0, 60) })); return true; }
      catch (_) { return false; }
    },
    sair() {
      try { sessionStorage.removeItem(CHAVE_SESSAO); } catch (_) { /* navegador sem armazenamento */ }
    }
  };

  // "?sair=1" encerra a sessão ANTES de montar a NavBar (assim ela já aparece deslogada)
  if (new URLSearchParams(location.search).get("sair") === "1") sessaoDemo.sair();

  // Aplica a sessão de demonstração no <body> (como o servidor faria)
  (function aplicarSessao() {
    const s = sessaoDemo.ler();
    if (!s || !document.body) return;
    document.body.dataset.logado = "sim";
    document.body.dataset.tipo = s.tipo;
    if (s.nome) document.body.dataset.nome = s.nome;
  })();

  /* ---------- 4. ESTADO DA PÁGINA (lido do <body>) ---------- */
  const corpo = () => document.body || document.createElement("body");
  const raiz = () => corpo().dataset.raiz || "";
  const logado = () => corpo().dataset.logado === "sim";
  const paginaAtual = () => corpo().dataset.pagina || "";
  const tipoUsuario = () => (logado() ? corpo().dataset.tipo || "" : "visitante");
  // Aberto pelo app (?plataforma=app) ou instalado (standalone) → esconde "Baixe o app"
  const ehApp = () =>
    new URLSearchParams(location.search).get("plataforma") === "app" ||
    (typeof window.matchMedia === "function" && window.matchMedia("(display-mode: standalone)").matches);

  /* ---------- 5. FUNÇÕES DE APOIO ---------- */
  // Escapa texto antes de colocar no HTML (evita injeção)
  const esc = (t) => String(t).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  // Monta o caminho a partir da raiz do site (links externos e data:/blob: ficam iguais)
  const caminho = (rel) => (/^(https?:|mailto:|tel:|data:|blob:|#)/i.test(rel) ? rel : raiz() + rel);

  const urlPagina = (nome) => caminho(CONFIG.paginas[nome] || CONFIG.paginas.inicio);
  const urlPerfil = () => caminho(CONFIG.perfilPorTipo[tipoUsuario()] || CONFIG.perfilPorTipo["cliente-cpf"]);
  // Pode ver o recurso? (usa seguranca/acesso.js; sem o arquivo, mostra tudo)
  const pode = (recurso) => (acesso ? acesso.pode(tipoUsuario(), recurso) : true);

  // Item bloqueado → login com destino; liberado → página real
  function hrefItem(item) {
    if (item.requerLogin && !logado()) {
      return `${urlPagina("login")}?destino=${encodeURIComponent(item.id)}`;
    }
    return caminho(item.href);
  }
  // Itens que aparecem: visitante vê todos (os bloqueados com cadeado);
  // logado vê só os permitidos para o seu tipo (ex.: prestador não vê "Para clientes").
  const itemVisivel = (item) => !logado() || pode(item.id);

  // <a> de um item do menu (usado na NavBar e no Rodapé)
  function linkMenu(item, marcarAtual) {
    const bloqueado = item.requerLogin && !logado();
    const atual = marcarAtual && item.id === paginaAtual() ? ' aria-current="page"' : "";
    const extra = bloqueado ? ` aria-label="${esc(item.texto)} (requer login)" title="Disponível após entrar na conta"` : "";
    return `<a href="${esc(hrefItem(item))}"${atual}${extra}>${bloqueado ? ICONES.cadeado : ""}<span>${esc(item.texto)}</span></a>`;
  }

  // Ícone da aba do navegador (se a página não tiver um)
  if (!document.querySelector('link[rel~="icon"]') && document.head) {
    const icone = document.createElement("link");
    icone.rel = "icon";
    icone.type = "image/svg+xml";
    icone.href = caminho(CONFIG.logo);
    document.head.appendChild(icone);
  }

  /* ---------- 6. EXPORTA PARA navbar.js, rodape.js e páginas ---------- */
  window.SD = Object.freeze({
    config: CONFIG, icones: ICONES, sessaoDemo,
    esc, caminho, urlPagina, urlPerfil, hrefItem, linkMenu, itemVisivel, pode,
    logado, paginaAtual, tipoUsuario, ehApp
  });
})();
