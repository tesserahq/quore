# Estate Buddy API

## Generate migrations

`poetry run alembic revision --autogenerate -m "create servers table"`

## Run migrations

* dev: `poetry run alembic upgrade head`

* test: `ENV=test poetry run alembic upgrade head`

## Run server

`poetry run dev`

## Build the image

`docker build -t quore .`

Run the API

`docker run --rm -p 8000:8000 quore`

## Run with a host volume

`docker run -v $(pwd)/data:/app/data -p 8000:8000 mcp-api`
