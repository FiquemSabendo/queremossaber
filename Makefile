.PHONY: install help watch_sass sass load_fixtures migrate server create_admin

help:
	@echo 'install: install dependencies'
	@echo 'test: run tests'
	@echo 'create_admin: create a superuser (admin)'
	@echo 'encode_gcloud_credentials'
	@echo 'load_fixtures: load database fixtures'
	@echo 'migrate: migrate database'
	@echo 'sass: compile styles'
	@echo 'server: start server'
	@echo 'watch_sass: watch changes and compile'
	@echo 'make_translations: regenerate translation files'
	@echo 'compile_translations: compile translation files'
	@echo 'setup_bucket_policy: applies bucket-policy.json policy to s3://queremosaber'

install:
	uv sync
	uv run prek install

test:
	uv run pytest
	uv run prek run --all-files

watch_sass: sass
	uv run watchmedo shell-command --patterns="*.scss" --recursive --command 'make sass' web/static/web/styles

sass:
	uv run pysassc web/static/web/styles/main.scss web/static/web/styles/main.css --sourcemap

load_fixtures:
	uv run python manage.py loaddata public_bodies_and_esics sample_foi_requests

migrate:
	uv run python manage.py migrate

server:
	uv run honcho -f Procfile.dev start

create_admin:
	uv run python manage.py createsuperuser

make_translations:
	uv run django-admin makemessages --all --ignore "env*"

compile_translations:
	# FIXME: This will compile all .po files in the current folder, including in
	# `.tox` and `env`
	uv run django-admin compilemessages

setup_bucket_policy:
	s3cmd setpolicy bucket-policy.json s3://queremossaber
