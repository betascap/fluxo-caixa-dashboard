@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title Dashboard FC - Ville de Provence

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║        Dashboard Fluxo de Caixa - Ville de Provence       ║
echo ║                   v1.0 - Streamlit                        ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

REM Verificar se o CSV existe
if not exist "output\fc_dados.csv" (
    echo ⚠️  AVISO: Arquivo output\fc_dados.csv não encontrado!
    echo.
    echo Você precisa:
    echo   1. Clicar em RODAR_SIENGE_TO_CSV.bat
    echo   2. Selecionar o PDF do Sienge
    echo   3. Gerar o CSV
    echo.
    echo Depois volte aqui e clique neste arquivo novamente.
    echo.
    pause
    exit /b 1
)

echo ✅ Dados encontrados: output\fc_dados.csv
echo.
echo 🚀 Iniciando dashboard...
echo.
echo 💻 Dashboard abrirá automaticamente em: http://localhost:8501
echo.
echo 👉 Se não abrir, acesse manualmente no navegador.
echo.
echo ⚠️  Não feche esta janela enquanto usar o dashboard.
echo    Pressione Ctrl+C para parar o servidor.
echo.

python -m streamlit run app.py --logger.level=warning

pause
