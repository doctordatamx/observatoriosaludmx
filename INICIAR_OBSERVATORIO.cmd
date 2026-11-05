@echo off

cd /d "%~dp0frontend"

if not exist node_modules (

 echo Faltan dependencias. Ejecuta npm ci en frontend.

 pause

 exit /b 1

)

echo Abre http://127.0.0.1:5173/ en tu navegador.

echo Para detenerlo, presiona Ctrl+C en esta ventana.

npm.cmd run dev -- --port 5173

