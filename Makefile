watch-sass:
	watchmedo shell-command --patterns="*.scss" --recursive --command 'sassc web/static/web/styles/main.scss web/static/web/styles/main.css --sourcemap' web/static/web/styles

sass:
	sassc web/static/web/styles/main.scss web/static/web/styles/main.css --sourcemap

encode_gcloud_credentials:
	@python3 -c 'import base64; creds = open("$(path)", "rb").read(); print(base64.b64encode(creds).decode("utf-8"))'
