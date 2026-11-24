# Painel de Ocorrências

Gera o painel semanal de ocorrências da TrackServices a partir da planilha **"Análise de Ocorrências"** (`.xlsm`/`.xlsx`). O resultado é um único arquivo HTML, sem dependências, que abre em qualquer navegador.

Lê da planilha:

- aba `0. ANAYLSIS`: ocorrências (cliente, placa, tipo, dias, observação, ação, "não notificar");
- aba `99. SETUP`: contatos dos clientes (colunas CLIENTE / NOME / TELEFONE).

Tipos de ocorrência tratados: Offline, Câmera com falha, Consumo de chip alto, Operando sem consumo, Cartão SD ausente, entre outros (ver `TIPOS` em `src/gerar_painel.py`).

## Estrutura

```
src/        app.py (janela Tkinter), gerar_painel.py (leitura da planilha + geração do HTML)
assets/     painel_modelo.html (template), ícone e logo
packaging/  build.bat, instalador.iss (Inno Setup), PainelOcorrencias.spec
docs/       COMANDOS.txt
output/     HTML gerado em modo linha de comando (ignorado pelo git)
```

## Instalar (usuário final)

1. Baixe o `Instalar-PainelOcorrencias.exe` na [última versão](https://github.com/KenzoLima/Painel-de-ocorrencias/releases/latest).
2. Dê dois cliques. Não precisa de administrador; instala em `%LOCALAPPDATA%\Programs\PainelOcorrencias`.
3. Abra pelo atalho do Menu Iniciar (ou da Área de Trabalho, se marcar a opção).

O Windows SmartScreen pode mostrar "editor desconhecido", pois o instalador não é assinado. Clique em **Mais informações → Executar assim mesmo**.

O painel abre numa janela do próprio programa (usa o WebView2, que já vem no Windows 11 e na maioria dos Windows 10).

## Requisitos

- Windows
- Python 3.10+ com `tkinter` (já vem no instalador oficial do Python)
- `openpyxl`
- `pywebview` (janela do painel)

```bash
pip install openpyxl pywebview
```

Só para gerar o instalador: `pyinstaller` e [Inno Setup 6](https://jrsoftware.org/isinfo.php).

## Como rodar

### Opção 1 — Janela (interface gráfica)

```bash
python src/app.py
```

Escolha a planilha na janela. O painel é gerado e aberto no navegador. Também dá para passar a planilha como argumento:

```bash
python src/app.py "Análise de Ocorrências - 9-11.xlsm"
```

No modo janela/instalado, o HTML é salvo em `%LOCALAPPDATA%\PainelOcorrencias\painel_ocorrencias.html`. O caminho é fixo para manter as marcações de "enviado" entre uma geração e outra.

### Opção 2 — Linha de comando

```bash
python src/gerar_painel.py "CAMINHO DA PLANILHA"            # grava em output/painel_ocorrencias.html
python src/gerar_painel.py "CAMINHO DA PLANILHA" saida.html # caminho de saída personalizado
```

Depois abra o arquivo gerado:

```bash
start output\painel_ocorrencias.html
```

## Gerar o instalador

```bash
packaging\build.bat
```

Roda o PyInstaller e o Inno Setup. O resultado fica em `dist\Instalar-PainelOcorrencias.exe`.

## Publicar uma nova versão

O instalador não vai para o git (pesa ~30 MB); ele é distribuído como *release* do GitHub.

1. Suba `AppVersion` em `packaging/instalador.iss` (ex.: `1.0.1`).
2. Gere o instalador: `packaginguild.bat` (resultado em `dist\` e copiado para a raiz).
3. Commit e push das mudanças.
4. Crie o release com o [GitHub CLI](https://cli.github.com/) (`gh auth login` uma vez):

```bash
gh release create v1.0.1 Instalar-PainelOcorrencias.exe --title "v1.0.1" --notes "O que mudou"
```

O link `.../releases/latest` passa a apontar para a versão nova automaticamente. Para corrigir um release já criado: `gh release upload v1.0.1 Instalar-PainelOcorrencias.exe --clobber`.

## Notas

- `build/`, `dist/`, `output/` e `*.spec` são gerados e não vão para o git.
- Se a estrutura da planilha mudar (nomes das abas ou ordem das colunas), ajuste `ler()` em `src/gerar_painel.py`.


abroba