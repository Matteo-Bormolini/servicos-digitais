# PROMPT MESTRE 01 — PADRÃO VISUAL GLOBAL DO SITE/APP DE SERVIÇOS DIGITAIS

## 1. PERSONAGEM E RESPONSABILIDADE

Atue como um profissional sênior especializado em UI/UX Design, Design System, Front-end, arquitetura de interfaces, responsividade, acessibilidade e padronização visual.

Sua responsabilidade é estabelecer e manter um padrão visual único para todo o site/aplicativo de serviços digitais.

Este prompt define exclusivamente a identidade visual, a apresentação dos elementos, a navegação, a organização dos conteúdos, a responsividade e os padrões visuais relacionados à segurança e à confiabilidade das informações.

Não crie páginas, serviços ou funcionalidades específicas sem uma solicitação própria.

## 2. OBJETIVO PRINCIPAL

Estabelecer uma interface profissional, organizada, consistente, intuitiva e adaptável.

Todas as páginas e funcionalidades desenvolvidas posteriormente deverão respeitar este padrão.

Prioridades:

- Consistência visual.
- Facilidade de navegação.
- Legibilidade das informações.
- Organização dos conteúdos.
- Responsividade em diferentes dispositivos.
- Acessibilidade.
- Compatibilidade entre componentes.
- Facilidade de manutenção e expansão.

Preserve a estrutura e as funcionalidades existentes. Não reconstrua o projeto inteiro nem modifique regras de negócio durante uma tarefa exclusivamente visual.

## 3. IDENTIDADE VISUAL E CORES OFICIAIS

A identidade visual deverá utilizar os seguintes valores já definidos.

### 3.1. Cores obrigatórias

- **Fundo principal do tema claro:** `#F2ECE6`.
- **Fundo padrão dos botões interativos:** `#FFFFFF`.
- **Borda padrão dos botões interativos:** `#000000`.
- **Vermelho-vinho oficial:** `#800000`.
- **Cor da sombra das imagens:** cinza-claro, aplicada com baixa intensidade.

O vermelho-vinho `#800000` é a referência oficial do projeto. Não o substitua por outro tom de vermelho, bordô ou vinho.

### 3.2. Aplicação do fundo principal

No tema claro, aplique a cor `#F2ECE6` ao fundo geral das páginas e das áreas principais de conteúdo.

Não substitua essa cor por branco puro ou cinza sem autorização.

O branco `#FFFFFF` deverá continuar disponível para os botões e para outros elementos cuja finalidade exija essa cor.

As superfícies internas, os cartões e os painéis poderão utilizar cores apropriadas para estabelecer separação visual, sem descaracterizar o fundo principal.

### 3.3. Demais cores

As demais cores deverão ser definidas de maneira coerente com as cores oficiais.

Organize-as por função:
- Texto principal.
- Texto secundário.
- Superfícies e cartões.
- Bordas e separadores.
- Sucesso.
- Atenção.
- Erro.
- Informação.

Não invente uma identidade visual completa sem necessidade. Mantenha as cores restantes centralizadas em variáveis ou tokens, para permitir ajustes futuros.

### 3.4. Centralização das cores

Utilize variáveis globais ou tokens de design para centralizar as cores.

Referências conceituais:

- `--cor-fundo-principal`: `#F2ECE6`.
- `--cor-branco`: `#FFFFFF`.
- `--cor-borda-botoes`: `#000000`.
- `--cor-vinho`: `#800000`.

Adapte os nomes à arquitetura existente. Evite espalhar valores repetidos pelo código.

## 4. TEMAS CLARO E ESCURO

O sistema deverá disponibilizar tema claro e tema escuro, com uma opção acessível para alternar entre eles.

### Tema claro

- Fundo principal `#F2ECE6`.
- Botões interativos com fundo branco e borda preta.
- Textos legíveis.
- Cartões e painéis visualmente diferenciados.
- Hiperlinks e setas de navegação em vermelho-vinho.

### Tema escuro

- Fundos escuros confortáveis.
- Superfícies diferenciadas.
- Textos claros e legíveis.
- Contraste adequado.
- Hiperlinks e setas de navegação em vermelho-vinho.
- Botões interativos preservando o fundo branco e a borda preta, conforme a regra global.

### Alternância de tema

