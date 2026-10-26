# SDOnline — S.D Serviços Digitais

Site da plataforma S.D, que conecta clientes (casas, condomínios e empresas) a prestadores de serviço de manutenção.

Site estático em **HTML + CSS + JavaScript puro**. Não precisa instalar nada nem compilar.
Para testar no computador: abra `index.html` (duplo clique) ou publique no GitHub Pages.

> **Situação atual (23/10/2026):** telas prontas em modo **demonstração**. Ainda NÃO existem servidor,
> banco de dados, login real nem segurança real. Nada digitado é salvo ou enviado.

## Estrutura (uma pasta por parte)

```
SDOnline/
├── index.html                 → entrada do site (abre home/)
├── README.md                  → este guia
├── docs/                      → regras do padrão visual
│   ├── prompt-mestre-padrao-visual.md
│   └── padrao-global.md
│
├── configuracoes/             → PADRÃO GLOBAL (vale para todas as páginas)
│   ├── base.css               → cores (claro/escuro), fontes, botões, links, mensagens
│   └── config.js              → caminhos das páginas, menu, rodapé, ícones, sessão de demonstração
├── navbar/                    → barra do topo (navbar.css + navbar.js)
├── rodape/                    → rodapé (rodape.css + rodape.js)
├── seguranca/                 → QUEM PODE VER O QUÊ
│   ├── acesso.js              → regras usadas pela tela (esconde itens)
│   ├── permissoes.json        → as mesmas regras, para o servidor (bloqueio real)
│   └── index.html             → tabela de consulta das regras
├── fotos/
│   ├── marca/                 → logos (provisórias)
│   └── padrao/                → fotos padrão de perfil (provisórias)
│
├── componentes/               → PEÇAS REUTILIZÁVEIS (escritas uma vez, usadas em várias páginas)
│   ├── utilidades/            → formatar telefone/CEP/data/R$, estrelas, fotos com reserva
│   ├── formulario/            → visual dos campos (login, cadastro, editar perfil)
│   ├── perfil-base/           → tudo que é igual nos 4 perfis (abas, telefones, edição, exclusão)
│   ├── carrossel/             → carrossel de fotos
│   ├── servicos-realizados/   → histórico de serviços (clientes CPF e CNPJ)
│   └── kanban-servicos/       → quadro "Meus serviços" (prestador)
│
├── modelo-pagina/             → modelo para criar páginas novas
├── home/                      → página inicial (visitante x logado)
├── login-cadastro/            → Fazer login + Criar login (CPF, CNPJ, Prestador)
├── perfil-adm/                → perfil do Administrador
├── perfil-cliente-cpf/        → perfil do Cliente CPF
├── perfil-cliente-cnpj/       → perfil do Cliente CNPJ
└── perfil-prestador/          → perfil do Prestador (+ "Ver como cliente" e Kanban)
```

Cada página fica em `<pasta>/index.html`, com o CSS e o JS dela na mesma pasta.

## Ordem dos arquivos em toda página

```html
<link rel="stylesheet" href="../configuracoes/base.css">
<link rel="stylesheet" href="../navbar/navbar.css">
<link rel="stylesheet" href="../rodape/rodape.css">
<!-- componentes usados pela página (opcional) -->
<link rel="stylesheet" href="NOME-DA-PAGINA.css">
<script src="../seguranca/acesso.js" defer></script>     <!-- 1º -->
<script src="../configuracoes/config.js" defer></script>  <!-- 2º -->
<script src="../navbar/navbar.js" defer></script>
<script src="../rodape/rodape.js" defer></script>
<!-- componentes usados pela página (opcional) -->
<script src="NOME-DA-PAGINA.js" defer></script>
```

O `<body>` informa:

