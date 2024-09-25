Rem Batch to run data_validate FROM `canoa`
@echo Off
Rem mgd 2024-05-27 v1
Rem mgd 2024-07-27 v2 (param1: data_validate folder)
Rem Example:
Rem D:\Projects\AdaptaBrasil\data_tunnel\run_validate.bat D:\Projects\AdaptaBrasil\data_valdate --input_folder D:\Projects\AdaptaBrasil\data_tunnel\00212\data --output_folder D:\Projects\AdaptaBrasil\data_tunnel\00212\report --no-spellchecker
Rem
Rem /!\ Keep synced with run_validate.sh
Rem --------------------------
Rem Go to data_validate folder [param1] (/d including the drive)
cd /d "%~1"
Rem Remove first param
shift
echo Activating data_validate environment...
call .venv\Scripts\activate.bat
Rem Check if .env is active, if not END
echo Running data_validate...
Rem %* does not "comply" with `shift`: call python main.py %*
call python main.py %1 %2 %3 %4 %5 %6 %7 %8 %9
echo Deactivating data_validate environment...
call .venv\Scripts\deactivate.bat
echo Returning to Canoa.
Rem eof