.PHONY: install dev test lint demo web clean

install:
	pip install -e .

dev:
	pip install -e ".[dev,web]"

test:
	pytest -q

lint:
	ruff check .

demo:
	python examples/synthetic_demo.py --gif assets/demo.gif --report assets/sample_report.json

web:
	streamlit run src/formfit/app/streamlit_app.py

clean:
	rm -rf build dist *.egg-info .pytest_cache demo.mp4 report.json
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
