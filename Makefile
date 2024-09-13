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

install:
	poetry install --no-root
	poetry run pre-commit install

test:
	poetry run pytest
	poetry run pre-commit run --all-files

watch_sass: sass
	poetry run watchmedo shell-command --patterns="*.scss" --recursive --command 'make sass' web/static/web/styles

sass:
	poetry run pysassc web/static/web/styles/main.scss web/static/web/styles/main.css --sourcemap

load_fixtures:
	poetry run python manage.py loaddata public_bodies_and_esics sample_foi_requests

migrate:
	poetry run python manage.py migrate

server:
	poetry run honcho -f Procfile.dev start

create_admin:
	poetry run python manage.py createsuperuser

make_translations:
	poetry run django-admin makemessages --all --ignore "env*"

compile_translations:
	# FIXME: This will compile all .po files in the current folder, including in
	# `.tox` and `env`
	poetry run django-admin compilemessages

poetry.lock:
	@if [ ! -f $@ ]; then \
		echo "Error: $@ does not exist. Please generate it externally."; \
		exit 1; \
	fi

# Esse arquivo é necessário pro DigitalOcean Apps detectar que é Python
requirements.txt: poetry.lock
	poetry export --format=requirements.txt > $@