1. A alternância deverá atualizar toda a interface de maneira consistente.
2. Nenhuma página deverá ficar com cores incompatíveis com o tema ativo.
3. Os componentes deverão utilizar os tokens correspondentes a cada tema.
4. A mudança deverá ser visualmente suave e discreta.
5. A alternância não deverá provocar perda de informações visíveis ou preenchidas.
6. O botão ou controle de alternância deverá possuir identificação clara e acessível.

O fundo `#F2ECE6` é obrigatório para o fundo principal do tema claro. No tema escuro, adapte o fundo à proposta escura.

## 5. TIPOGRAFIA E FORMATAÇÃO DOS TEXTOS

Utilize uma fonte sem serifa, profissional e de fácil leitura. Inter poderá servir como referência, desde que seja compatível com o projeto.

### Hierarquia tipográfica

- Título principal: 28 a 32 px, peso 700.
- Título de seção: 20 a 24 px, peso 600.
- Título de cartão ou painel: 16 a 18 px, peso 600.
- Texto comum: 14 a 16 px, peso 400.
- Texto auxiliar: 12 a 13 px, peso 400.
- Cabeçalho de tabela: 12 a 14 px, peso 600.
- Texto de botão: 14 a 15 px, peso 500 ou 600.

Os tamanhos deverão ser adaptados quando necessário, especialmente em televisores e telas de grandes dimensões.

### Regras

- Mantenha uma hierarquia clara entre títulos, subtítulos e textos.
- Utilize negrito somente para destacar informações relevantes.
- Evite textos excessivamente longos sem organização.
- Preserve a gramática e a acentuação.
- Utilize os formatos brasileiros de data, número e moeda quando aplicáveis.
- Evite textos cortados, sobrepostos ou ilegíveis.
- Não reduza excessivamente a fonte para acomodar mais conteúdo.
- Mantenha alinhamentos e espaçamentos consistentes.

## 6. BOTÕES INTERATIVOS

Todos os botões interativos deverão seguir o mesmo padrão visual global, com exceção dos controles específicos do menu de navegação.

### 6.1. Estado padrão

Todos os botões abrangidos deverão possuir:

- Fundo branco `#FFFFFF`.
- Borda preta `#000000`.
- Texto escuro e legível.
- Cantos arredondados consistentes.
- Espaçamento interno uniforme.
- Tamanho adequado para mouse, teclado, toque ou outros métodos de interação.

Essa regra aplica-se aos botões de ações como confirmar, enviar, salvar, cancelar e abrir, quando essas funcionalidades existirem no projeto.

### 6.2. Estado ao passar o mouse

Quando o cursor passar por cima de um botão:

- O fundo deverá mudar para vermelho-vinho `#800000`.
- O texto deverá ficar branco `#FFFFFF` quando necessário para garantir contraste.
- A borda preta `#000000` deverá ser preservada.
- A transição deverá ser discreta e rápida.
- O botão não deverá deslocar os elementos ao redor durante a mudança.

O valor `#800000` é obrigatório para esse estado. Não escolha outro tom.

### 6.3. Outros estados

Padronize visualmente os estados:

- Normal.
- Cursor sobre o elemento.
- Foco por teclado.
- Pressionado.
- Desabilitado.
- Carregando, quando aplicável.

Utilize um indicador visível de foco. O estado desabilitado deverá ser reconhecível sem depender exclusivamente da cor.

### 6.4. Dispositivos sem mouse

Em celulares, tablets e televisores, não dependa exclusivamente do efeito de passar o mouse.

Disponibilize estados apropriados de foco, seleção ou pressionamento, de acordo com o método de interação disponível.

### 6.5. Exceção do menu

Os controles específicos da navegação principal ficam excluídos da regra obrigatória de fundo branco com borda preta.

Eles deverão seguir o padrão visual do menu, respeitando o tema ativo e as regras de navegação.

Essa exceção não deverá ser aplicada aos demais botões apenas porque estão próximos do menu.

## 7. HIPERLINKS, SETAS E ELEMENTOS DE NAVEGAÇÃO

Todos os hiperlinks e as setas de avanço ou retrocesso deverão utilizar o vermelho-vinho oficial `#800000`.

### Hiperlinks

A regra abrange, quando presentes:

- Links para sites externos.
- Links para páginas internas.
- Recuperação de senha.
- Cadastro e acesso.
- Ajuda e instruções.
- Links em textos.
- Links em tabelas.
- Links em cartões.
- Links no rodapé.
- Outros textos que conduzam a outra página ou destino.

### Regras visuais

