/* =====================================================================
   S.D — UTILIDADES COMPARTILHADAS (componentes/utilidades/utilidades.js)
   Funções pequenas usadas por vários componentes e páginas, guardadas
   em UM lugar só (antes cada perfil tinha a sua cópia):
     formatar telefone, CEP, data e dinheiro · validar e-mail/telefone ·
     estrelas de avaliação · fotos com reserva (padrão → ícone) · mensagens.
   Não depende de nenhum outro arquivo. Uso: window.SDUtil.<função>
   ===================================================================== */
(function () {
  "use strict";

  /* ---------- 1. TEXTO E NÚMEROS ---------- */
  const soDigitos = (v) => String(v || "").replace(/\D/g, "");

  // (11) 91234-5678 / (11) 3123-4567 — formata enquanto a pessoa digita
  function formatarTelefone(v) {
    const d = soDigitos(v).slice(0, 11);
    if (d.length <= 2) return d ? "(" + d : "";
    if (d.length <= 6) return `(${d.slice(0, 2)}) ${d.slice(2)}`;
    if (d.length <= 10) return `(${d.slice(0, 2)}) ${d.slice(2, 6)}-${d.slice(6)}`;
    return `(${d.slice(0, 2)}) ${d.slice(2, 7)}-${d.slice(7)}`;
  }
  // 01000-000
  function formatarCep(v) {
    const d = soDigitos(v).slice(0, 8);
    return d.length > 5 ? `${d.slice(0, 5)}-${d.slice(5)}` : d;
  }
  // "2026-10-02" → "02/10/2026" (sem fuso horário, para não mudar o dia)
  function formatarData(iso) {
    if (!iso) return "—";
    const [a, m, d] = String(iso).split("-");
    return `${d}/${m}/${a}`;
  }
  // Data de hoje no formato AAAA-MM-DD
  function hojeISO() {
    const h = new Date();
    return `${h.getFullYear()}-${String(h.getMonth() + 1).padStart(2, "0")}-${String(h.getDate()).padStart(2, "0")}`;
  }
  const formatarMoeda = (v) => Number(v || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
  const decimal = (n) => Number(n).toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  // "a, b , ,c" → ["a","b","c"] (sem repetidos)
  const listaDeTexto = (t) => [...new Set(String(t || "").split(",").map((x) => x.trim()).filter(Boolean))];

  /* ---------- 2. VALIDAÇÕES ---------- */
  const telefoneValido = (v) => /^\d{10,11}$/.test(soDigitos(v));
  const emailValido = (v) => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v);

  /* ---------- 3. MENSAGENS (usa as classes .mensagem do base.css) ---------- */
  function mostrarMensagem(el, tipo, texto) {   // tipo: sucesso | erro | info | atencao
    el.className = "mensagem " + tipo;
    el.textContent = texto;
  }
  function limparMensagem(el) { el.className = "mensagem"; el.textContent = ""; }

  /* ---------- 4. ESTRELAS DE AVALIAÇÃO (cheia / meia / vazia) ----------
     Cada chamada usa um prefixo único: evita ids repetidos na página. */
  let contadorEstrelas = 0;
  function estrelasSVG(media) {
    const pre = "sd-est" + (++contadorEstrelas);
    let html = '<span class="estrelas-icones" aria-hidden="true">';
    for (let i = 1; i <= 5; i++) {
      const cheia = media >= i;                  // estrela cheia só quando atinge o valor
      const meia = !cheia && media >= i - 0.5;   // meia estrela a partir de ,5
      const id = `${pre}-${i}`;
      html += `<svg viewBox="0 0 24 24"><defs><linearGradient id="${id}"><stop offset="50%" stop-color="currentColor"/><stop offset="50%" stop-color="transparent"/></linearGradient></defs><path d="M12 2.5l2.9 6 6.6.9-4.8 4.6 1.2 6.5L12 17.4l-5.9 3.1 1.2-6.5L2.5 9.4l6.6-.9z" fill="${cheia ? "currentColor" : meia ? `url(#${id})` : "none"}" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/></svg>`;
    }
    return html + "</span>";
  }

  /* ---------- 5. ÍCONES PROVISÓRIOS (enquanto as fotos padrão não existem) ----------
     tipo: "pessoa" (Cliente CPF) | "casa" (cliente casa) | "predio" (Cliente CNPJ)
           | "prestador" (engrenagem com capacete) */
  const DESENHOS = {
    pessoa: '<circle cx="100" cy="80" r="32" fill="#800000"/><path d="M40 170a60 60 0 0 1 120 0Z" fill="#800000"/>',
    casa: '<path d="M50 104 100 60l50 44v50H50Z" fill="#800000"/><rect x="88" y="118" width="24" height="36" fill="#EADFD6"/>',
    predio: '<rect x="62" y="48" width="76" height="112" rx="4" fill="#800000"/>' +
      '<g fill="#EADFD6"><rect x="76" y="62" width="16" height="14"/><rect x="108" y="62" width="16" height="14"/>' +
      '<rect x="76" y="88" width="16" height="14"/><rect x="108" y="88" width="16" height="14"/>' +
      '<rect x="76" y="114" width="16" height="14"/><rect x="108" y="114" width="16" height="14"/>' +
      '<rect x="91" y="138" width="18" height="22"/></g>',
    prestador: '<g fill="none" stroke="#800000" stroke-width="12"><circle cx="100" cy="112" r="34"/>' +
      '<path d="M100 58v16M100 150v16M46 112h16M138 112h16M62 74l11 11M127 139l11 11M62 150l11-11M127 85l11-11"/></g>' +
      '<path d="M58 60a42 30 0 0 1 84 0Z" fill="#800000"/><rect x="48" y="58" width="104" height="8" rx="4" fill="#800000"/>'
  };
  const paraDataUrl = (svg) => "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
  function iconeProvisorio(tipo) {
    return paraDataUrl(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect width="200" height="200" fill="#EADFD6"/>${DESENHOS[tipo] || DESENHOS.pessoa}</svg>`);
  }
  // Avatar com as iniciais do nome (ex.: administrador sem foto)
  function iconeIniciais(nome) {
    const partes = String(nome || "").trim().split(/\s+/).filter(Boolean);
    const txt = ((partes[0] || "")[0] || "") + ((partes.length > 1 ? partes[partes.length - 1] : "")[0] || "");
    return paraDataUrl(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect width="200" height="200" fill="#EADFD6"/><text x="100" y="118" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="64" font-weight="700" fill="#800000" text-anchor="middle">${txt.toUpperCase()}</text></svg>`);
  }

  /* ---------- 6. FOTO COM RESERVA ----------
     Tenta a foto da pessoa → se falhar, a foto padrão do sistema → se
     também falhar (arquivo ainda não criado), o ícone provisório. */
  function aplicarFoto(img, url, padrao, tipoIcone) {
    img.onerror = () => {
      if (img.dataset.etapa === "padrao" || !padrao) { img.onerror = null; img.src = iconeProvisorio(tipoIcone); return; }
      img.dataset.etapa = "padrao"; img.src = padrao;
    };
    img.dataset.etapa = url ? "foto" : "padrao";
    img.src = url || padrao || iconeProvisorio(tipoIcone);
  }

  /* ---------- 7. TABELAS PEQUENAS (linha "rótulo | valor") ---------- */
  function linhaTabela(rotulo, conteudo) {
    const tr = document.createElement("tr");
    const th = document.createElement("th");
    th.scope = "row";
    th.textContent = rotulo;
    const td = document.createElement("td");
    if (typeof conteudo === "string") td.textContent = conteudo; else td.append(conteudo);
    tr.append(th, td);
    return tr;
  }

  window.SDUtil = Object.freeze({
    soDigitos, formatarTelefone, formatarCep, formatarData, hojeISO, formatarMoeda, decimal, listaDeTexto,
    telefoneValido, emailValido, mostrarMensagem, limparMensagem,
    estrelasSVG, iconeProvisorio, iconeIniciais, aplicarFoto, linhaTabela
  });
})();
