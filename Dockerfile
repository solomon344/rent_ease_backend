FROM astral/uv:python3.12-bookworm-slim


WORKDIR /app

COPY . .

RUN uv sync

RUN uv run manage.py collectstatic --noinput

RUN uv run manage.py migrate

ENV settings="rent_ease_backend.settings"

EXPOSE 8000

CMD ["gunicorn", "rent_ease_backend.wsgi", "--bind", "0.0.0.0:8000"]