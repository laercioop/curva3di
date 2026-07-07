# Curva3DI

**Visualização 3D interativa da curva de juros futuros (DI) da B3**, publicada como um site estático via GitHub Pages.

🔗 **Site ao vivo:** https://laercioop.github.io/curva3di/

![License](https://img.shields.io/badge/license-MIT-blue)
![GitHub Pages](https://img.shields.io/badge/deploy-GitHub%20Pages-222)
![Feito com Plotly.js](https://img.shields.io/badge/gr%C3%A1ficos-Plotly.js-3f4f75)

---

## O que é

O Curva3DI plota a evolução histórica da curva de DI (taxa x prazo x tempo) em um gráfico 3D navegável no navegador, sem precisar de servidor: os dados ficam embutidos no próprio HTML e a renderização é feita com [Plotly.js](https://plotly.com/javascript/).

- **Eixo X** — tempo (datas históricas)
- **Eixo Y** — prazo do vértice (1 dia até 10 anos)
- **Eixo Z** — taxa (% a.a.)

## Funcionalidades

- **Modos de visualização**
  - *Curvas por data* — uma curva de juros por data, ao longo do tempo
  - *Superfície* — superfície 3D contínua taxa × prazo × tempo
  - *Séries por vértice* — evolução histórica de cada vértice isoladamente
  - *Tudo* — combina os três modos acima
  - **Curvas personalizadas** *(exclusivo)* — monte seu próprio comparativo: escolha datas específicas, defina uma cor para cada uma, adicione/remova curvas livremente. Ao ativar esse modo, os demais controles de corte de tempo são substituídos por esse painel.
- **Corte no tempo** — filtre o intervalo de datas exibido (6M, 1A, 2A, 3A, 5A ou tudo) e controle a densidade de curvas plotadas
- **Seleção de vértices** — escolha quais prazos aparecem (todos, principais, curto prazo, ou manual)
- **Controles de câmera** — presets (perspectiva, frente, lado, topo, taxa), zoom, giro automático e nudges
- Interface responsiva, tema azul/branco com animações leves nos botões

## Estrutura do repositório

| Arquivo | Descrição |
|---|---|
| `gerar_curva_di_3d.py` | Lê a planilha histórica de DI e gera `index.html` / `curva_di_3d.html` |
| `index.html` | Página publicada pelo GitHub Pages (gerada — não editar à mão) |
| `curva_di_3d.html` | Cópia idêntica ao `index.html`, mantida para uso local/arquivo |
| `atualizar_e_publicar.bat` | Roda o pipeline completo (gera → commita → envia ao GitHub) com um duplo-clique |
| `.gitignore` | Ignora `__pycache__` e afins |

> `index.html` e `curva_di_3d.html` são **artefatos gerados**. Qualquer alteração de layout, cores ou comportamento deve ser feita em `gerar_curva_di_3d.py`, no bloco `HTML_TEMPLATE`, e depois regenerada.

## Como atualizar os dados

### Opção 1 — duplo clique (recomendado)

Rode `atualizar_e_publicar.bat`. Ele:

1. Lê a planilha de origem e compara a última data já publicada com a mais recente disponível
2. Se não houver dado novo, avisa e para (sem commit vazio)
3. Se houver, gera as páginas, comita e envia (`git push`) para o GitHub automaticamente

### Opção 2 — manual

```bash
python gerar_curva_di_3d.py   # gera index.html e curva_di_3d.html
git add index.html curva_di_3d.html
git commit -m "Atualiza curva DI com dados mais recentes"
git push origin main
```

## Fonte dos dados

A planilha de origem (`didol - novo_ticker.xlsx`, aba `Historico`) contém o histórico diário das taxas de DI por vértice (1 dia, 1M a 10Y). O script:

1. Lê e normaliza a planilha (`read_history`)
2. Preenche lacunas (`ffill`) e monta o payload JSON embutido no HTML (`build_payload`)
3. Injeta esse payload no template HTML/JS via `string.Template`

## Publicação (GitHub Pages)

O repositório está configurado para publicar a branch `main`, raiz `/`, via **Settings → Pages**. Como o gerador sempre escreve tanto `index.html` quanto `curva_di_3d.html`, o site fica disponível automaticamente em `https://laercioop.github.io/curva3di/` a cada push.

## Tecnologias

- [Plotly.js](https://plotly.com/javascript/) (via CDN) para o gráfico 3D
- HTML/CSS/JS puro (sem build step, sem dependências de front-end)
- Python + pandas/openpyxl para o pipeline de geração

## Licença

MIT — veja [LICENSE](LICENSE).
