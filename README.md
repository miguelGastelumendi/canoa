<!--
   /* cSpell:locale en pt-br
   /* cSpell:ignore sendgrid sqlalchemy
   /* mgd 2024-05-03
-->
# — Canoa _Frontend_ de AdaptaBrasil —


## Processo de Validação

A validação de um arquivo para um esquema é realizado em ```.private.upload_file.process``` e consta
dos seguintes módulos:

   1. check
      - Validar existência de variáveis e de arquivos necessários para o processo;
      - Verificar a existência das pastas do processo ou criar caso não existam;
      - CBE: 200 (ver: ```.helpers.error_helper.py```): ```UPLOAD_FILE_CHECK = 200```
   2. register
   2. unzip
   3. submit
   3. email



## Variáveis de Ambiente

Para manter a privacidade e a segurança das informações confidenciais, são usadas
variáveis de ambiente (`envvars` [_Environment Variables_](https://en.wikipedia.org/wiki/Environment_variable)). As principais são:

- `CANOA_APP_MODE` seleciona o modo da aplicação, selecionando configurações diferentes. Atualmente temos `Production` e `Debug`.
  Para maiores detalhes e novas configurações ver o módulo `./config.py`.
- `CANOA_DEBUG` configura o modo da aplicação: `False` ou `True`. Para ativar o modo depuração em Flask, deve usar
    [`FLASK_DEBUG`](https://flask.palletsprojects.com/en/latest/config/#DEBUG);
- `CANOA_EMAIL_API_KEY` A chave da API para o envio de e-mails (o app usa [sendgrid](https://sendgrid.com/));
- `CANOA_EMAIL_ORIGINATOR` O endereço de e-mail do remetente, quem envia correios em nome de Canoa e está registrado na API de envio;
- `CANOA_SERVER_ADDRESS` O endereço do servidor da aplicação (ver ```main.py```);
- `CANOA_SQLALCHEMY_DATABASE_URI` O URI do banco de dados que deve ser usado para a conexão usando
    [Flask&minus;SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/latest/config);

Qualquer atributo da configuração base (`BaseConfig` em  `.config.py`) pode ser configurado por meio de uma envvar.
Basta adicionar o nome do atributo antecedido com CANOA na lista (ver ```.config.get_os_env```)

É possível atribuir um valor fixo para a envvar [`SECRET_KEY`](https://flask.palletsprojects.com/en/latest/config/#SECRET_KEY),
mas se é deixado em branco, o sistema gerara um nova valor a cada variação da versão do aplicativo.




