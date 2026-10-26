# Site S.D — Padrão global de TODAS as páginas (atualizado 23/10/2026)

Regra: toda página nova parte de `modelo-pagina/index.html`. NÃO recriar NavBar, Rodapé, cores, botões ou campos dentro de cada página — alterar só nos arquivos globais:

| Parte | Arquivo |
|---|---|
| Cores, fontes, botões, links, mensagens | `configuracoes/base.css` |
| Caminhos, menu, rodapé, ícones, sessão de demonstração | `configuracoes/config.js` |
| Quem vê o quê | `seguranca/acesso.js` + `seguranca/permissoes.json` |
| Barra do topo | `navbar/navbar.css` + `navbar/navbar.js` |
| Rodapé | `rodape/rodape.css` + `rodape/rodape.js` |
| Campos de formulário | `componentes/formulario/formulario.css` |
| Funções pequenas (telefone, CEP, R$, estrelas, fotos) | `componentes/utilidades/utilidades.js` |
| Base dos perfis | `componentes/perfil-base/` |

## Estrutura de toda página
```html
<body data-pagina="ID_DO_MENU" data-logado="nao|sim" data-tipo="" data-raiz="../">
  <header id="sd-navbar"></header>   <!-- montado pelo navbar.js -->
  <main id="conteudo"> ... </main>
  <footer id="sd-rodape"></footer>   <!-- montado pelo rodape.js -->
```

## NavBar
- Fundo vinho #800000, textos brancos; fixa no topo; hover #5C0000 com contorno branco.
- 7 itens: Início · Serviços · Para clientes 🔒 · Seja um prestador 🔒 · Sobre nós · Políticas · Suporte.
- 🔒 visitante → login com destino. Logado → só os itens permitidos para o tipo (prestador não vê "Para clientes"; clientes não veem "Seja um prestador"; adm vê os dois).
- Direita: tema (lua/sol); visitante: Entrar + Criar conta; logado: Meu perfil + Sair.
- Menu compacto (3 riscos) abaixo de 1260px; fecha com Esc ou clique fora.

## Rodapé
- Marca + descrição · Navegação · Políticas · Baixe o app ("Em breve"; escondido no app).
- Aviso: Suporte é só para erros e melhorias da plataforma.

## Cores
- Fundo claro #F2ECE6 · botões #FFFFFF borda #000000 · hover/links/setas #800000 · menu hover #5C0000.
- Tema escuro só se o usuário escolher. Fundo #161312, superfície #221E1C.
- Sombra de imagens: 0 2px 8px rgba(0,0,0,.10). Cartões raio 12px, botões 8px.

## Componentes globais
- .btn (normal, hover vinho, foco, pressionado, desabilitado tracejado), .btn-icone, .btn-pequeno, .btn-seta.
- .link, .mensagem.sucesso|erro|info|atencao, .selo-demo, .visualmente-oculto, .img-sombra.
- Campos: .campo, .campo-erro, .campo-check, .senha-caixa + .btn-olho, .form-grade.
