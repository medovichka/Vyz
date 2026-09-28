@echo off
chcp 65001 >nul
cd /d "%~dp0"
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo [ПРЕДУПРЕЖДЕНИЕ] .venv не найден, используется системный Python
)
:menu
cls
echo ====================================
echo    УПРАВЛЕНИЕ ПРОГНОЗОМ ПОГОДЫ
echo ====================================
echo.
echo  [1] Полный цикл
echo  [2] Получить широту, долготу - api_caller.py
echo  [3] Точки погоды - wpp_parser.py
echo  [4] Удалить weather.md
echo  [5] Удалить weather.db
echo  [0] Выход
echo.
set /p choice="Выберите пункт: "

if "%choice%"=="1" goto full_run
if "%choice%"=="2" goto test_geo
if "%choice%"=="3" goto test_parse
if "%choice%"=="4" goto delete_md
if "%choice%"=="5" goto delete_db
if "%choice%"=="0" goto end
goto menu

:full_run
cls
python main.py
pause
goto menu

:test_geo
cls
python -c "from api_caller import get_geo; from config import MY_IP; print(get_geo(MY_IP))"
pause
goto menu

:test_parse
cls
python wpp_parser.py
pause
goto menu

:delete_md
cls
if exist weather.md (
    del weather.md
    echo Md удален.
) else (
    echo Md не найден.
)
pause
goto menu

:delete_db
cls
if exist weather.db (
    del weather.db
    echo База данных удалена.
) else (
    echo База данных не найдена.
)
pause
goto menu

:end
exit /b 0