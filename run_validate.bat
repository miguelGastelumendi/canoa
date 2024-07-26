Rem Batch to run data_validate FROM `canoa`
@Echo Off
Rem mgd 2024-05-27 v1
Rem Example:
Rem D:\Projects\AdaptaBrasil\data_valdate\run.bat --input_folder D:\Projects\AdaptaBrasil\data_tunnel\00212\data --output_folder D:\Projects\AdaptaBrasil\data_tunnel\00212\report --no-spellchecker
Rem Save the current directory
pushd .
Rem Go to data_validate folder (/d including other drive)
cd /d "%~dp0"
Echo Activating data_validate enviromnent...
call .venv\Scripts\activate.bat
Rem TODO: check if activated
Echo Running data_validate...
Rem Check if .env is active, if not END
call python main.py %*
Echo Deactivating data_validate enviromnent...
call .venv\Scripts\deactivate.bat
popd .
Echo Returnnig to Canoa
Rem eof