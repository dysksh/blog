.PHONY: up down build serve clean claude

up:
	USER_UID=$$(id -u) USER_GID=$$(id -g) DEV_HOME=$$([ "$$(id -u)" = "0" ] && echo /root || echo /home/dev) \
	docker compose up -d --build

down:
	docker compose down --remove-orphans || true

build:
	docker compose exec blog python scripts/build.py

serve:
	make build
	@echo "Serving at http://localhost:8000 — press Ctrl+C to stop"
	docker compose exec blog python -m http.server 8000 -d public; make clean

clean:
	docker compose exec blog rm -rf public

claude:
	docker compose exec claude claude
