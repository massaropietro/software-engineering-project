export COMPOSE_FILE := "docker-compose.local.yml"

# Default command to list all available commands.
default:
    @just --list

# build: Build python image.
build:
    @echo "Building python image..."
    @docker compose build

# up: Start up containers.
up *args:
    @echo "Starting up containers..."
    @docker compose up --remove-orphans {{ args }}

# down: Stop containers.
down:
    @echo "Stopping containers..."
    @docker compose down

# prune: Remove containers and their volumes.
prune *args:
    @echo "Killing containers and removing volumes..."
    @docker compose down -v {{ args }}

# logs: View container logs
logs *args:
    @docker compose logs -f {{ args }}

# manage: Executes `manage.py` command.
manage +args:
    @docker compose run --rm django python ./manage.py {{ args }}

# format: Formatta il codice backend (ruff)
format:
    @docker compose exec django sh -c "ruff check . --fix --unsafe-fixes && ruff format ."

# lint: Verifica lo stile del codice backend (ruff)
lint:
    @docker compose exec django sh -c "ruff check . && ruff format --check ."

# Esegui i test e genera subito il report HTML
test *args:
    @docker compose run --rm django sh -c "coverage run -m pytest {{ args }} && coverage html"

# makemessages: Genera o aggiorna i file di traduzione (.po)
makemessages:
    @docker compose run --rm django python manage.py makemessages -a

# compilemessages: Compila i file di traduzione (.mo)
compilemessages:
    @docker compose run --rm django python manage.py compilemessages
