@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title Curva DI 3D - Atualizar e Publicar
color 0B

echo.
echo   ============================================================
echo                CURVA DI 3D - ATUALIZAR E PUBLICAR
echo   ============================================================
echo.
echo   [1/3] Verificando planilha e gerando paginas...
echo   ------------------------------------------------------------
python gerar_curva_di_3d.py
set PY_STATUS=%errorlevel%
echo   ------------------------------------------------------------

if %PY_STATUS%==2 (
    echo.
    echo   ^>^> Nada a fazer: a planilha nao tem datas novas.
    echo.
    goto fim
)
if not %PY_STATUS%==0 (
    color 0C
    echo.
    echo   ^>^> ERRO ao gerar as paginas. Nenhum commit foi feito.
    echo.
    pause
    exit /b 1
)

echo.
echo   [2/3] Registrando alteracoes no git...
echo   ------------------------------------------------------------
git add curva_di_3d.html index.html
git commit -m "Atualiza curva DI com dados mais recentes"
echo   ------------------------------------------------------------

echo.
echo   [3/3] Enviando para o GitHub...
echo   ------------------------------------------------------------
git push origin main
if errorlevel 1 (
    color 0C
    echo   ------------------------------------------------------------
    echo.
    echo   ^>^> ERRO ao enviar para o GitHub. Verifique sua conexao/login.
    echo.
    pause
    exit /b 1
)
echo   ------------------------------------------------------------

echo.
echo   ^>^> Publicado com sucesso!
echo   ^>^> Site: https://laercioop.github.io/curva3di/

:fim
echo.
pause
