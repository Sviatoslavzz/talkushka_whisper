
.PHONY: uninstall_all_dependencies

install:
	pip install -e . -U

install_dev:
	pip install -e .[dev,test] -U

uninstall_all_dependencies:
	pip freeze | grep -v '^-e' | xargs pip uninstall -y
	pip cache purge

#test:
#	pytest tests/

lint:
	ruff check .
	ruff format . --check

format:
	ruff check . --fix
	ruff format .

clean:
	rm -rf src/*.egg-info *.egg_info __pycache__ build/
	@echo "🧹🧹🧹 perfect"
