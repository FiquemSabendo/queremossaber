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


## Rodando testes

```
pip install tox
tox
```
