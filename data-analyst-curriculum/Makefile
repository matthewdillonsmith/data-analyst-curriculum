.PHONY: generate generate-medium api docker-api clean

generate:
	python -m generators.generate_all --scale small

generate-medium:
	python -m generators.generate_all --scale medium

api:
	uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

docker-api:
	docker compose up --build

clean:
	rm -rf datasets/01_* datasets/02_* datasets/03_* datasets/04_* datasets/05_* datasets/06_* datasets/07_*
