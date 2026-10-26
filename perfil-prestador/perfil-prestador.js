/* =====================================================================
   S.D — PERFIL DO PRESTADOR DE SERVIÇOS (perfil-prestador/perfil-prestador.js)
   O comportamento comum (abas, telefones, edição, exclusão) vem de
   componentes/perfil-base/perfil-base.js. Aqui fica só o exclusivo do Prestador:
     - Dados da empresa + área de atuação, especialidades, responsável
       técnico, registros/certificações, região e horário de atendimento.
     - Vitrine pública (estilo LinkedIn): nome, especialidades e números.
     - LOGO OBRIGATÓRIA: sem logo, usa a foto padrão e mostra alerta urgente.
     - "Trabalhos e empresa": carrossel OPCIONAL de fotos com legenda.
     - Avaliações recentes (públicas).
     - "Ver como cliente": mostra o perfil como o cliente vê (sem dados privados).
     - Aba "Meus serviços": quadro Kanban (componentes/kanban-servicos).
   IMPORTANTE: demonstração — salvar, excluir, enviar fotos e buscar os
   serviços dependem do servidor.
   ===================================================================== */
(function () {
  "use strict";
  const U = window.SDUtil, P = window.SDPerfil, SD = window.SD;
  const $ = P.$;

  /* ---------- 1. CONFIGURAÇÃO (fácil de ajustar) ---------- */
  const CONFIG = {
    ...P.PADRAO,                                 // telefones (4), fotos (JPG/PNG/WEBP até 5 MB)
    maxFotosTrabalho: 12,
    maxEspecialidades: 8,
    tamanhoMinLogoPx: 200,                       // logo menor que isso fica borrada
    urlAvaliacoes: SD.urlPagina("avaliacoes"),
    // Fotos padrão do sistema (arquivos ainda a criar). Sem o arquivo, aparece um ícone provisório.
    fotoPadraoPrestador: SD.caminho("fotos/padrao/prestador.png"),
    fotoPadraoCliente: { cpf: SD.caminho("fotos/padrao/cliente-cpf.png"), cnpj: SD.caminho("fotos/padrao/cliente-cnpj.png") }
  };

  // Área de atuação principal (foco atual: manutenção + fornecimento de itens)
  const AREAS_ATUACAO = [
    "Manutenção predial (geral)", "Elétrica", "Hidráulica", "Pintura e revestimentos",
    "Telhados, calhas e impermeabilização", "Ar-condicionado e refrigeração",
    "Portões, interfones e CFTV", "Elevadores", "Sistemas de incêndio",
    "Caixa d'água, bombas e reservatórios", "Jardinagem e paisagismo",
    "Fornecimento de equipamentos e materiais", "Outra"
  ];
  // Distância máxima de atendimento (km) — usada na busca por proximidade
  const RAIOS_KM = [5, 10, 15, 20, 30, 50, 100];

  /* ---------- 2. DADOS DE DEMONSTRAÇÃO ----------
     Substituir pelos dados vindos do servidor depois do login. */
  const demo = (texto) => window.SDCarrossel.imagemDemo(texto);

  const perfil = {
    login: "prestador.exemplo",
    razaoSocial: "Empresa Exemplo Manutenções Ltda.",
    nomeFantasia: "Exemplo Manutenções",
    tipoConta: "Prestador de serviços - Pessoa jurídica (CNPJ)",
    documento: "00.000.000/0001-00",
    areaAtuacao: "Manutenção predial (geral)",
    especialidades: ["Elétrica predial", "Hidráulica", "Impermeabilização", "Bombas de recalque", "Pintura"],
    responsavelNome: "Nome Sobrenome Exemplo",
    responsavelCargo: "Técnico responsável",
    certificacoes: ["NR-10", "NR-35"],
    anoInicio: "2015",
    membroDesde: "2026",
    email: "contato@exemplo.com.br",
    telefones: [{ numero: "11920000000", principal: true }],
    raioKm: 15,
    bairrosAtendidos: "",
    emergencia: true,
    horario: "Segunda a sábado, 07:00 às 18:00",
    endereco: "Rua Exemplo",
    numero: "250",
    complemento: "Galpão 2",
    bairro: "Centro",
    cep: "01000000",
    sobre: "Empresa especializada em manutenção predial para condomínios e empresas. Equipe própria, uniformizada e com treinamentos de segurança. Garantia de 90 dias em todos os serviços.",
    avaliacao: { media: 4.7, total: 38 },
    servicosAnteriores: 52,                        // concluídos antes do quadro atual (histórico do servidor)
    foto: null,                                    // null = SEM LOGO → foto padrão + alerta
    fotosTrabalho: [
      { src: demo("Impermeabilização — depois"), legenda: "Impermeabilização de laje — depois" },
      { src: demo("Quadro elétrico novo"), legenda: "Troca de quadro elétrico" },
      { src: demo("Equipe e veículo"), legenda: "Nossa equipe" }
    ]
  };

  // Avaliações recentes (públicas). Cliente identificado só pelo tipo (privacidade).
  const avaliacoes = [
    { data: "2026-10-12", nota: 5, cliente: "Cliente CNPJ · Condomínio residencial", texto: "Serviço rápido, equipe educada e deixou tudo limpo." },
    { data: "2026-09-28", nota: 4, cliente: "Cliente CPF · Casa", texto: "Resolveu o vazamento. Chegou um pouco depois do combinado." },
    { data: "2026-09-05", nota: 5, cliente: "Cliente CNPJ · Empresa / escritório", texto: "Orçamento claro e cumpriu o prazo." }
  ];

  // Serviços do quadro (Kanban). telefone = só aparece depois do aceite.
  const servicosKanban = [
    { id: "s1", etapa: "orcando", servico: "Reparo de infiltração no teto", cliente: "Condomínio Exemplo A", tipoCliente: "cnpj", fotoCliente: null,
      bairro: "Vila Exemplo", local: "Hall, corredores e escadas", visita: "Precisa de visita — falar com o zelador",
      dataPedido: "2026-10-20", valor: 1800, telefone: "11930000001",
      descricao: "Mancha de umidade no teto do hall do 3º andar, aumenta quando chove.",
      fotos: [{ src: demo("Mancha no teto"), legenda: "Foto enviada pelo cliente" }] },
    { id: "s2", etapa: "orcando", servico: "Instalação de chuveiro elétrico", cliente: "Cliente Exemplo B", tipoCliente: "cpf", fotoCliente: null,
      bairro: "Jardim Exemplo", local: "Banheiro", visita: "Não precisa de visita prévia",
      dataPedido: "2026-10-19", valor: 220, telefone: "11930000002",
      descricao: "Trocar chuveiro antigo por um novo (o cliente já comprou).", fotos: [] },
    { id: "s3", etapa: "aceito", servico: "Limpeza de caixa d'água (2 reservatórios)", cliente: "Condomínio Exemplo C", tipoCliente: "cnpj", fotoCliente: null,
      bairro: "Centro", local: "Caixa d'água, reservatórios e bombas", visita: "Dia útil, das 08:00 às 17:00",
      dataPedido: "2026-10-14", dataAgendada: "2026-10-28", valor: 950, telefone: "11930000003",
      descricao: "Limpeza semestral com laudo. Acesso pela cobertura.",
      fotos: [{ src: demo("Reservatório superior"), legenda: "Reservatório superior" }] },
    { id: "s4", etapa: "realizar", servico: "Troca do quadro de disjuntores", cliente: "Empresa Exemplo D", tipoCliente: "cnpj", fotoCliente: null,
      bairro: "Bairro Exemplo", local: "Quadros elétricos, medidores e gerador", visita: "Agendado com a recepção",
      dataPedido: "2026-10-02", dataAgendada: "2026-10-24", valor: 3200, telefone: "11930000004",
      descricao: "Quadro antigo aquecendo. Trocar por quadro novo com DR.",
      fotos: [{ src: demo("Quadro antigo"), legenda: "Antes" }, { src: demo("Material separado"), legenda: "Material separado" }] },
    { id: "s5", etapa: "realizar", servico: "Pintura da fachada (bloco B)", cliente: "Condomínio Exemplo A", tipoCliente: "cnpj", fotoCliente: null,
      bairro: "Vila Exemplo", local: "Fachada e área externa", visita: "Início combinado com o síndico",
      dataPedido: "2026-09-20", dataAgendada: "2026-11-03", valor: 14500, telefone: "11930000001",
      descricao: "Pintura completa com tinta acrílica, incluindo andaime.", fotos: [] },
    { id: "s6", etapa: "prestado", servico: "Manutenção das bombas de recalque", cliente: "Condomínio Exemplo C", tipoCliente: "cnpj", fotoCliente: null,
      bairro: "Centro", local: "Caixa d'água, reservatórios e bombas", visita: "Realizada",
      dataPedido: "2026-09-25", dataAgendada: "2026-10-08", dataConclusao: "2026-10-10", valor: 1450, telefone: "11930000003",
      avaliacaoRecebida: 5, descricao: "Manutenção preventiva e troca de selos.",
      fotos: [{ src: demo("Bombas — antes"), legenda: "Antes" }, { src: demo("Bombas — depois"), legenda: "Depois" }] },
    { id: "s7", etapa: "prestado", servico: "Conserto de vazamento na cozinha", cliente: "Cliente Exemplo E", tipoCliente: "cpf", fotoCliente: null,
      bairro: "Jardim Exemplo", local: "Cozinha", visita: "Realizada",
      dataPedido: "2026-09-22", dataAgendada: "2026-09-27", dataConclusao: "2026-09-27", valor: 180, telefone: "11930000005",
      avaliacaoRecebida: null, descricao: "Vazamento no sifão da pia.", fotos: [{ src: demo("Sifão trocado"), legenda: "Sifão trocado" }] }
  ];

  let quadro = null, telefones = null, abas = null;

  /* ---------- 3. EXIBIÇÃO DOS DADOS ---------- */
  function textoRegiao() {
    let t = `Até ${perfil.raioKm} km a partir de ${perfil.bairro || "endereço da empresa"}`;
    if (perfil.bairrosAtendidos) t += ` · ${perfil.bairrosAtendidos}`;
    return t;
  }
  const textoHorario = () => (perfil.horario || "—") + (perfil.emergencia ? " · Atende emergências" : "");

  // Etiquetas (especialidades / certificações)
  function renderizarChips(ul, itens, vazio) {
    ul.innerHTML = "";
    if (!itens.length) {
      const li = document.createElement("li"); li.className = "chip-vazio"; li.textContent = vazio; ul.append(li); return;
    }
    itens.forEach((t) => { const li = document.createElement("li"); li.textContent = t; ul.append(li); });
  }

  function renderizarDados() {
    P.preencherCampos({
      nomeExibicao: perfil.nomeFantasia || perfil.razaoSocial,
      login: perfil.login,
      razaoSocial: perfil.razaoSocial,
      nomeFantasia: P.ouTraco(perfil.nomeFantasia),
      tipoConta: perfil.tipoConta,
      documento: perfil.documento,
      areaAtuacao: P.ouTraco(perfil.areaAtuacao),
      regiaoResumo: `Atende até ${perfil.raioKm} km de ${perfil.bairro || "sua base"}`,
      responsavel: perfil.responsavelCargo ? `${perfil.responsavelNome} — ${perfil.responsavelCargo}` : perfil.responsavelNome,
      email: perfil.email,
      regiao: textoRegiao(),
      horario: textoHorario(),
      sobre: perfil.sobre || "A empresa ainda não escreveu uma apresentação.",
      endereco: P.ouTraco(perfil.endereco),
      numero: P.ouTraco(perfil.numero),
      complemento: P.ouTraco(perfil.complemento),
      bairro: P.ouTraco(perfil.bairro),
      cep: perfil.cep ? U.formatarCep(perfil.cep) : "—"
    });

    renderizarChips($("#vitrine-especialidades"), perfil.especialidades, "Nenhuma especialidade informada");
    renderizarChips($("#lista-especialidades"), perfil.especialidades, "Nenhuma especialidade informada");
    renderizarChips($("#lista-certificacoes"), perfil.certificacoes, "Nenhum registro informado");
    P.preencherLinkAvaliacoes($("#link-avaliacoes"), perfil.avaliacao, CONFIG.urlAvaliacoes);
    $("#link-todas-avaliacoes").href = CONFIG.urlAvaliacoes;
    renderizarNumeros();

    // Contato rápido (visão do cliente) — WhatsApp e ligação
    const principal = perfil.telefones.find((t) => t.principal);
    const tel = U.soDigitos(principal && principal.numero);
    $("#btn-whatsapp").href = "https://wa.me/55" + tel;
    $("#btn-ligar").href = "tel:+55" + tel;

    P.preencherPlaceholders({
      "f-login": perfil.login, "f-razao": perfil.razaoSocial, "f-fantasia": perfil.nomeFantasia,
      "f-sobre": perfil.sobre, "f-especialidades": perfil.especialidades.join(", "), "f-certificacoes": perfil.certificacoes.join(", "),
      "f-resp-nome": perfil.responsavelNome, "f-resp-cargo": perfil.responsavelCargo, "f-inicio": perfil.anoInicio,
      "f-email": perfil.email, "f-telefone": U.formatarTelefone(principal && principal.numero),
      "f-horario": perfil.horario, "f-bairros": perfil.bairrosAtendidos,
      "f-endereco": perfil.endereco, "f-numero": perfil.numero, "f-complemento": perfil.complemento,
      "f-bairro": perfil.bairro, "f-cep": U.formatarCep(perfil.cep),
      "f-senha": "Deixe vazio para manter a atual", "f-senha2": "Repita a nova senha"
    });
    P.preencherSelect($("#f-area"), perfil.areaAtuacao || "não informada", AREAS_ATUACAO);
    P.preencherSelect($("#f-raio"), `${perfil.raioKm} km`, RAIOS_KM.map((r) => ({ texto: `${r} km`, valor: String(r) })));
    $("#f-emergencia").checked = !!perfil.emergencia;

    if (telefones) telefones.renderizar();
    renderizarFoto();
  }

  // Números da vitrine (somente números, sem gráficos)
  function renderizarNumeros() {
    const concluidos = perfil.servicosAnteriores + (quadro ? quadro.contar("prestado") : 0);
    const anos = new Date().getFullYear() - Number(perfil.anoInicio);
    $("#num-concluidos").textContent = concluidos.toLocaleString("pt-BR");
    $("#num-avaliacao").textContent = `${U.decimal(perfil.avaliacao.media)} / 5`;
    $("#num-experiencia").textContent = anos > 0 ? `${anos} ${anos === 1 ? "ano" : "anos"}` : "Menos de 1 ano";
    $("#num-desde").textContent = perfil.membroDesde;
  }

  /* ---------- 4. LOGO (foto de perfil OBRIGATÓRIA) ---------- */
  function renderizarFoto() {
    const img = $("#foto-perfil"), semLogo = !perfil.foto;
    U.aplicarFoto(img, perfil.foto, CONFIG.fotoPadraoPrestador, "prestador");
    img.alt = semLogo ? "Foto padrão: a empresa ainda não adicionou a logo" : "Logo de " + (perfil.nomeFantasia || perfil.razaoSocial);
    $("#foto-moldura").classList.toggle("sem-logo", semLogo);
    $("#selo-sem-logo").hidden = !semLogo;
    $("#alerta-logo").hidden = !semLogo;
    $("#btn-foto").textContent = semLogo ? "Adicionar logo" : "Trocar logo";
    P.atualizarAltura();
  }

  // Lê largura/altura da imagem para recusar logos muito pequenas
  function medirImagem(url) {
    return new Promise((ok) => {
      const i = new Image();
      i.onload = () => ok({ largura: i.naturalWidth, altura: i.naturalHeight });
      i.onerror = () => ok(null);
      i.src = url;
    });
  }

  function iniciarLogo() {
    const msg = $("#msg-foto");
    const escolher = () => $("#input-foto").click();
    $("#btn-foto").addEventListener("click", escolher);
    $("#btn-alerta-logo").addEventListener("click", () => {
      if (abas && abas.ativo !== 0) abas.ativar(0, true);
      $("#btn-foto").scrollIntoView({ block: "center", behavior: "smooth" });
      escolher();
    });

    $("#input-foto").addEventListener("change", async (e) => {
      const arq = e.target.files[0];
      e.target.value = "";
      if (!arq) return;
      const erro = P.validarArquivo(arq, CONFIG);
      if (erro) { U.mostrarMensagem(msg, "erro", erro); return; }
      const url = URL.createObjectURL(arq);
      const medida = await medirImagem(url);
      if (!medida) { URL.revokeObjectURL(url); U.mostrarMensagem(msg, "erro", `"${arq.name}": não foi possível ler a imagem.`); return; }
      if (medida.largura < CONFIG.tamanhoMinLogoPx || medida.altura < CONFIG.tamanhoMinLogoPx) {
        URL.revokeObjectURL(url);
        U.mostrarMensagem(msg, "erro", `Imagem muito pequena (${medida.largura} × ${medida.altura} px). Use no mínimo ${CONFIG.tamanhoMinLogoPx} × ${CONFIG.tamanhoMinLogoPx} px.`);
        return;
      }
      if (perfil.foto) URL.revokeObjectURL(perfil.foto);
      perfil.foto = url;
      renderizarFoto();
      const quadrada = Math.abs(medida.largura - medida.altura) / Math.max(medida.largura, medida.altura) < 0.1;
      U.mostrarMensagem(msg, "atencao", "Logo atualizada na pré-visualização (ainda não enviada ao servidor)." +
        (quadrada ? "" : " Dica: a imagem não é quadrada; as bordas podem ser cortadas no círculo."));
    });
  }

  /* ---------- 5. FOTOS DE TRABALHOS (carrossel opcional) ---------- */
  let carrosselTrabalho = null;

  const fotosParaCarrossel = () => perfil.fotosTrabalho.map((f, i) => ({
    src: f.src,
    legenda: f.legenda || "",
    alt: f.legenda ? `Foto ${i + 1}: ${f.legenda}` : `Foto ${i + 1} de trabalhos da empresa`
  }));

  function sincronizarControles(indice) {
    const total = perfil.fotosTrabalho.length;
    $("#controles-foto-atual").hidden = total === 0;
    $("#fotos-trabalho-total").textContent = `${total} de ${CONFIG.maxFotosTrabalho} fotos`;
    const cheio = total >= CONFIG.maxFotosTrabalho;
    const add = $("#btn-add-fotos-trabalho");
    add.disabled = cheio;
    add.title = cheio ? `Limite de ${CONFIG.maxFotosTrabalho} fotos` : "";
    // Na visão do cliente, sem fotos o bloco inteiro some
    $(".fotos-trabalho").classList.toggle("so-dono", total === 0);
    if (!total) return;
    const i = Math.min(indice, total - 1);
    const input = $("#legenda-foto");
    if (document.activeElement !== input) input.value = perfil.fotosTrabalho[i].legenda || "";
    $("#legenda-foto-posicao").textContent = `(foto ${i + 1} de ${total})`;
  }

  function redesenharFotos(indice) {
    carrosselTrabalho.atualizar(fotosParaCarrossel(), indice);
    sincronizarControles(carrosselTrabalho.indice);
    P.atualizarAltura();
  }

  function iniciarFotosTrabalho() {
    const msg = $("#msg-fotos-trabalho");
    $("#max-fotos-trabalho").textContent = CONFIG.maxFotosTrabalho;

    carrosselTrabalho = window.SDCarrossel.criar({
      alvo: $("#carrossel-trabalho"),
      rotulo: "Fotos de trabalhos e da empresa",
      fotos: fotosParaCarrossel(),
      vazio: "Nenhuma foto adicionada. É opcional — use o botão \"Adicionar fotos\".",
      aoMudar: (i) => sincronizarControles(i)
    });
    sincronizarControles(0);

    // Legenda da foto atual (aplica ao sair do campo ou com Enter)
    const legenda = $("#legenda-foto");
    const aplicarLegenda = () => {
      const i = carrosselTrabalho.indice;
      if (!perfil.fotosTrabalho[i]) return;
      const nova = legenda.value.trim();
      if (nova === (perfil.fotosTrabalho[i].legenda || "")) return;
      perfil.fotosTrabalho[i].legenda = nova;
      redesenharFotos(i);
    };
    legenda.addEventListener("change", aplicarLegenda);
    legenda.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); aplicarLegenda(); } });

    $("#btn-remover-foto-trabalho").addEventListener("click", () => {
      const i = carrosselTrabalho.indice;
      const [removida] = perfil.fotosTrabalho.splice(i, 1);
      if (removida && removida.src.startsWith("blob:")) URL.revokeObjectURL(removida.src);
      legenda.value = "";
      redesenharFotos(Math.max(0, Math.min(i, perfil.fotosTrabalho.length - 1)));
      U.mostrarMensagem(msg, "atencao", "Foto removida nesta tela (ainda não salvo no servidor).");
      if (!perfil.fotosTrabalho.length) $("#btn-add-fotos-trabalho").focus();
    });

    $("#btn-add-fotos-trabalho").addEventListener("click", () => $("#input-fotos-trabalho").click());
    $("#input-fotos-trabalho").addEventListener("change", (e) => {
      const arquivos = [...e.target.files];
      e.target.value = "";
      if (!arquivos.length) return;
      const erros = [], primeiraNova = perfil.fotosTrabalho.length;
      let adicionadas = 0;
      arquivos.forEach((arq) => {
        if (perfil.fotosTrabalho.length >= CONFIG.maxFotosTrabalho) { erros.push(`"${arq.name}": limite de ${CONFIG.maxFotosTrabalho} fotos atingido.`); return; }
        const erro = P.validarArquivo(arq, CONFIG);
        if (erro) { erros.push(erro); return; }
        perfil.fotosTrabalho.push({ src: URL.createObjectURL(arq), legenda: "" });
        adicionadas++;
      });
      if (adicionadas) {
        legenda.value = "";
        redesenharFotos(primeiraNova);
        const texto = `${adicionadas} ${adicionadas === 1 ? "foto adicionada" : "fotos adicionadas"} (pré-visualização, ainda não enviadas ao servidor). Escreva uma legenda para cada foto.`;
        U.mostrarMensagem(msg, "atencao", erros.length ? `${texto} Não adicionadas: ${erros.join(" ")}` : texto);
        legenda.focus();
      } else {
        U.mostrarMensagem(msg, "erro", erros.join(" "));
      }
    });
  }

  /* ---------- 6. AVALIAÇÕES RECENTES (as 3 mais novas) ---------- */
  function renderizarAvaliacoes() {
    const lista = $("#lista-avaliacoes");
    lista.innerHTML = "";
    [...avaliacoes].sort((a, b) => b.data.localeCompare(a.data)).slice(0, 3).forEach((a) => {
      const li = document.createElement("li");
      li.className = "avaliacao-item";
      const topo = document.createElement("div");
      topo.className = "avaliacao-topo";
      const est = document.createElement("span");
      est.className = "estrelas";
      est.innerHTML = U.estrelasSVG(a.nota);
      const nota = document.createElement("span");
      nota.textContent = `${a.nota} de 5`;
      est.append(nota);
      const data = document.createElement("time");
      data.dateTime = a.data; data.textContent = U.formatarData(a.data);
      topo.append(est, data);
      const p = document.createElement("p"); p.textContent = a.texto;
      const autor = document.createElement("span"); autor.className = "avaliacao-autor"; autor.textContent = a.cliente;
      li.append(topo, p, autor);
      lista.append(li);
    });
    $("#avaliacoes-vazio").hidden = avaliacoes.length > 0;
  }

  /* ---------- 7. VISÃO: DONO x CLIENTE ----------
     Só muda a TELA. Na versão final o servidor envia ao cliente somente os
     dados públicos (nunca login, senha, endereço completo ou o quadro). */
  const visaoCliente = () => document.body.dataset.visao === "cliente";

  function definirVisao(visao, focar) {
    document.body.dataset.visao = visao;
    const cliente = visao === "cliente";
    $("#aviso-visao").hidden = !cliente;
    $("#titulo-pagina").textContent = cliente ? (perfil.nomeFantasia || perfil.razaoSocial) : "Perfil do prestador";
    // Fecha a edição ao trocar de visão (o texto digitado é mantido)
    if (cliente && !$("#sanfona-editar").hidden) P.abrirSanfona(false);
    abas.ativar(0, false);
    $("#perfil-trilho").scrollLeft = 0;
    const url = new URL(location.href);
    if (cliente) url.searchParams.set("visao", "cliente"); else url.searchParams.delete("visao");
    try { history.replaceState(null, "", url); } catch (_) { /* arquivo local ou sandbox: ignora */ }
    if (focar) (cliente ? $("#btn-voltar-edicao") : $("#btn-ver-como-cliente")).focus();
    P.atualizarAltura();
  }

  function iniciarVisao() {
    $("#btn-ver-como-cliente").addEventListener("click", () => definirVisao("cliente", true));
    $("#btn-voltar-edicao").addEventListener("click", () => definirVisao("dono", true));
    const pedida = new URLSearchParams(location.search).get("visao");
    definirVisao(pedida === "cliente" ? "cliente" : "dono", false);
  }

  /* ---------- 8. FORMULÁRIO: campos e regras exclusivas do Prestador ---------- */
  function iniciarFormulario() {
    $("#f-sobre").addEventListener("input", (e) => { $("#contador-sobre").textContent = e.target.value.length; P.atualizarAltura(); });
    P.iniciarFormulario({
      perfil,
      coletar: (valor) => ({
        razaoSocial: valor("f-razao"), nomeFantasia: valor("f-fantasia"),
        areaAtuacao: $("#f-area").value, sobre: valor("f-sobre"),
        especialidades: valor("f-especialidades"), certificacoes: valor("f-certificacoes"),
        responsavelNome: valor("f-resp-nome"), responsavelCargo: valor("f-resp-cargo"), anoInicio: valor("f-inicio"),
        horario: valor("f-horario"), raioKm: $("#f-raio").value, bairrosAtendidos: valor("f-bairros"),
        emergencia: $("#f-emergencia").checked
      }),
      camposTexto: ["razaoSocial", "nomeFantasia", "areaAtuacao", "sobre", "responsavelNome", "responsavelCargo",
        "anoInicio", "horario", "bairrosAtendidos"],
      validar: (d, marcar) => {
        const anoAtual = new Date().getFullYear();
        if (d.razaoSocial && d.razaoSocial.length < 3) marcar("f-razao", "Informe a razão social completa.");
        if (d.nomeFantasia && d.nomeFantasia.length < 2) marcar("f-fantasia", "Nome fantasia muito curto.");
        if (d.sobre && d.sobre.length < 30) marcar("f-sobre", "Escreva pelo menos 30 caracteres para apresentar a empresa.");
        if (d.especialidades && U.listaDeTexto(d.especialidades).length > CONFIG.maxEspecialidades) marcar("f-especialidades", `Informe no máximo ${CONFIG.maxEspecialidades} especialidades.`);
        if (d.responsavelNome && d.responsavelNome.split(/\s+/).length < 2) marcar("f-resp-nome", "Informe nome e sobrenome.");
        if (d.responsavelCargo && d.responsavelCargo.length < 2) marcar("f-resp-cargo", "Cargo muito curto.");
        if (d.anoInicio && (!/^\d{4}$/.test(d.anoInicio) || +d.anoInicio < 1900 || +d.anoInicio > anoAtual)) marcar("f-inicio", `Informe um ano entre 1900 e ${anoAtual}.`);
      },
      // Listas, número e caixa de seleção (não são texto simples)
      aplicarExtra: (d, alterados) => {
        ["especialidades", "certificacoes"].forEach((c) => {
          if (!d[c]) return;
          const nova = U.listaDeTexto(d[c]);
          if (nova.join("|") !== perfil[c].join("|")) { perfil[c] = nova; alterados.push(c); }
        });
        if (d.raioKm && Number(d.raioKm) !== perfil.raioKm) { perfil.raioKm = Number(d.raioKm); alterados.push("raioKm"); }
        if (d.emergencia !== !!perfil.emergencia) { perfil.emergencia = d.emergencia; alterados.push("emergencia"); }
      },
      aoConcluir: () => { $("#contador-sobre").textContent = "0"; renderizarDados(); }
    });
  }

  /* ---------- 9. INÍCIO ---------- */
  document.addEventListener("DOMContentLoaded", () => {
    quadro = window.SDKanban.criar({
      alvo: $("#kanban"), resumo: $("#kanban-resumo"), total: $("#servicos-total"), anuncio: $("#kanban-anuncio"),
      servicos: servicosKanban, fotoPadraoCliente: CONFIG.fotoPadraoCliente,
      aoMudar: () => { renderizarNumeros(); P.atualizarAltura(); }
    });
    telefones = P.iniciarTelefones(perfil, { max: CONFIG.maxTelefonesSecundarios, classeRemover: "so-dono" });
    renderizarDados();
    iniciarFotosTrabalho();
    renderizarAvaliacoes();
    P.iniciarSanfona();
    iniciarFormulario();
    iniciarLogo();
    P.iniciarExclusao();
    abas = P.iniciarAbas({
      abas: ["#aba-perfil", "#aba-servicos"],
      // Na visão do cliente só existe o painel Perfil
      navegaveis: () => (visaoCliente() ? [$("#aba-perfil")] : [$("#aba-perfil"), $("#aba-servicos")]),
      semArrasto: visaoCliente
    });
    iniciarVisao();
  });

  // Ganchos só para testes automatizados (não usados pela página)
  window.__SDPrestador = { perfil, get quadro() { return quadro; }, definirVisao };
})();
