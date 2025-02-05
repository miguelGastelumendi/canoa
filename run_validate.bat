Rem Batch to run data_validate FROM `canoa`
@echo Off
Rem cspell:ignore setlocal endlocal popd pushd venv py_args errorlevel enabledelayedexpansion
Rem mgd 2024-05-27 v1
Rem mgd 2024-07-27 v2 (param1: data_validate folder)
Rem mgd 2025-02-04 v3
Rem     %* does not "comply" with `shift`: call python main.py %*
Rem     1) save params in py_args, 2) setlocal 3) pushd/popd
Rem Example:
Rem D:\Projects\AdaptaBrasil\data_tunnel\run_validate.bat D:\Projects\AdaptaBrasil\data_validate --input_folder D:\Projects\AdaptaBrasil\data_tunnel\00212\data --output_folder D:\Projects\AdaptaBrasil\data_tunnel\00212\report --no-spellchecker
Rem
Rem /!\ Keep synced with run_validate.sh
Rem --------------------------
Rem Go to data_validate folder [param1]
pushd "%~1"
Rem Save params from 2 to n in py_args
set "py_args="
setlocal enabledelayedexpansion
Rem Loop to add args to py_args
:add_args
    shift
    if "%~1"=="" goto args_ready
    set "py_args=!py_args! %~1"
    goto add_args
:args_ready
endlocal & set "py_args=%py_args%"
echo %py_args%

if exist .venv\Scripts\activate.bat (
    echo Activating data_validate environment...
    call .venv\Scripts\activate.bat
) else (
    echo Virtual environment not found & exit /b 1
)

if not exist "main.py" (
    echo main.py not found in the current directory & exit /b 2
)
echo Running data_validate...
call python main.py %py_args%
set "exit_code=%ERRORLEVEL%"

echo Deactivating data_validate environment...
if exist .venv\Scripts\deactivate.bat (
    call .venv\Scripts\deactivate.bat
) else (
    echo Virtual environment deactivation script not found
)

popd
echo Returning to Canoa.
exit /b %exit_code%
Rem eof