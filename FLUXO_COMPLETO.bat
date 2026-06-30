@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title Dashboard FC - Fluxo Completo

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║     Fluxo Completo: Sienge PDF → Dashboard              ║
echo ║             Ville de Provence v1.0                      ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

REM Passo 1: Perguntar pelo PDF
set /p pdf_path="📄 Caminho do PDF do Sienge (ex: C:\...\CONTAS PAGAS.pdf): "

if not exist "!pdf_path!" (
    echo.
    echo ❌ ERRO: Arquivo não encontrado em "!pdf_path!"
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ PDF encontrado: !pdf_path!
echo.

REM Passo 2: Processar dados
echo 📊 Processando dados...
echo.

python sienge_to_bi.py "!pdf_path!" "" "output\fc_dados.csv"

if !errorlevel! neq 0 (
    echo.
    echo ❌ ERRO ao processar PDF
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Dados processados com sucesso!
echo.

REM Passo 3: Aguardar um pouco e abrir dashboard
echo.
echo 🚀 Iniciando dashboard em 3 segundos...
timeout /t 3 /nobreak

echo.
echo 💻 Dashboard abrirá em: http://localhost:8501
echo.
echo ⚠️  Não feche esta janela enquanto usar o dashboard.
echo    Pressione Ctrl+C para parar.
echo.

python -m streamlit run app.py --logger.level=warning

pause
