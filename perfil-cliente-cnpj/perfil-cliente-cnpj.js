/* =====================================================================
   S.D — PERFIL DO CLIENTE CNPJ (perfil-cliente-cnpj/perfil-cliente-cnpj.js)
   O comportamento comum (abas, telefones, edição, foto, exclusão) vem de
   componentes/perfil-base/perfil-base.js. Aqui fica só o exclusivo do CNPJ:
     - Dados da empresa: razão social, nome fantasia, CNPJ (inalterável),
       tipo de estabelecimento, responsável pela conta, contato no local
       (zelador/portaria/recepção) e horário para visitas.
     - Foto de perfil (logo) opcional → foto padrão do sistema.
     - "Fotos do local": carrossel OPCIONAL; cada foto indica a área.
     - Aba "Serviços realizados" (componentes/servicos-realizados) com "Local".
   IMPORTANTE: demonstração — salvar, excluir, enviar fotos e buscar o
   histórico dependem do servidor.
   ===================================================================== */
(function () {
  "use strict";
  const U = window.SDUtil, P = window.SDPerfil, SD = window.SD;
  const $ = P.$;

  /* ---------- 1. CONFIGURAÇÃO (fácil de ajustar) ---------- */
  const CONFIG = {
    ...P.PADRAO,   // telefones (4), fotos (JPG/PNG/WEBP até 5 MB)
    maxFotosLocal: 12,
    // Fotos padrão do sistema (arquivos ainda a criar). Sem o arquivo, aparece um ícone provisório.
    fotoPadraoCliente: SD.caminho("fotos/padrao/cliente-cnpj.png"),
    fotoPadraoEmpresa: SD.caminho("fotos/padrao/prestador.png")
  };

  // Tipos de estabelecimento (lista do campo de seleção)
  const TIPOS_ESTABELECIMENTO = [
    "Condomínio residencial", "Condomínio comercial", "Condomínio misto",
    "Empresa / escritório", "Comércio / loja", "Indústria / galpão", "Outro"
  ];

  // Áreas mais comuns para manutenção em condomínios e empresas
  // (base: sistemas citados na ABNT NBR 5674 — manutenção de edificações).
  const AREAS = [
    { nome: "Fachada e área externa",                 exemplos: "pintura, revestimento, infiltrações, muros" },
    { nome: "Portaria, recepção e acessos",           exemplos: "portões de pedestres, interfone, controle de acesso" },
    { nome: "Hall, corredores e escadas",             exemplos: "iluminação, pisos, corrimãos, portas corta-fogo" },
    { nome: "Garagem e estacionamento",               exemplos: "portão automático, piso, demarcação, drenagem" },
    { nome: "Telhado, cobertura e calhas",            exemplos: "telhas, impermeabilização, rufos, calhas" },
    { nome: "Caixa d'água, reservatórios e bombas",   exemplos: "limpeza, boias, bombas de recalque, registros" },
    { nome: "Elevadores e casa de máquinas",          exemplos: "cabine, portas, casa de máquinas" },
    { nome: "Quadros elétricos, medidores e gerador", exemplos: "disjuntores, aterramento, gerador, SPDA (para-raios)" },
    { nome: "Sistema de incêndio",                    exemplos: "extintores, hidrantes, iluminação de emergência" },
    { nome: "Área de lazer",                          exemplos: "piscina, salão de festas, academia, churrasqueira, playground" },
    { nome: "Jardins e áreas verdes",                 exemplos: "irrigação, poda, paisagismo" },
    { nome: "Banheiros, vestiários e copa",           exemplos: "hidráulica, louças, revestimentos, exaustão" },
    { nome: "Salas, escritórios e lojas",             exemplos: "ar-condicionado, iluminação, divisórias, rede" },
    { nome: "Galpão, depósito e área técnica",        exemplos: "estrutura, piso industrial, docas, portas de enrolar" },
    { nome: "Outra área",                             exemplos: "" }
  ];

  /* ---------- 2. DADOS DE DEMONSTRAÇÃO ----------
     Substituir pelos dados vindos do servidor depois do login. */
  const demo = (texto) => window.SDCarrossel.imagemDemo(texto);

  const perfil = {
    login: "condominio.exemplo",
    razaoSocial: "Condomínio Edifício Exemplo",
    nomeFantasia: "Residencial Exemplo",
    tipoConta: "Cliente - Pessoa jurídica (CNPJ)",
    documento: "00.000.000/0001-00",
    tipoEstabelecimento: "Condomínio residencial",
    responsavelNome: "Nome Sobrenome Exemplo",
    responsavelCargo: "Síndico(a)",
    email: "administracao@exemplo.com.br",
    telefones: [{ numero: "1130000000", principal: true }],
    contatoNome: "Nome do Zelador",
    contatoFuncao: "Zelador(a)",
    contatoTelefone: "11911111111",
    horarioVisitas: "Segunda a sexta, 08:00 às 17:00",
    endereco: "Avenida Exemplo",
    numero: "500",
    complemento: "",
    bairro: "Centro",
    cep: "01000000",
    // Notas que os prestadores dão ao cliente NÃO aparecem aqui (só os prestadores as veem).
    foto: null,                              // null = usa a foto padrão
    // Fotos do local (opcional). area = uma das AREAS ("" = não informada)
    fotosLocal: [
      { src: demo("Fachada do prédio"), area: "Fachada e área externa" },
      { src: demo("Garagem — vista geral"), area: "Garagem e estacionamento" },
      { src: demo("Área de lazer — piscina"), area: "Área de lazer" }
    ]
  };

  // Histórico de serviços (exemplo). local = área onde o serviço foi feito (CNPJ);
  // fotos = fotos do serviço realizado (aparecem no carrossel ao expandir o item).
  const servicos = [
    { data: "2026-10-10", servico: "Manutenção preventiva das bombas de recalque", local: "Caixa d'água, reservatórios e bombas",
      prestador: "Empresa Exemplo A", valor: 1450.00, estrelas: 5, foto: null,
      fotos: [{ src: demo("Bombas — antes"), legenda: "Antes" }, { src: demo("Troca de selos"), legenda: "Durante o serviço" }, { src: demo("Bombas — depois"), legenda: "Depois" }] },
    { data: "2026-09-03", servico: "Troca do motor do portão da garagem", local: "Garagem e estacionamento",
      prestador: "Empresa Exemplo B", valor: 2380.00, estrelas: 4, foto: null,
      fotos: [{ src: demo("Motor antigo"), legenda: "Motor antigo" }, { src: demo("Motor novo instalado"), legenda: "Motor novo instalado" }] },
    { data: "2026-07-18", servico: "Recarga e inspeção dos extintores", local: "Sistema de incêndio",
      prestador: "Prestador Exemplo C", valor: 640.00, estrelas: null, foto: null,
      fotos: [] }
  ];

  let telefones = null, foto = null;

  /* ---------- 3. EXIBIÇÃO DOS DADOS ---------- */
  function textoContatoLocal() {
    const partes = [];
    if (perfil.contatoNome) partes.push(perfil.contatoFuncao ? `${perfil.contatoNome} (${perfil.contatoFuncao})` : perfil.contatoNome);
    if (perfil.contatoTelefone) partes.push(U.formatarTelefone(perfil.contatoTelefone));
    return partes.join(" · ") || "—";
  }

  function renderizarDados() {
    P.preencherCampos({
      login: perfil.login,
      razaoSocial: perfil.razaoSocial,
      nomeFantasia: P.ouTraco(perfil.nomeFantasia),
      tipoConta: perfil.tipoConta,
      documento: perfil.documento,
      tipoEstabelecimento: P.ouTraco(perfil.tipoEstabelecimento),
      responsavel: perfil.responsavelCargo ? `${perfil.responsavelNome} — ${perfil.responsavelCargo}` : perfil.responsavelNome,
      email: perfil.email,
      contatoLocal: textoContatoLocal(),
      horarioVisitas: P.ouTraco(perfil.horarioVisitas),
      endereco: P.ouTraco(perfil.endereco),
      numero: P.ouTraco(perfil.numero),
      complemento: P.ouTraco(perfil.complemento),
      bairro: P.ouTraco(perfil.bairro),
      cep: perfil.cep ? U.formatarCep(perfil.cep) : "—"
    });
    P.preencherPlaceholders({
      "f-login": perfil.login, "f-razao": perfil.razaoSocial, "f-fantasia": perfil.nomeFantasia,
      "f-resp-nome": perfil.responsavelNome, "f-resp-cargo": perfil.responsavelCargo, "f-email": perfil.email,
      "f-telefone": U.formatarTelefone(perfil.telefones.find((t) => t.principal)?.numero),
      "f-local-nome": perfil.contatoNome, "f-local-funcao": perfil.contatoFuncao,
      "f-local-telefone": U.formatarTelefone(perfil.contatoTelefone), "f-horario": perfil.horarioVisitas,
      "f-endereco": perfil.endereco, "f-numero": perfil.numero, "f-complemento": perfil.complemento,
      "f-bairro": perfil.bairro, "f-cep": U.formatarCep(perfil.cep),
      "f-senha": "Deixe vazio para manter a atual", "f-senha2": "Repita a nova senha"
    });
    P.preencherSelect($("#f-tipo"), perfil.tipoEstabelecimento || "não informado", TIPOS_ESTABELECIMENTO);
    if (telefones) telefones.renderizar();
    if (foto) foto.renderizar();
  }

  /* ---------- 4. FOTOS DO LOCAL (carrossel opcional) ---------- */
  let carrosselLocal = null;

  const fotosParaCarrossel = () => perfil.fotosLocal.map((f, i) => ({
    src: f.src,
    legenda: f.area || "Área não informada",
    alt: `Foto ${i + 1} do local: ${f.area || "área não informada"}`
  }));

  // Controles da foto atual (área + remover) e contadores
  function sincronizarControles(indice) {
    const total = perfil.fotosLocal.length;
    $("#controles-foto-atual").hidden = total === 0;
    $("#fotos-local-total").textContent = `${total} de ${CONFIG.maxFotosLocal} fotos`;
    const cheio = total >= CONFIG.maxFotosLocal;
    const add = $("#btn-add-fotos-local");
    add.disabled = cheio;
    add.title = cheio ? `Limite de ${CONFIG.maxFotosLocal} fotos` : "";
    if (!total) return;
    const i = Math.min(indice, total - 1);
    $("#area-foto").value = perfil.fotosLocal[i].area || "";
    $("#area-foto-posicao").textContent = `(foto ${i + 1} de ${total})`;
  }

  function redesenharFotosLocal(indice) {
    carrosselLocal.atualizar(fotosParaCarrossel(), indice);
    sincronizarControles(carrosselLocal.indice);
    P.atualizarAltura();
  }

  function iniciarFotosLocal() {
    const msg = $("#msg-fotos-local");
    $("#max-fotos-local").textContent = CONFIG.maxFotosLocal;

    // Lista de áreas sugeridas e opções do campo "Área desta foto"
    const lista = $("#lista-areas"), sel = $("#area-foto");
    sel.append(new Option("Selecione a área…", ""));
    AREAS.forEach((a) => {
      const li = document.createElement("li");
      li.textContent = a.nome;
      if (a.exemplos) { const s = document.createElement("small"); s.textContent = a.exemplos; li.append(s); }
      lista.append(li);
      sel.append(new Option(a.nome, a.nome));
    });
    // Abrir/fechar a lista de áreas muda a altura do painel
    $(".areas-sugeridas").addEventListener("toggle", P.atualizarAltura);

    carrosselLocal = window.SDCarrossel.criar({
      alvo: $("#carrossel-local"),
      rotulo: "Fotos do local",
      fotos: fotosParaCarrossel(),
      vazio: "Nenhuma foto do local adicionada. É opcional — use o botão \"Adicionar fotos do local\".",
      aoMudar: (i) => sincronizarControles(i)
    });
    sincronizarControles(0);

    // Trocar a área da foto atual
    sel.addEventListener("change", () => {
      const i = carrosselLocal.indice;
      if (!perfil.fotosLocal[i]) return;
      perfil.fotosLocal[i].area = sel.value;
      redesenharFotosLocal(i);
    });

    // Remover a foto atual
    $("#btn-remover-foto-local").addEventListener("click", () => {
      const i = carrosselLocal.indice;
      const [removida] = perfil.fotosLocal.splice(i, 1);
      if (removida && removida.src.startsWith("blob:")) URL.revokeObjectURL(removida.src);
      redesenharFotosLocal(Math.max(0, Math.min(i, perfil.fotosLocal.length - 1)));
      U.mostrarMensagem(msg, "atencao", "Foto removida nesta tela (ainda não salvo no servidor).");
      if (!perfil.fotosLocal.length) $("#btn-add-fotos-local").focus();
    });

    // Adicionar fotos (várias de uma vez, respeitando o limite)
    $("#btn-add-fotos-local").addEventListener("click", () => $("#input-fotos-local").click());
    $("#input-fotos-local").addEventListener("change", (e) => {
      const arquivos = [...e.target.files];
      e.target.value = "";
      if (!arquivos.length) return;
      const erros = [], primeiraNova = perfil.fotosLocal.length;
      let adicionadas = 0;
      arquivos.forEach((arq) => {
        if (perfil.fotosLocal.length >= CONFIG.maxFotosLocal) { erros.push(`"${arq.name}": limite de ${CONFIG.maxFotosLocal} fotos atingido.`); return; }
        const erro = P.validarArquivo(arq, CONFIG);
        if (erro) { erros.push(erro); return; }
        perfil.fotosLocal.push({ src: URL.createObjectURL(arq), area: "" });
        adicionadas++;
      });
      if (adicionadas) {
        redesenharFotosLocal(primeiraNova);          // mostra a 1ª foto nova
        const texto = `${adicionadas} ${adicionadas === 1 ? "foto adicionada" : "fotos adicionadas"} (pré-visualização, ainda não enviadas ao servidor). Escolha a área de cada foto.`;
        U.mostrarMensagem(msg, "atencao", erros.length ? `${texto} Não adicionadas: ${erros.join(" ")}` : texto);
        $("#area-foto").focus();
      } else {
        U.mostrarMensagem(msg, "erro", erros.join(" "));
      }
    });
  }

  /* ---------- 5. FORMULÁRIO: campos e regras exclusivas do CNPJ ---------- */
  function iniciarFormulario() {
    P.iniciarFormulario({
      perfil,
      coletar: (valor) => ({
        razaoSocial: valor("f-razao"), nomeFantasia: valor("f-fantasia"),
        tipoEstabelecimento: $("#f-tipo").value,
        responsavelNome: valor("f-resp-nome"), responsavelCargo: valor("f-resp-cargo"),
        contatoNome: valor("f-local-nome"), contatoFuncao: valor("f-local-funcao"),
        contatoTelefone: U.soDigitos(valor("f-local-telefone")), horarioVisitas: valor("f-horario")
      }),
      camposTexto: ["razaoSocial", "nomeFantasia", "tipoEstabelecimento", "responsavelNome", "responsavelCargo",
        "contatoNome", "contatoFuncao", "contatoTelefone", "horarioVisitas"],
      validar: (d, marcar) => {
        if (d.razaoSocial && d.razaoSocial.length < 3) marcar("f-razao", "Informe a razão social completa.");
        if (d.nomeFantasia && d.nomeFantasia.length < 2) marcar("f-fantasia", "Nome fantasia muito curto.");
        if (d.responsavelNome && d.responsavelNome.split(/\s+/).length < 2) marcar("f-resp-nome", "Informe nome e sobrenome.");
        if (d.responsavelCargo && d.responsavelCargo.length < 2) marcar("f-resp-cargo", "Cargo muito curto.");
        if (d.contatoNome && d.contatoNome.length < 2) marcar("f-local-nome", "Nome muito curto.");
        if (d.contatoTelefone && !U.telefoneValido(d.contatoTelefone)) marcar("f-local-telefone", "Informe DDD + número (10 ou 11 dígitos).");
      },
      aoConcluir: renderizarDados
    });
  }

  /* ---------- 6. INÍCIO ---------- */
  document.addEventListener("DOMContentLoaded", () => {
    telefones = P.iniciarTelefones(perfil, { max: CONFIG.maxTelefonesSecundarios });
    foto = P.iniciarFotoOpcional({
      perfil, config: CONFIG, padrao: CONFIG.fotoPadraoCliente, tipoIcone: "predio",
      textoAlt: (temFoto) => (temFoto ? "Foto de perfil de " + (perfil.nomeFantasia || perfil.razaoSocial) : "Foto padrão de perfil da empresa")
    });
    renderizarDados();
    iniciarFotosLocal();
    window.SDServicos.renderizar({
      lista: $("#lista-servicos"), total: $("#servicos-total"), vazio: $("#servicos-vazio"),
      servicos, fotoPadraoEmpresa: CONFIG.fotoPadraoEmpresa
    });
    P.iniciarSanfona();
    iniciarFormulario();
    P.iniciarExclusao();
    P.iniciarAbas({ abas: ["#aba-perfil", "#aba-servicos"] });
  });
})();