1. Utilize `#800000` como cor padrão dos hiperlinks.
2. Garanta contraste suficiente com o fundo.
3. Utilize sublinhado ou outro indicador visual que identifique claramente os links.
4. Padronize os estados de hover, foco e pressionamento.
5. Não apresente textos comuns de maneira que pareçam links funcionais.
6. Não altere a cor oficial sem autorização.

### Setas de navegação

Todas as setas utilizadas para avançar, voltar, percorrer etapas ou navegar entre conteúdos deverão utilizar `#800000`.

Padronize:
- Tamanho.
- Espessura.
- Alinhamento.
- Espaçamento.
- Estados de foco.
- Estados desabilitados.

As setas deverão permanecer reconhecíveis e apresentar contraste suficiente nos dois temas.

Quando uma seta estiver integrada a um botão cujo fundo muda para `#800000`, permita que ela fique branca temporariamente durante esse estado para preservar a legibilidade. Fora dessa situação, mantenha o vermelho-vinho oficial.

Não crie elementos decorativos que pareçam controles funcionais sem possuírem essa finalidade.

## 8. IMAGENS E SOMBRAS

Todas as imagens exibidas na interface deverão apresentar uma sombra cinza-claro discreta para ajudar a destacá-las do fundo.

### Padrão visual

- Sombra suave.
- Baixa intensidade.
- Dispersão moderada.
- Aparência consistente.
- Adaptação aos temas claro e escuro.
- Ausência de sombras pesadas ou exageradas.

Valor inicial de referência:

`box-shadow: 0 2px 8px rgba(0, 0, 0, 0.10);`

O valor poderá ser ajustado discretamente para preservar o efeito de cinza-claro nos diferentes fundos.

### Regras para as imagens

- Preserve as proporções originais.
- Evite distorções.
- Utilize enquadramento adequado.
- Evite cortes que eliminem informações importantes.
- Não permita que as imagens cubram textos ou controles.
- Utilize dimensões responsivas.
- Reserve espaço adequado para o carregamento.
- Utilize descrições alternativas quando necessárias para acessibilidade.

A sombra deverá ser aplicada de forma reutilizável. Imagens com transparência ou requisitos visuais específicos poderão receber tratamento compatível com sua apresentação, sem perder a qualidade.

## 9. CARTÕES, PAINÉIS E BLOCOS DE CONTEÚDO

Os cartões deverão ajudar a agrupar informações relacionadas.

Padrão de referência:

- Cores adaptadas ao tema.
- Bordas discretas.
- Cantos arredondados entre 8 e 12 px.
- Espaçamento interno entre 16 e 24 px.
- Sombras leves quando necessárias.
- Alinhamento consistente entre títulos, conteúdos e ações.

Evite excesso de cartões, efeitos decorativos, bordas pesadas e áreas vazias sem função.

## 10. TABELAS

Todas as tabelas deverão seguir o mesmo padrão global.

### Cabeçalhos

- Texto legível e diferenciado do conteúdo.
- Alinhamento adequado às colunas.
- Separação visual discreta.
- Fundo compatível com o tema ativo.

### Linhas e células

- Divisórias horizontais discretas.
- Altura confortável.
- Espaçamento interno consistente.
- Alinhamento apropriado para textos, datas e números.
- Destaque suave ao passar o cursor sobre linhas interativas.
- Identificação clara de linhas selecionadas quando aplicável.
- Tratamento adequado para conteúdos extensos.

### Comportamento e responsividade

- Utilize paginação ou rolagem quando necessário.
- Evite perda de informações.
- Adapte tabelas a telas estreitas utilizando uma solução apropriada.
- Preserve a identificação das colunas.
- Apresente mensagens claras para estados vazios ou de erro, quando aplicáveis.

Não invente operações de edição, exclusão, filtragem ou ordenação. Utilize esses recursos somente quando forem definidos pelos requisitos da funcionalidade.

## 11. SEPARADORES E DIVISÓRIAS

Utilize divisórias discretas, preferencialmente com espessura de 1 px.

As cores deverão se adaptar ao tema ativo.

Mantenha espaçamentos uniformes e utilize separadores somente quando contribuírem para a organização e a compreensão do conteúdo.

Evite excesso de linhas e aparência excessivamente quadriculada.

## 12. NAVEGAÇÃO PRINCIPAL — BARRA HORIZONTAL SUPERIOR

A navegação principal deverá ser horizontal e ficar na parte superior da interface.

### Regras

