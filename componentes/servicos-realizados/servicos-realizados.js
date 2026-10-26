/* =====================================================================
   S.D — SERVIÇOS REALIZADOS (componentes/servicos-realizados/servicos-realizados.js)
   Lista do histórico de serviços usada nos perfis de Cliente CPF e CNPJ.
   Cada item: data pequena no canto superior direito, foto circular da
   empresa e tabela de cantos arredondados (Serviço, [Local], Prestador,
   Valor, Sua Avaliação). Ao clicar, o item se expande e mostra o
   carrossel com as fotos do serviço (para o cliente se recordar).
   Depende de: componentes/utilidades, componentes/carrossel e
   componentes/servicos-realizados/servicos-realizados.css.

   Uso:
     SDServicos.renderizar({
       lista: elemento <ol>, total: elemento do contador, vazio: elemento do aviso,
       servicos: [...], fotoPadraoEmpresa: "../fotos/padrao/prestador.png"
     });
   Formato de cada serviço:
     { data: "AAAA-MM-DD", servico, prestador, valor (número em R$),
       estrelas (1 a 5 ou null), foto (da empresa ou null),
       local (opcional — usado no CNPJ), fotos: [{ src, legenda }] }
   ===================================================================== */
(function () {
  "use strict";
  const U = window.SDUtil;
  if (!U) { console.error("[S.D] servicos-realizados.js: carregue componentes/utilidades/utilidades.js antes."); return; }

  const SETA = '<svg class="servico-seta" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>';
  let contadorItens = 0;

  /* ---------- 1. UM ITEM DA LISTA ---------- */
  function criarItem(s, fotoPadraoEmpresa) {
    const idFotos = "servico-fotos-" + (++contadorItens);
    const fotos = Array.isArray(s.fotos) ? s.fotos : [];

    const li = document.createElement("li");
    const item = document.createElement("article");
    item.className = "servico-item";
    item.setAttribute("aria-label", `${s.servico}, ${U.formatarData(s.data)}`);

    // Data bem pequena no canto superior direito
    const data = document.createElement("time");
    data.className = "servico-data";
    data.dateTime = s.data;
    data.textContent = U.formatarData(s.data);

    // Foto circular da empresa/prestador (sem foto → padrão do sistema → ícone)
    const moldura = document.createElement("div");
    moldura.className = "servico-foto";
    const img = document.createElement("img");
    img.alt = "Foto de " + s.prestador;
    img.width = 72; img.height = 72; img.loading = "lazy";
    U.aplicarFoto(img, s.foto, fotoPadraoEmpresa, "prestador");
    moldura.append(img);

    // "Sua Avaliação" = nota que o cliente deu ao prestador
    const avaliacao = document.createElement("span");
    if (s.estrelas == null) {
      avaliacao.className = "sem-avaliacao";
      avaliacao.textContent = "Ainda não avaliado";
    } else {
      avaliacao.className = "estrelas";
      avaliacao.innerHTML = U.estrelasSVG(s.estrelas);
      const txt = document.createElement("span");
      txt.className = "estrelas-texto";
      txt.textContent = `${s.estrelas} de 5`;
      avaliacao.append(txt);
    }

    const valor = document.createElement("span");
    valor.className = "valor-dinheiro";
    valor.textContent = U.formatarMoeda(s.valor);

    const tabela = document.createElement("table");
    tabela.className = "tabela-servico";
    const corpo = document.createElement("tbody");
    corpo.append(U.linhaTabela("Serviço", s.servico));
    if (s.local) corpo.append(U.linhaTabela("Local", s.local));   // CNPJ: área do condomínio/empresa
    corpo.append(
      U.linhaTabela("Prestador", s.prestador),
      U.linhaTabela("Valor", valor),
      U.linhaTabela("Sua Avaliação", avaliacao)
    );
    tabela.append(corpo);

    // Botão de expandir (o clique em qualquer parte do item também expande)
    const botao = document.createElement("button");
    botao.type = "button";
    botao.className = "servico-expandir";
    botao.setAttribute("aria-expanded", "false");
    botao.setAttribute("aria-controls", idFotos);
    const textoBotao = (aberto) => fotos.length
      ? `${aberto ? "Ocultar" : "Ver"} fotos do serviço (${fotos.length})`
      : `${aberto ? "Ocultar" : "Ver"} fotos do serviço`;
    botao.innerHTML = `<span></span>${SETA}`;
    botao.firstChild.textContent = textoBotao(false);

    // Área expandida com o carrossel (criado só na primeira abertura)
    const area = document.createElement("div");
    area.className = "servico-fotos";
    area.id = idFotos;
    area.hidden = true;
    let carrossel = null;

    function alternar() {
      const abrir = area.hidden;
      area.hidden = !abrir;
      item.classList.toggle("expandido", abrir);
      botao.setAttribute("aria-expanded", String(abrir));
      botao.firstChild.textContent = textoBotao(abrir);
      if (abrir && !carrossel && window.SDCarrossel) {
        carrossel = window.SDCarrossel.criar({
          alvo: area,
          rotulo: "Fotos do serviço: " + s.servico,
          fotos: fotos.map((f, i) => ({ src: f.src, legenda: f.legenda, alt: f.legenda || `Foto ${i + 1} do serviço ${s.servico}` })),
          vazio: "Nenhuma foto foi registrada para este serviço."
        });
      }
    }

    botao.addEventListener("click", (e) => { e.stopPropagation(); alternar(); });

    // Clique no item (fora do carrossel). Ignora arrastos e seleção de texto.
    let inicio = null;
    item.addEventListener("pointerdown", (e) => { inicio = { x: e.clientX, y: e.clientY }; });
    item.addEventListener("click", (e) => {
      if (e.target.closest(".servico-fotos, a, button, input, select, textarea")) return;
      if (inicio && Math.hypot(e.clientX - inicio.x, e.clientY - inicio.y) > 8) return;
      if (String(window.getSelection && window.getSelection()).length) return;
      alternar();
    });

    item.append(data, moldura, tabela, botao, area);
    li.append(item);
    return li;
  }

  /* ---------- 2. LISTA COMPLETA ---------- */
  function renderizar({ lista, total, vazio, servicos, fotoPadraoEmpresa }) {
    lista.innerHTML = "";
    // Mais recente primeiro
    const ordenados = [...servicos].sort((a, b) => b.data.localeCompare(a.data));
    ordenados.forEach((s) => lista.append(criarItem(s, fotoPadraoEmpresa)));

    const n = servicos.length;
    if (total) total.textContent = n ? `${n} ${n === 1 ? "serviço" : "serviços"}` : "";
    if (vazio) vazio.hidden = n > 0;
    lista.hidden = n === 0;
  }

  window.SDServicos = { renderizar };
})();
