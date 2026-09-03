
# Variables
NAME         = a_maze_ing.py
CONFIG       = config.txt
VENV         = .venv
PYTHON       = $(VENV)/bin/python3
PIP          = $(VENV)/bin/pip

# Output colors
BLUE = \033[1;32m
RED = \033[1;31m
YELLOW = \033[1;33m
RESET = \033[0m


# Rules
.PHONY: all
all: install

.PHONY: install
install: $(VENV)/bin/activate
	@echo "$(BLUE)Installing development tools (flake8, mypy)...$(RESET)"
	@$(PIP) install --upgrade pip
	@$(PIP) install flake8 mypy pytest
	@echo "$(RED)Environment ready. Now you can run $(BLUE)'make run' $(RED)or $(BLUE)'make lint'...$(RESET)"

$(VENV)/bin/activate:
	@echo "$(BLUE)Creating Python virtual environment...$(RESET)"
	@python3 -m venv $(VENV)

.PHONY: run
run:
	@if [ ! -d "$(VENV)" ]; then make install; fi
	$(PYTHON) $(NAME) $(CONFIG)

.PHONY: debug
debug:
	@if [ ! -d "$(VENV)" ]; then make install; fi
	$(PYTHON) -m pdb $(NAME) $(CONFIG)

.PHONY: clean
clean:
	@echo "$(BLUE)Cleaning cache files..."
	@rm -rf __pycache__
	@rm -rf .mypy_cache
	@rm -rf .pytest_cache
	@rm -rf *.egg-info
	@rm -rf build dist
	@echo "$(RED)Cleanup completed.$(RESET)"

.PHONY: fclean
fclean: clean
	@rm -rf $(VENV)
	@echo "$(RED)Virtual environment removed.$(RESET)"

.PHONY: lint
lint:
	@if [ ! -d "$(VENV)" ]; then make install; fi
	@echo "$(BLUE)Running flake8..."
	@$(VENV)/bin/flake8 . --exclude=.venv
	@echo "$(BLUE)Running mypy..."
	@$(VENV)/bin/mypy . --exclude=.venv --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
	@echo "$(RED)Code is clean!$(RESET)"

.PHONY: lint-strict
lint-strict:
	@if [ ! -d "$(VENV)" ]; then make install; fi
	@echo "$(BLUE)Running flake8..."
	@$(VENV)/bin/flake8 . --exclude=.venv
	@echo "$(BLUE)Running mypy --strict..."
	@$(VENV)/bin/mypy . --exclude=.venv --strict
	@echo "$(RED)Code is perfect!$(RESET)"

.PHONY: test
test:
	@if [ ! -d "$(VENV)" ]; then make install; fi
	@echo "$(BLUE)Running unit tests...$(RESET)"
	@PYTHONPATH=. $(VENV)/bin/pytest tests/ -v