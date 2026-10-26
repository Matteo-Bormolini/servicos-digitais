/* =====================================================================
   S.D — RODAPÉ (rodape/rodape.js)
   Monta o rodapé a partir de configuracoes/config.js (window.SD).
   Precisa de: <footer id="sd-rodape"></footer> na página.
   ===================================================================== */
(function () {
  "use strict";

  if (!window.SD) {
    console.error("[S.D] rodape.js: carregue configuracoes/config.js antes deste arquivo.");
    return;
  }
  const SD = window.SD;
  const I = SD.icones;
  const C = SD.config;

  // Coluna "Baixe o app" (não aparece dentro do app)
  function htmlLojas() {
    if (SD.ehApp()) return "";
    const lojas = C.lojas.map((l) => l.href
      ? `<a class="loja" href="${SD.esc(l.href)}" target="_blank" rel="noopener noreferrer">${I.celular}<span>${SD.esc(l.nome)}</span></a>`
      : `<a class="loja" role="link" aria-disabled="true" aria-label="${SD.esc(l.nome)} — em breve">${I.celular}<span><small>Em breve</small>${SD.esc(l.nome)}</span></a>`
    ).join("");
    return `<div><h2>Baixe o app</h2><div class="lojas">${lojas}</div></div>`;
  }

  function montar() {
    const alvo = document.getElementById("sd-rodape");
    if (!alvo) return;
    alvo.classList.add("rodape");

    const itens = C.rodapeLinks.map((id) => C.menu.find((m) => m.id === id)).filter(Boolean).filter(SD.itemVisivel);

    alvo.innerHTML = `
      <div class="rodape-conteudo">
        <div class="rodape-colunas">
          <div class="rodape-marca">
            <a class="marca" href="${SD.esc(SD.urlPagina("inicio"))}" aria-label="${SD.esc(C.nome)} — página inicial">${I.logo}<span class="marca-texto" aria-hidden="true">Serviços<br>Digitais</span></a>
            <p>${SD.esc(C.descricao)}</p>
          </div>
          <nav aria-label="Navegação do rodapé">
            <h2>Navegação</h2>
            <ul>${itens.map((i) => `<li>${SD.linkMenu(i, false)}</li>`).join("")}</ul>
          </nav>
          <div>
            <h2>Políticas</h2>
            <ul>${C.rodapePoliticas.map((p) => `<li><a href="${SD.esc(SD.caminho(p.href))}">${SD.esc(p.texto)}</a></li>`).join("")}</ul>
          </div>
          ${htmlLojas()}
        </div>
        <p class="rodape-aviso"><strong>Suporte</strong> é exclusivo para erros e melhorias da plataforma. Não é canal de reclamação sobre prestadores ou clientes.</p>
        <div class="rodape-base">
          <span>© ${new Date().getFullYear()} ${SD.esc(C.nome)}</span>
          <span><a href="${SD.esc(SD.urlPagina("termos"))}">Termos</a> · <a href="${SD.esc(SD.urlPagina("privacidade"))}">Privacidade</a></span>
        </div>
      </div>`;
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", montar);
  else montar();
})();
