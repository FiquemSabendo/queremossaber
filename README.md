# Lainonima

[![Travis](https://travis-ci.org/vitorbaptista/lainonima.svg?branch=master)](https://travis-ci.org/vitorbaptista/lainonima)

## Instalando

```
virtualenv --no-site-packages env
. env/bin/activate
pip install -r requirements.txt
```

## Executando

1. Copie o `.env.example` para `.env` e altere as configurações (no mínimo, o
   `DATABASE_URL`)
1. Execute as database migrations com `python manage.py migrate`
1. Crie um superusuário com `python manage.py createsuperuser`
1. Execute `make watch-sass` em um terminal separado, para compilar o SASS para
   CSS
1. Rode o servidor com `python manage.py runserver`

A partir desse momento, você já pode acessar o projeto em
[http://localhost:8000](http://localhost:8000). Para enviar um pedido, você
precisa ter algum `PublicBody` cadastrado no banco de dados. A forma mais fácil
é cadastrar as fixtures executando `python manage.py loaddata
load_public_bodies_and_esic`.

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
