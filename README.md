# Lainonima

[![Travis](https://travis-ci.org/vitorbaptista/lainonima.svg?branch=master)](https://travis-ci.org/vitorbaptista/lainonima)

## Instalando

```
virtualenv --no-site-packages env
. env/bin/activate
pip install -r requirements.txt
```

## Executando

1. Execute as database migrations com `python manage.py migrate`
1. Crie um superusuário com `python manage.py createsuperuser`
1. Rode o servidor com `python manage.py runserver`

A partir desse momento, você já pode acessar o projeto em
[http://localhost:8000](http://localhost:8000). Para enviar um pedido, você
precisa ter algum `PublicBody` cadastrado no banco de dados. A forma mais fácil
de cadastrar é pela tela de administração em
[http://localhost:8000/admin](http://localhost:8000/admin)


## Rodando testes

```
pip install tox
tox
```
