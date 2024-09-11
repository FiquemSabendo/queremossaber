# Queremos Saber

[![Test](https://github.com/FiquemSabendo/queremossaber/actions/workflows/test.yml/badge.svg)](https://github.com/FiquemSabendo/queremossaber/actions/workflows/test.yml)

Plataforma que permite o envio de pedidos pela Lei de Acesso à
Informação sem revelar sua identidade.

## Instalando

Assumindo que você já tem o Python e `poetry` instalados, instale as dependências com:

```
make install
```

## Executando

1. Copie o `.env.example` para `.env` e altere as configurações (no mínimo, o
   `DATABASE_URL`)
1. Execute as database migrations com `make migrate`
1. Carregue as fixtures no seu banco de dados com `make load_fixtures`
1. Crie um superusuário com `make create_admin`
1. Execute `make watch_sass` em um terminal separado, para compilar o SASS para
   CSS
1. Rode o servidor com `make server`

A partir desse momento, você já pode acessar o projeto em
[http://localhost:8000](http://localhost:8000).

## Testes

Para rodar os testes, primeiro se certifique que seu usuário do postgres tenha
permissões para criar um banco de dados e executar comandos no banco de dados.

```
sudo -u postgres psql
ALTER ROLE queremossaber WITH CREATEDB;
```

Isso permitirá que ele crie o banco de dados de testes durante sua execução.

## Pedidos de exemplo

Quando você carrega as fixtures no seu banco de dados, os seguintes pedidos de exemplo são criados:

* Rejeitado em moderação: SL6F4L46
* Aprovado mas não enviado: H4BRYOXF
* Respondido com um PDF: HQCYR6KQ
* Aguardando resposta atrasada do órgão público: GQ2XOQM7

## Configurando uploads para Digital Ocean Spaces

Durante desenvolvimento, os arquivos enviados são salvos no filesystem local.
Em produção, usamos o Digital Ocean Spaces. Para habilitá-lo, configure as
variáveis que iniciam com `AWS_` no arquivo `.env` e adicione `ENABLE_S3=True`.

## Rodando testes

```
pip install tox
tox
```
