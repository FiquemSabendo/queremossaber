watch-sass:
	watchmedo shell-command --patterns="*.scss" --recursive --command 'sassc web/static/web/styles/main.scss web/static/web/styles/main.css --sourcemap' web/static/web/styles
