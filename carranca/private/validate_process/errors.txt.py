"""
    erros.txt
    Upload Files Process
    This is a list of errors texts that the user can correct,
    e enviar de novo.
    If is changed, update db.canoa.ui_items[secError, upload_files]
    The format is Json, it's here for quick reference

    The extension is py, in order to have syntax highlighting and error check
"""
erros = {
    'check':
        {
            '5': 'O arquivo deve estar en formato zip e ter extensão .zip',
            '7': 'O nome do arquivo deve ser menor que 50 caracteres.',
            '8': 'O arquivo deve estar en formato zip e ter extensão .zip',
         },
    'register': {},
    'unzip': {},
    'submit': {},
    'email': {}
}



