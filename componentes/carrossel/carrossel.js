/* =====================================================================
   S.D — CARROSSEL DE FOTOS (componentes/carrossel/carrossel.js)
   Componente reutilizável. Usado nos perfis (fotos do local do Cliente
   CNPJ, fotos dos serviços realizados, fotos de trabalhos do Prestador
   e fotos do quadro de serviços). Depende de componentes/carrossel/carrossel.css.

   Como usar:
     const c = SDCarrossel.criar({
       alvo: elemento,                 // onde o carrossel será montado
       rotulo: "Fotos do serviço",     // nome lido por leitores de tela
       fotos: [{ src, alt, legenda }], // legenda é opcional
       vazio: "Nenhuma foto.",         // texto quando não há fotos
       aoMudar: (indice) => {}         // opcional: avisa a foto atual
     });
     c.atualizar(novasFotos, indice);  c.irPara(2);  c.indice;

   Navegação: setas na tela, pontos, teclado (← → Home End),
   deslizar no celular/trackpad e arrastar com o mouse.
   ===================================================================== */
(function () {
  "use strict";

  const SETA_ESQ = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><path d="m15 18-6-6 6-6"/></svg>';
  const SETA_DIR = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><path d="m9 18 6-6-6-6"/></svg>';

  // Respeita "reduzir movimento" do sistema
  const movimento = () =>
    window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth";

  function criar(opcoes) {
    const { alvo, rotulo = "Fotos", vazio = "Nenhuma foto.", aoMudar } = opcoes;
    let fotos = Array.isArray(opcoes.fotos) ? opcoes.fotos.slice() : [];
    let atual = 0;

    /* ---------- 1. ESTRUTURA ---------- */
    const raiz = document.createElement("div");
    raiz.className = "carrossel";
    raiz.setAttribute("role", "region");
    raiz.setAttribute("aria-roledescription", "carrossel");
    raiz.setAttribute("aria-label", rotulo);
    raiz.innerHTML = `
      <div class="carrossel-janela">
        <div class="carrossel-trilho" tabindex="0"></div>
        <button type="button" class="btn btn-icone btn-seta carrossel-ant" aria-label="Foto anterior">${SETA_ESQ}</button>
        <button type="button" class="btn btn-icone btn-seta carrossel-prox" aria-label="Próxima foto">${SETA_DIR}</button>
      </div>
      <div class="carrossel-rodape">
        <div class="carrossel-pontos"></div>
        <span class="carrossel-contador" aria-live="polite" aria-atomic="true"></span>
      </div>
      <p class="carrossel-vazio" hidden></p>`;
    const janela = raiz.querySelector(".carrossel-janela");
    const trilho = raiz.querySelector(".carrossel-trilho");
    const pontos = raiz.querySelector(".carrossel-pontos");
    const contador = raiz.querySelector(".carrossel-contador");
    const rodape = raiz.querySelector(".carrossel-rodape");
    const btnAnt = raiz.querySelector(".carrossel-ant");
    const btnProx = raiz.querySelector(".carrossel-prox");
    const textoVazio = raiz.querySelector(".carrossel-vazio");
    trilho.setAttribute("aria-label", rotulo + " — use as setas do teclado para trocar de foto");
    textoVazio.textContent = vazio;
    alvo.append(raiz);

    /* ---------- 2. DESENHO ---------- */
    function renderizar() {
      trilho.innerHTML = "";
      pontos.innerHTML = "";
      const total = fotos.length;
      fotos.forEach((f, i) => {
        const slide = document.createElement("div");
        slide.className = "carrossel-slide";
        slide.setAttribute("role", "group");
        slide.setAttribute("aria-roledescription", "foto");
        slide.setAttribute("aria-label", `${i + 1} de ${total}`);
        const fig = document.createElement("figure");
        const img = document.createElement("img");
        img.src = f.src;
        img.alt = f.alt || f.legenda || `Foto ${i + 1}`;
        img.loading = "lazy";
        img.decoding = "async";
        img.draggable = false;
        fig.append(img);
        if (f.legenda) {
          const leg = document.createElement("figcaption");
          leg.textContent = f.legenda;
          fig.append(leg);
        }
        slide.append(fig);
        trilho.append(slide);

        const ponto = document.createElement("button");
        ponto.type = "button";
        ponto.className = "carrossel-ponto";
        ponto.setAttribute("aria-label", `Ir para a foto ${i + 1}`);
        ponto.addEventListener("click", () => irPara(i));
        pontos.append(ponto);
      });

      const temFotos = total > 0, varias = total > 1;
      janela.hidden = !temFotos;
      rodape.hidden = !temFotos;
      textoVazio.hidden = temFotos;
      btnAnt.hidden = btnProx.hidden = !varias;   // 1 foto: sem setas
      pontos.hidden = !varias;
      atual = Math.min(atual, Math.max(0, total - 1));
      marcar(atual);
      trilho.scrollLeft = atual * trilho.clientWidth;
    }

    // Atualiza pontos, contador e slides visíveis
    function marcar(i) {
      atual = i;
      [...pontos.children].forEach((p, n) => p.setAttribute("aria-current", n === i ? "true" : "false"));
      [...trilho.children].forEach((s, n) => s.setAttribute("aria-hidden", n === i ? "false" : "true"));
      contador.textContent = fotos.length ? `${i + 1} / ${fotos.length}` : "";
      if (typeof aoMudar === "function") aoMudar(i);
    }

    function irPara(i, suave = true) {
      const total = fotos.length;
      if (!total) return;
      const novo = (i + total) % total;            // setas dão a volta (última → primeira)
      trilho.scrollTo({ left: novo * trilho.clientWidth, behavior: suave ? movimento() : "auto" });
      marcar(novo);
    }

    /* ---------- 3. EVENTOS ---------- */
    btnAnt.addEventListener("click", () => irPara(atual - 1));
    btnProx.addEventListener("click", () => irPara(atual + 1));

    trilho.addEventListener("keydown", (e) => {
      const mapa = { ArrowLeft: atual - 1, ArrowRight: atual + 1, Home: 0, End: fotos.length - 1 };
      if (e.key in mapa) { e.preventDefault(); e.stopPropagation(); irPara(mapa[e.key]); }
    });

    // Deslize nativo (dedo/trackpad): descobre a foto pela posição
    let espera;
    trilho.addEventListener("scroll", () => {
      clearTimeout(espera);
      espera = setTimeout(() => {
        const i = Math.round(trilho.scrollLeft / Math.max(1, trilho.clientWidth));
        if (i !== atual && i < fotos.length) marcar(i);
      }, 80);
    }, { passive: true });

    // Mouse: arrastar para os lados
    let arrasto = null, acabouDeArrastar = false;
    trilho.addEventListener("pointerdown", (e) => {
      if (e.pointerType !== "mouse" || e.button !== 0 || fotos.length < 2) return;
      arrasto = { x: e.clientX, inicio: trilho.scrollLeft, base: atual, moveu: false };
      trilho.setPointerCapture(e.pointerId);
    });
    trilho.addEventListener("pointermove", (e) => {
      if (!arrasto) return;
      const dx = e.clientX - arrasto.x;
      if (Math.abs(dx) > 5) {
        arrasto.moveu = true;
        trilho.classList.add("arrastando");        // desliga o encaixe durante o arrasto
        trilho.scrollLeft = arrasto.inicio - dx;
      }
    });
    const soltar = (e) => {
      if (!arrasto) return;
      const dx = e.clientX - arrasto.x, { moveu, base } = arrasto;
      arrasto = null;
      trilho.classList.remove("arrastando");
      if (!moveu) return;
      acabouDeArrastar = true;
      setTimeout(() => { acabouDeArrastar = false; }, 0);
      const limite = trilho.clientWidth * 0.15;   // arrastar 15% troca de foto
      let novo = base;
      if (dx < -limite) novo = Math.min(fotos.length - 1, base + 1);
      if (dx > limite) novo = Math.max(0, base - 1);
      irPara(novo);
    };
    trilho.addEventListener("pointerup", soltar);
    trilho.addEventListener("pointercancel", soltar);
    // Evita que o fim de um arrasto conte como clique
    raiz.addEventListener("click", (e) => { if (acabouDeArrastar) { e.preventDefault(); e.stopPropagation(); } }, true);

    // Mantém a foto atual alinhada se o tamanho mudar
    if ("ResizeObserver" in window) {
      new ResizeObserver(() => { trilho.scrollLeft = atual * trilho.clientWidth; }).observe(trilho);
    }

    renderizar();

    return {
      raiz,
      get indice() { return atual; },
      irPara,
      atualizar(novas, indice) {
        fotos = Array.isArray(novas) ? novas.slice() : [];
        if (typeof indice === "number") atual = Math.max(0, indice);
        renderizar();
      }
    };
  }

  /* ---------- 4. IMAGEM PROVISÓRIA (SVG) — SOMENTE para dados de demonstração ----------
     Na versão final as fotos virão do servidor (armazenamento de fotos). */
  function imagemDemo(texto, cor = "#800000") {
    const t = String(texto).replace(/[<>&"]/g, "");
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500">
      <rect width="800" height="500" fill="#EADFD6"/>
      <rect x="0" y="330" width="800" height="170" fill="${cor}" opacity=".18"/>
      <path d="M90 330 260 170 400 300 520 210 710 330Z" fill="${cor}" opacity=".55"/>
      <circle cx="640" cy="120" r="46" fill="${cor}" opacity=".35"/>
      <text x="400" y="430" font-family="Segoe UI, Arial, sans-serif" font-size="34" font-weight="600" text-anchor="middle" fill="#1F1A17">${t}</text>
    </svg>`;
    return "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
  }

  window.SDCarrossel = { criar, imagemDemo };
})();