| Atributo | Valores | Para quê |
|---|---|---|
| `data-pagina` | inicio, servicos, clientes, prestador, sobre, politicas, suporte, perfil | destaca o item do menu |
| `data-logado` | `nao` / `sim` | o **servidor** preenche; libera itens com cadeado |
| `data-tipo` | cliente-cpf, cliente-cnpj, prestador, adm | define o "Meu perfil" e os itens do menu |
| `data-raiz` | `../` | caminho até a pasta SDOnline |

**Não recrie** menu, rodapé, cores, botões ou campos dentro das páginas: altere só em
`configuracoes/`, `navbar/`, `rodape/` ou `componentes/`.

## Tipos de usuário (mesmo nome em todo o site)

| Tipo | Página "Meu perfil" | Menu depois de entrar |
|---|---|---|
| `cliente-cpf` | `perfil-cliente-cpf/` | vê "Para clientes" |
| `cliente-cnpj` | `perfil-cliente-cnpj/` | vê "Para clientes" |
| `prestador` | `perfil-prestador/` | vê "Seja um prestador" |
| `adm` | `perfil-adm/` | vê os dois |

As regras ficam em `seguranca/acesso.js` (tela) e `seguranca/permissoes.json` (servidor). Mudou uma, mude a outra.

## Testar navegando logado (modo demonstração)

1. Abra `home/` → **Entrar**.
2. Digite qualquer e-mail e senha, escolha **Entrar como** (CPF, CNPJ, Prestador ou Administrador) → **Fazer login**.
3. A Home abre na visão do logado; **Meu perfil** leva ao perfil do tipo escolhido; **Sair** desconecta.
4. "Criar login" também entra direto no tipo cadastrado.

O "login" de demonstração guarda só `{ tipo, nome }` na aba do navegador (sessionStorage) e some ao fechar a aba.
**Nunca guarda senha.** Para desligar quando houver servidor: `modoDemonstracao: false` em `configuracoes/config.js`.

## Criar uma página nova

1. Copie a pasta `modelo-pagina/` e renomeie (ex.: `sobre/`).
2. Troque o `<title>`, o `data-pagina` e o conteúdo.
3. Estilos próprios: crie `sobre.css` usando só os tokens `--cor-*` do `base.css`.

## Cores oficiais

| Uso | Cor |
|---|---|
| Fundo principal (tema claro) | `#F2ECE6` |
| Botões | fundo `#FFFFFF`, borda `#000000` |
| Hover dos botões, links e setas | `#800000` |
| NavBar e Rodapé | `#800000` (hover do menu `#5C0000`) |
| Fundo do tema escuro | `#161312` |

## Segurança — importante

- `data-logado`, `data-tipo` e a sessão de demonstração só mudam a **tela**. Qualquer pessoa pode alterar isso no navegador.
  Login, permissões e dados têm de ser validados no **servidor** (próxima etapa).
- Senhas: nunca exibidas, nunca guardadas no navegador. No servidor, só o hash.
- Textos colocados no HTML pelos scripts passam por escape (`textContent` ou `SD.esc`).
- **Não coloque senhas, chaves de API ou dados reais de clientes neste repositório** (ele pode ficar público no GitHub Pages).

## Páginas ainda não criadas

Já aparecem nos links, mas as pastas ainda não existem (dão erro 404):
`localizar-prestador/` · `localizar-condominios/` · `avaliacoes/` · `sobre/` · `politicas/` · `suporte/` ·
`termos/` · `responsabilidade/` · `politica-privacidade/`.

## Pendências conhecidas

- Servidor, banco de dados, login real, recuperação de senha e segurança (próxima etapa).
- Logo provisória: trocar `fotos/marca/` e o SVG `ICONES.logo` em `configuracoes/config.js`.
- Fotos padrão provisórias em `fotos/padrao/` (trocar mantendo os nomes).
- Tema escuro: link `#800000` tem pouco contraste; solução provisória = link com fundo `#F2ECE6`.
- Perfil do cliente visto pelo prestador (com avaliações) ainda a criar.
