# Pedidos Anônimos

[![Travis](https://travis-ci.org/okfn-brasil/pedidosanonimos.svg?branch=master)](https://travis-ci.org/okfn-brasil/pedidosanonimos)

Plataforma que permite o envio de pedidos anônimos pela Lei de Acesso à
Informação.

## Instalando

```
virtualenv --no-site-packages env
. env/bin/activate
pip install -r requirements.txt
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

## Pedidos de exemplo

Quando você carrega as fixtures no seu banco de dados, os seguintes pedidos de exemplo são criados:

* Rejeitado em moderação: SL6F4L46
* Aprovado mas não enviado: H4BRYOXF
* Respondido com um PDF: HQCYR6KQ
* Aguardando resposta atrasada do órgão público: GQ2XOQM7

## Configurando uploads para Google Cloud

Durante desenvolvimento, os arquivos enviados são salvos no filesystem local.
Em produção, usamos o Google Cloud Storage. Para habilitá-lo, precisamos do
JSON com as credenciais do GCloud. Como usamos o Heroku para deploy, não
podemos apontar diretamente para o arquivo (o filesystem do Heroku é efêmero).
Ao invés disso, codificamos esse JSON em base64 e o colocamos na variável
`GS_APPLICATION_CREDENTIALS_BASE64`.

Considerando que suas credenciais estejam em `gcloud-credentials.json`, execute:

`make encode_gcloud_credentials path=gcloud-credentials.json`

Esse comando irá retornar o arquivo codificado em base64, daí basta alterar as
variáveis de ambiente no arquivo `.env`:

1. `GS_APPLICATION_CREDENTIALS_BASE64` com o conteúdo do comando anterior
1. `ENABLE_GCLOUD=True`
1. Configure o nome do seu bucket em `GS_BUCKET_NAME`

Reinicie o servidor Django, e os próximos arquivos enviados já irão para o
GCloud.

## Rodando testes

```
pip install tox
tox
```
