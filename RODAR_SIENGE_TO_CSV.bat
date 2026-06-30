@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ============================================
echo  Gerador de Dados para Dashboard BI
echo ============================================
echo.

REM Pedir caminho do PDF
set /p pdf_path="Caminho completo do PDF (ex: C:\Users\...\CONTAS PAGAS.pdf): "

if not exist "!pdf_path!" (
    echo.
    echo ERRO: Arquivo PDF nao encontrado em "!pdf_path!"
    echo.
    pause
    exit /b 1
)

REM Pedir caminho do Excel (opcional)
set /p xlsx_path="Caminho do Excel para atualizar (deixe em branco para pular): "

REM Pedir caminho do CSV de saida
set /p csv_path="Caminho do CSV de saida (ex: fc_dados.csv): "
if "!csv_path!"=="" (
    set csv_path=fc_dados.csv
)

echo.
echo Processando...
echo.

REM Rodar o script
if "!xlsx_path!"=="" (
    python sienge_to_bi.py "!pdf_path!" "" "!csv_path!"
) else (
    python sienge_to_bi.py "!pdf_path!" "!xlsx_path!" "!csv_path!"
)

echo.
if %errorlevel% equ 0 (
    echo ============================================
    echo  SUCESSO!
    echo ============================================
    echo.
    echo Proximos passos:
    echo 1. Abra Power BI Desktop
    echo 2. Importe o arquivo: !csv_path!
    echo 3. Crie os graficos conforme README_POWERBI.md
    echo.
) else (
    echo ============================================
    echo  ERRO na execucao
    echo ============================================
    echo.
)

pause
