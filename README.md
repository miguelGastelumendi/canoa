<!--
   /* cSpell:locale en pt-br
   /* cSpell:ignore sendgrid sqlalchemy
   /* mgd 2024-05-03
-->
# — Canoa _Frontend_ de AdaptaBrasil —


## Variáveis de Ambiente

Para manter a privacidade e a segurança das informações confidenciais, são usadas
variáveis de ambiente (`envvars` [_Environment Variables_](https://en.wikipedia.org/wiki/Environment_variable)). As principais são:

- `CANOA_APP_MODE` seleciona o modo da aplicação, selecionando configurações diferentes. Atualmente temos `Production` e `Debug`.
  Para maiores detalhes e novas configurações ver o módulo `./config.py`.
- `CANOA_DEBUG` configura o modo da aplicação: `False` ou `True`. Para ativar o modo depuração em Flask, deve usar
    [`FLASK_DEBUG`](https://flask.palletsprojects.com/en/latest/config/#DEBUG);
- `CANOA_EMAIL_API_KEY` A chave da API para o envio de e-mails (é usado [sendgrid](https://sendgrid.com/));
- `CANOA_EMAIL_ORIGINATOR` O endereço de e-mail do remetente, quem envia correios em nome de Canoa e está registrado na API de envio;
- `CANOA_SQLALCHEMY_DATABASE_URI` O URI do banco de dados que deve ser usado para a conexão usando
    [Flask&minus;SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/latest/config);

Qualquer atributo da configuração base (`BaseConfig` em  `./config.py`) pode ser configurado por meio de uma envvar.
Basta adicionar o nome do atributo antecedido com CANOA na lista.

É possível atribuir um valor fixo para a envvar [`SECRET_KEY`](https://flask.palletsprojects.com/en/latest/config/#SECRET_KEY),
mas se é deixado em branco, o sistema gerara um nova valor a cada variação da versão do aplicativo.



