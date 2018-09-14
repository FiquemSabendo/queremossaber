watch_sass:
	make sass  # Ensure we have compiled the latest SASS files
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
	python manage.py runserver

create_admin:
	python manage.py createsuperuser

help:
	@echo 'create_admin: create a superuser (admin)'
	@echo 'encode_gcloud_credentials'
	@echo 'load_fixtures: load database fixtures'
	@echo 'migrate: migrate database'
	@echo 'sass: compile styles'
	@echo 'server: start server'
	@echo 'watch_sass: watch changes and compile'