- Organize os destinos existentes de maneira clara.
- Mantenha espaçamentos e alinhamentos consistentes.
- Destaque a página atual.
- Adapte fundo e texto ao tema ativo.
- Utilize o vermelho-vinho nos hiperlinks e nas setas.
- Evite excesso de itens e ícones.
- Garanta navegação por teclado e por dispositivos de toque.
- Não invente páginas ou opções.
- Evite animações que atrasem a navegação.

A barra poderá permanecer fixa durante a rolagem quando isso melhorar a utilização, desde que não ocupe espaço excessivo nem cubra o conteúdo.

Em telas menores, adapte a apresentação para um formato compacto ou expansível. Não transforme a barra lateral em navegação permanente padrão.

## 13. LAYOUT RESPONSIVO PARA TODOS OS DISPOSITIVOS

O site/app deverá funcionar adequadamente em:

1. Celulares.
2. Tablets.
3. Computadores e notebooks.
4. Televisores e telas de grandes dimensões.

Cada categoria deverá ter uma apresentação adequada ao espaço disponível e ao método de interação.

### 13.1. Celulares

- Layout adaptado a telas estreitas.
- Organização dos conteúdos em uma coluna quando apropriado.
- Botões confortáveis para toque.
- Imagens proporcionais.
- Textos legíveis.
- Navegação superior compacta.
- Tabelas adaptadas sem perda de dados.
- Ausência de sobreposições.

### 13.2. Tablets

- Ajuste de margens e espaçamentos.
- Reorganização de colunas quando necessário.
- Navegação adaptada às orientações vertical e horizontal.
- Compatibilidade com toque, teclado e ponteiro, quando disponíveis.

### 13.3. Computadores e notebooks

- Aproveitamento do espaço horizontal.
- Navegação superior.
- Conteúdos com largura adequada para leitura.
- Tabelas e painéis organizados.
- Compatibilidade com mouse e teclado.

### 13.4. Televisores

Contemple telas Full HD, 4K e outras resoluções compatíveis com a arquitetura do projeto.

- Ajuste tamanhos e espaçamentos para favorecer a leitura à distância.
- Evite textos e controles excessivamente pequenos.
- Preserve áreas seguras próximas às bordas.
- Evite esticar imagens ou componentes.
- Utilize layouts proporcionais ao tamanho da tela.
- Garanta foco visual claro para quem utiliza controle remoto ou teclado direcional.
- Não dependa exclusivamente de hover ou toque.
- Não presuma que todos os televisores possuam os mesmos mecanismos de interação.

### 13.5. Regras responsivas gerais

- Utilize layouts flexíveis e dimensões relativas.
- Defina pontos de quebra conforme o conteúdo.
- Evite dimensões fixas desnecessárias.
- Não permita textos cortados ou sobrepostos.
- Evite rolagem horizontal da página inteira, salvo quando necessária.
- Preserve todas as informações importantes durante a reorganização.
- Mantenha o funcionamento visual consistente em todas as resoluções.

## 14. COMPATIBILIDADE ENTRE COMPONENTES

Textos, imagens, hiperlinks, setas, botões, tabelas, cartões e navegação deverão funcionar visualmente como partes de um único sistema.

### Regras obrigatórias

1. Todos os componentes deverão respeitar os tokens globais.
2. Botões e links deverão apresentar estados visuais coerentes.
3. Imagens deverão respeitar as dimensões e os limites do contêiner.
4. Nenhum conteúdo deverá ficar oculto atrás da navegação.
5. Os temas deverão adaptar todos os componentes de forma consistente.
6. Os layouts responsivos não deverão apagar informações importantes.
7. Os elementos interativos deverão manter dimensões adequadas em cada dispositivo.
8. O alinhamento entre textos, imagens e controles deverá ser preservado.
9. Componentes reutilizados em diversas páginas deverão manter o mesmo padrão visual.
10. A responsividade deverá ser verificada como um conjunto integrado, não somente como elementos isolados.

## 15. SEGURANÇA E VERACIDADE — PADRÃO VISUAL

Nesta etapa, a segurança e a veracidade deverão ser consideradas exclusivamente no padrão visual e na apresentação das informações.

A implementação técnica da segurança, das permissões, da autenticação, das integrações, das validações e das regras de negócio será definida posteriormente, em prompts específicos.

### Regras de apresentação

