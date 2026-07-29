# Como Criar o Executável SGEP Pedidos

## Pré-requisitos

- Python 3.14+ instalado
- Pacotes necessários:

```bash
pip install selenium webdriver-manager pyinstaller
```

## Estrutura do Projeto

```
Automatizar pedidos - Copia/
├── main.py              # Ponto de entrada
├── config.py            # Configurações (login, seletores, clientes)
├── SGEP_Pedidos.spec    # Arquivo de build do PyInstaller
├── pages/
│   ├── interface.py     # Interface gráfica (Tkinter)
│   ├── pedidos.py       # Automação de pedidos (Selenium)
│   ├── pdf.py           # Download automático de PDFs
│   └── __init__.py
├── utils/
│   ├── driver.py        # Gerenciamento do ChromeDriver
│   ├── waits.py         # Helpers de espera e clique
│   └── __init__.py
└── dist/
    └── SGEP_Pedidos.exe # Executável gerado
```

## Gerar o Executável

### Opção 1 — Usando o .spec (recomendado)

```bash
cd "D:\Documento\#Estudo & Trabalho\Código\Automatizar pedidos - Copia"

# Limpar builds anteriores (opcional, mas recomendado)
rmdir /s /q dist 2>nul
rmdir /s /q build 2>nul

# Gerar o executável
python -m PyInstaller SGEP_Pedidos.spec --noconfirm
```

O executável será gerado em `dist\SGEP_Pedidos.exe`.

### Opção 2 — Comando direto (sem .spec)

```bash
python -m PyInstaller --onefile --noconsole --name SGEP_Pedidos ^
    --add-data "config.py;." ^
    --add-data "pages;pages" ^
    --add-data "utils;utils" ^
    --hidden-import selenium ^
    --hidden-import webdriver_manager ^
    --hidden-import tkinter ^
    main.py
```

## Limpar Build Anterior

Antes de gerar um novo executável, delete as pastas `dist` e `build`:

```bash
rmdir /s /q dist
rmdir /s /q build
```

Ou no PowerShell:

```powershell
Remove-Item -Recurse -Force dist, build -ErrorAction SilentlyContinue
```

## Adicionar/Remover Arquivos

Se você criar novos arquivos `.py` em `pages/` ou `utils/`, eles já estão incluídos automaticamente via o `.spec`:

```python
# SGEP_Pedidos.spec — linha 8
datas=[('config.py', '.'), ('pages', 'pages'), ('utils', 'utils')]
```

Se adicionar uma **pasta nova**, adicione ao `.spec`:

```python
datas=[('config.py', '.'), ('pages', 'pages'), ('utils', 'utils'), ('nova_pasta', 'nova_pasta')]
```

## Dependências

Se usar uma nova biblioteca externa, adicione ao `hiddenimports` no `.spec`:

```python
hiddenimports=['selenium', 'webdriver_manager', 'tkinter', 'nova_biblioteca']
```

## Solução de Problemas

### Executável não abre

- Verifique se `main.py` existe na raiz do projeto
- Execute o `.exe` pelo terminal para ver erros: `dist\SGEP_Pedidos.exe`

### Erro de import no executável

- Adicione o módulo em `hiddenimports` no `.spec`
- Execute `--noconfirm` para forçar rebuild completo

### Chrome não inicia

- O `webdriver-manager` baixa o chromedriver automaticamente
- Verifique se o Chrome está instalado na máquina
