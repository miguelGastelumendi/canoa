#!/bin/bash
echo *********************************************************
echo Para usar esse bash ele deve ser adaptado para a máquina,
echo alterando para a estrutura de diretórios adequada.
echo
echo A variável de ambiente SQLALCHEMY_DATABASE_URI deve estar
echo definida.
echo *********************************************************
echo
cd rurallegal/
source venv/bin/activate
cd utils/sp_comp/
python spComp.py