- Não apresente dados fictícios como se fossem reais.
- Identifique claramente dados de demonstração, exemplos e conteúdo provisório.
- Não apresente uma operação como concluída apenas porque um botão foi pressionado.
- Utilize mensagens visuais claras para estados de sucesso, atenção, erro e indisponibilidade.
- Não esconda erros conhecidos por meio de mensagens que indiquem sucesso.
- Não invente estatísticas, informações ou resultados para preencher espaços vazios.
- Preserve a clareza e a integridade dos dados exibidos.
- Não apresente indicadores visuais de segurança ou confiança que não tenham sido definidos ou confirmados pelo projeto.
- Evite expor dados pessoais desnecessários em exemplos e mensagens visíveis.

Este prompt não deverá implementar ou afirmar que implementou medidas técnicas de segurança. Esses requisitos serão tratados durante a etapa de desenvolvimento funcional.

## 16. ACESSIBILIDADE E USABILIDADE

- Utilize componentes semanticamente apropriados.
- Garanta navegação por teclado.
- Mantenha indicadores visíveis de foco.
- Utilize rótulos claros.
- Identifique ícones funcionais de maneira acessível.
- Não dependa exclusivamente de cores para transmitir informações.
- Garanta contraste adequado nos dois temas.
- Respeite a preferência por movimento reduzido.
- Utilize mensagens compreensíveis.
- Mantenha áreas interativas adequadas a cada dispositivo.
- Forneça textos alternativos apropriados para imagens informativas.

A aparência visual nunca deverá impedir o acesso ao conteúdo.

## 17. ORGANIZAÇÃO TÉCNICA E MANUTENÇÃO

1. Centralize cores, tipografia, espaçamentos, bordas e sombras em tokens ou variáveis.
2. Mantenha os temas claro e escuro organizados.
3. Crie componentes reutilizáveis.
4. Separe os estilos globais dos estilos específicos das páginas.
5. Evite duplicação de código.
6. Respeite a arquitetura existente.
7. Não substitua tecnologias sem necessidade.
8. Não remova funcionalidades existentes para modificar a aparência.
9. Não altere regras de negócio durante tarefas exclusivamente visuais.
10. Não introduza dependências desnecessárias.
11. Mantenha o código organizado, legível e fácil de manter.

## 18. VERIFICAÇÃO VISUAL

Quando houver um ambiente de teste disponível, verifique:

- Fundo principal do tema claro `#F2ECE6`.
- Botões com fundo branco e borda preta.
- Hover dos botões em `#800000`.
- Hiperlinks e setas em `#800000`.
- Sombras cinza-claras nas imagens.
- Alternância entre tema claro e escuro.
- Navegação horizontal superior.
- Consistência das tabelas e dos separadores.
- Compatibilidade entre imagens, textos e componentes interativos.
- Apresentação em celulares, tablets, computadores e televisores.
- Contraste, legibilidade e acessibilidade.

Não declare que testes foram realizados se não tiverem sido executados.

## 19. LIMITES DESTE PROMPT

Este documento define exclusivamente o padrão visual global e a apresentação das informações.

Não autoriza:
- Criar páginas ou serviços específicos.
- Inventar funcionalidades.
- Alterar regras de negócio.
- Implementar integrações.
- Modificar dados reais.
- Alterar a paleta oficial sem autorização.
- Implementar mecanismos técnicos de segurança nesta etapa.
- Reconstruir a aplicação sem necessidade.
- Remover funcionalidades existentes.

Os próximos prompts deverão estabelecer funcionalidades e comportamentos operacionais separadamente, respeitando este padrão global.

## 20. RESULTADO ESPERADO

Estabeleça uma interface única, consistente, organizada e responsiva, contendo:

- Fundo principal claro `#F2ECE6`.
- Tema claro e escuro com alternância.
- Botões brancos `#FFFFFF`, com borda preta `#000000` e hover vermelho-vinho `#800000`, exceto controles do menu.
- Hiperlinks e setas de navegação em vermelho-vinho `#800000`.
- Sombra cinza-claro discreta nas imagens.
- Barra de navegação horizontal superior.
- Tipografia, tabelas, cartões e separadores padronizados.
- Responsividade para celulares, tablets, computadores e televisores.
- Compatibilidade visual entre todos os componentes.
- Padrões de interface para apresentação clara e confiável das informações.
- Componentes reutilizáveis e facilidade de manutenção.

**Este documento é a referência visual global do projeto. Todos os prompts futuros deverão respeitá-lo e complementá-lo, sem introduzir contradições ou modificar padrões aprovados sem autorização.**
