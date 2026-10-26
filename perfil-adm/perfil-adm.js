/* =====================================================================
   S.D — PERFIL DO ADMINISTRADOR (perfil-adm/perfil-adm.js)
   O comportamento comum (abas, telefones, edição, exclusão) vem de
   componentes/perfil-base/perfil-base.js. Aqui fica só o exclusivo do adm:
     - "Cargo" = "Administrador - <cargo definido pelo líder>"
     - Foto de perfil (sem foto → iniciais do nome) + galeria de até 12 fotos
     - Aba "Administração" (em desenvolvimento)
   O adm vê dados sigilosos dos usuários, mas NUNCA a senha (hash no servidor).
   IMPORTANTE: demonstração — salvar/enviar de verdade depende do servidor.
   ===================================================================== */
(function () {
  "use strict";
  const U = window.SDUtil, P = window.SDPerfil, SD = window.SD;
  const $ = P.$;

  /* ---------- 1. CONFIGURAÇÃO (fácil de ajustar) ---------- */
  const CONFIG = {
    ...P.PADRAO,                 // telefones (4), fotos (JPG/PNG/WEBP até 5 MB)
    maxFotosGaleria: 12,
    urlAvaliacoes: SD.urlPagina("avaliacoes")
  };

  /* ---------- 2. DADOS DE DEMONSTRAÇÃO ----------
     Substituir pelos dados vindos do servidor depois do login. */
  const perfil = {
    login: "admin.sd",
    nome: "Nome Sobrenome Exemplo",
    cargoBase: "Administrador",          // fixo para o tipo adm
    cargoLider: "Suporte da plataforma", // definido pelo líder
    documento: "000.000.000-00",
    email: "admin@exemplo.com.br",
    telefones: [{ numero: "11900000000", principal: true }],
    endereco: "Rua Exemplo",
    numero: "100",
    complemento: "Sala 1",
    bairro: "Centro",
    cep: "01000000",
    avaliacao: { media: 4.8, total: 12 },
    foto: null,
    galeria: []
  };

  let telefones = null;

  /* ---------- 3. EXIBIÇÃO DOS DADOS ---------- */
  function renderizarDados() {
    P.preencherCampos({
      login: perfil.login,
      nome: perfil.nome,
      cargo: perfil.cargoBase + " - " + perfil.cargoLider,  // espaço antes e depois do "-"
      documento: perfil.documento,
      email: perfil.email,
      endereco: P.ouTraco(perfil.endereco),
      numero: P.ouTraco(perfil.numero),
      complemento: P.ouTraco(perfil.complemento),
      bairro: P.ouTraco(perfil.bairro),
      cep: perfil.cep ? U.formatarCep(perfil.cep) : "—"
    });
    P.preencherLinkAvaliacoes($("#link-avaliacoes"), perfil.avaliacao, CONFIG.urlAvaliacoes);
    P.preencherPlaceholders({
      "f-login": perfil.login, "f-nome": perfil.nome, "f-email": perfil.email,
      "f-telefone": U.formatarTelefone(perfil.telefones.find((t) => t.principal)?.numero),
      "f-endereco": perfil.endereco, "f-numero": perfil.numero, "f-complemento": perfil.complemento,
      "f-bairro": perfil.bairro, "f-cep": U.formatarCep(perfil.cep),
      "f-senha": "Deixe vazio para manter a atual", "f-senha2": "Repita a nova senha"
    });
    if (telefones) telefones.renderizar();
    renderizarFoto();
  }

  /* ---------- 4. FOTO DE PERFIL E GALERIA ---------- */
  function renderizarFoto() {
    const img = $("#foto-perfil");
    img.src = perfil.foto || U.iconeIniciais(perfil.nome);
    img.alt = "Foto de perfil de " + perfil.nome;
  }

  function renderizarGaleria() {
    const grade = $("#galeria-grade");
    grade.innerHTML = "";
    perfil.galeria.forEach((url, i) => {
      const li = document.createElement("li");
      const img = document.createElement("img");
      img.src = url; img.alt = `Foto secundária ${i + 1}`; img.loading = "lazy";
      const rem = document.createElement("button");
      rem.type = "button"; rem.className = "btn-remover"; rem.innerHTML = P.ICONES.x;
      rem.setAttribute("aria-label", `Remover foto secundária ${i + 1}`);
      rem.addEventListener("click", () => { URL.revokeObjectURL(url); perfil.galeria.splice(i, 1); renderizarGaleria(); $("#btn-galeria").focus(); });
      li.append(img, rem);
      grade.append(li);
    });
    $("#titulo-galeria").textContent = `Galeria (${perfil.galeria.length})`;
    $("#galeria-vazia").hidden = perfil.galeria.length > 0;
    $("#btn-galeria").disabled = perfil.galeria.length >= CONFIG.maxFotosGaleria;
    P.atualizarAltura();
  }

  function iniciarFotos() {
    const msg = $("#msg-foto");
    $("#btn-foto").addEventListener("click", () => $("#input-foto").click());
    $("#btn-galeria").addEventListener("click", () => $("#input-galeria").click());

    $("#input-foto").addEventListener("change", (e) => {
      const arq = e.target.files[0];
      e.target.value = "";
      if (!arq) return;
      const erro = P.validarArquivo(arq, CONFIG);
      if (erro) { U.mostrarMensagem(msg, "erro", erro); return; }
      if (perfil.foto) URL.revokeObjectURL(perfil.foto);
      perfil.foto = URL.createObjectURL(arq);
      renderizarFoto();
      U.mostrarMensagem(msg, "atencao", "Pré-visualização atualizada (ainda não enviada ao servidor).");
    });

    $("#input-galeria").addEventListener("change", (e) => {
      const arquivos = [...e.target.files];
      e.target.value = "";
      const problemas = [];
      arquivos.forEach((arq) => {
        if (perfil.galeria.length >= CONFIG.maxFotosGaleria) { problemas.push(`Limite de ${CONFIG.maxFotosGaleria} fotos atingido.`); return; }
        const erro = P.validarArquivo(arq, CONFIG);
        if (erro) problemas.push(erro); else perfil.galeria.push(URL.createObjectURL(arq));
      });
      renderizarGaleria();
      if (problemas.length) U.mostrarMensagem(msg, "erro", [...new Set(problemas)].join(" "));
      else if (arquivos.length) U.mostrarMensagem(msg, "atencao", "Fotos adicionadas à pré-visualização (ainda não enviadas ao servidor).");
    });
  }

  /* ---------- 5. INÍCIO ---------- */
  document.addEventListener("DOMContentLoaded", () => {
    telefones = P.iniciarTelefones(perfil, { max: CONFIG.maxTelefonesSecundarios });
    renderizarDados();
    renderizarGaleria();
    P.iniciarSanfona();
    P.iniciarFormulario({
      perfil,
      coletar: (valor) => ({ nome: valor("f-nome") }),
      camposTexto: ["nome"],
      validar: (d, marcar) => {
        if (d.nome && d.nome.split(/\s+/).length < 2) marcar("f-nome", "Informe nome e sobrenome.");
      },
      aoConcluir: renderizarDados
    });
    iniciarFotos();
    P.iniciarExclusao();
    P.iniciarAbas({ abas: ["#aba-perfil", "#aba-admin"] });
  });
})();
