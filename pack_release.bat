@echo off
title Icescript Player - Gerar Pacote de Distribuicao
echo ============================================================
echo   Criando Pacote de Distribuicao do Icescript Player (.ZIP)
echo ============================================================
echo.

if not exist "dist\IcescriptPlayer\IcescriptPlayer.exe" (
    echo [INFO] Executavel nao encontrado. Compilando primeiro...
    call build.bat
)

REM Criar arquivo ZIP de distribuicao
powershell -NoProfile -Command "Compress-Archive -Path 'dist\IcescriptPlayer\*' -DestinationPath 'dist\IcescriptPlayer_v1.0.0_Setup.zip' -Force"

if exist "dist\IcescriptPlayer_v1.0.0_Setup.zip" (
    echo.
    echo ============================================================
    echo   PACOTE CRIADO COM SUCESSO!
    echo   Arquivo para enviar ao aluno:
    echo   dist\IcescriptPlayer_v1.0.0_Setup.zip
    echo ============================================================
    echo.
) else (
    echo [ERRO] Falha ao criar arquivo zip.
)

pause
