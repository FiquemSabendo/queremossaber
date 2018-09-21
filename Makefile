.PHONY: help watch_sass sass encode_gcloud_credentials load_fixtures migrate server create_admin

help:
	@echo 'create_admin: create a superuser (admin)'
	@echo 'encode_gcloud_credentials'
	@echo 'load_fixtures: load database fixtures'
	@echo 'migrate: migrate database'
	@echo 'sass: compile styles'
	@echo 'server: start server'
	@echo 'watch_sass: watch changes and compile'

watch_sass: sass
	watchmedo shell-command --patterns="*.scss" --recursive --command 'make sass' web/static/web/styles

sass:
	sassc web/static/web/styles/main.scss web/static/web/styles/main.css --sourcemap

encode_gcloud_credentials:
	@python3 -c 'import base64; creds = open("$(path)", "rb").read(); print(base64.b64encode(creds).decode("utf-8"))'

load_fixtures:
	python manage.py loaddata public_bodies_and_esics sample_foi_requests

migrate:
	python manage.py migrate

server:
	honcho -f Procfile.dev start

create_admin:
	python manage.py createsuperuser
