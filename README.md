# Queremos Saber

[![Test](https://github.com/FiquemSabendo/queremossaber/actions/workflows/test.yml/badge.svg)](https://github.com/FiquemSabendo/queremossaber/actions/workflows/test.yml)

Plataforma que permite o envio de pedidos pela Lei de Acesso à
Informação sem revelar sua identidade.

## Instalando

Assumindo que você já tem o Python e [`uv`](https://docs.astral.sh/uv/) instalados, instale as dependências com:

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
Uma vez isso esteja configurado, para rodar os testes basta executar:

```
make test
```

## Pedidos de exemplo

Quando você carrega as fixtures no seu banco de dados, os seguintes pedidos de exemplo são criados:

* Rejeitado em moderação: SL6F4L46
* Aprovado mas não enviado: H4BRYOXF
* Respondido com um PDF: HQCYR6KQ
* Aguardando resposta atrasada do órgão público: GQ2XOQM7

## API para desenvolvedores

Sistemas externos podem criar pedidos de LAI programaticamente através da API
em `/api/`. Todo acesso exige um token, criado pelo admin do Django em
`Api > Api clients` (`/a/api/apiclient/add/`).

Envie o token no header `Authorization: Token <token>`.

### Buscar órgãos públicos

```
GET /api/public_bodies/?search=<termo>
```

Retorna até 20 órgãos cujo nome contenha `<termo>` (ou os 20 primeiros
cadastrados, se `search` for omitido), no formato:

```json
{"results": [{"id": 1, "name": "...", "level": "Local", "municipality": "...", "uf": "SP"}]}
```

### Criar um pedido

```
POST /api/foi_requests/
Content-Type: multipart/form-data
```

Campos:

* `receiver` (obrigatório): id do órgão público, obtido via `/api/public_bodies/`.
* `summary` (obrigatório): resumo curto do pedido.
* `body` (obrigatório, 55 a 2000 caracteres): texto do pedido.
* `attached_file` (opcional): arquivo a ser anexado (ex: imagem do mapa).
* `can_publish` (opcional, padrão `true`).
* `previous_protocol` (opcional): protocolo de um pedido anterior relacionado.

O pedido criado entra na mesma fila de moderação usada pelo formulário do
site — ele só é enviado ao órgão público depois de aprovado por um moderador.
Em caso de sucesso (`201`), a resposta é:

```json
{"protocol": "ABCDEFGH", "url": "https://queremossaber.org.br/p/ABCDEFGH/", "status": "pending"}
```

## Configurando uploads para Digital Ocean Spaces

Durante desenvolvimento, os arquivos enviados são salvos no filesystem local.
Em produção, usamos o Digital Ocean Spaces. Para habilitá-lo, configure as
variáveis que iniciam com `AWS_` no arquivo `.env` e adicione `ENABLE_S3=True`.
