ARGS := $(filter-out $@,$(MAKEFLAGS))
test:
	poetry run pytest -rP 

lint:
	poetry run flake8 --show-source

format:
	poetry run black --diff .

clean:
	find . -type d -name '__pycache__' -exec rm -rf {} +

build:
	docker build --tag xls2csv .

run:
	docker run -v ~/Downloads/Banks:/inout xls2csv $(ARGS)

runLocal:
	poetry run python xls2csv/xls2csv.py ~/Downloads/Banks

manual-test:
	TEST_MODE=true
	poetry run python xls2csv/xls2csv.py manual_test
