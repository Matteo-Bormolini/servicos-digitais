/* =====================================================================
   S.D — REGRAS DE ACESSO DA TELA (seguranca/acesso.js)
   Diz QUEM pode ver CADA parte do site. Carregar em TODAS as páginas,
   ANTES de configuracoes/config.js.
   Manter IGUAL a seguranca/permissoes.json (versão que o servidor usa).

   IMPORTANTE: isto só ESCONDE itens na tela. O bloqueio real tem de ser
   feito no SERVIDOR, conferindo o perfil em cada página e em cada consulta.
   ===================================================================== */
(function () {
  "use strict";

  /* ---------- 1. PERFIS (tipos de usuário) ---------- */
  const PERFIS = {
    "visitante":    "Visitante",
    "cliente-cpf":  "Cliente CPF",
    "cliente-cnpj": "Cliente CNPJ",
    "prestador":    "Prestador",
    "adm":          "Administrador"
  };
  const LOGADOS = ["cliente-cpf", "cliente-cnpj", "prestador", "adm"];

  /* ---------- 2. RECURSO → PERFIS QUE PODEM ACESSAR ("*" = todos) ----------
     Os nomes dos itens do menu são os mesmos "id" de configuracoes/config.js. */
  const REGRAS = {
    // Itens do menu e páginas públicas
    "inicio":    ["*"],
    "servicos":  ["*"],
    "sobre":     ["*"],
    "politicas": ["*"],
    "suporte":   ["*"],
    // "Para clientes" (buscar prestadores) — só clientes (e adm para suporte)
    "clientes":  ["cliente-cpf", "cliente-cnpj", "adm"],
    // "Seja um prestador" (localizar condomínios) — só prestador (e adm)
    "prestador": ["prestador", "adm"],
    // Conta
    "login-cadastro": ["visitante"],
    "meu-perfil":     LOGADOS,
    "sair":           LOGADOS,
    // Páginas de perfil (o adm acessa todas para manutenção e suporte)
    "perfil-adm":          ["adm"],
    "perfil-cliente-cpf":  ["cliente-cpf", "adm"],
    "perfil-cliente-cnpj": ["cliente-cnpj", "adm"],
    "perfil-prestador":    ["prestador", "adm"]
  };

  /* ---------- 3. FUNÇÕES ---------- */
  // Negar por padrão: recurso sem regra fica bloqueado
  function pode(perfil, recurso) {
    const regra = REGRAS[recurso];
    if (!regra) return false;
    return regra.includes("*") || regra.includes(perfil || "visitante");
  }
  // Nome amigável do perfil ("cliente-cpf" → "Cliente CPF")
  const nomePerfil = (perfil) => PERFIS[perfil] || PERFIS.visitante;
  const perfilValido = (perfil) => Object.prototype.hasOwnProperty.call(PERFIS, perfil);

  window.SD_ACESSO = Object.freeze({ PERFIS, LOGADOS, REGRAS, pode, nomePerfil, perfilValido });
})();
