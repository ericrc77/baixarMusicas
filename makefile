setup:
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	cp .env.example .env || copy .env.example .env

run:
	python main.py

test:
	pytest tests/

selftest:
	python -m app --selftest
