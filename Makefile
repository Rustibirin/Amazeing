# Variables
NAME    = a_maze_ing.py
CONFIG  = config.txt
VENV    = .venv
PYTHON  = $(VENV)/bin/python3
PIP     = $(VENV)/bin/pip

# Output colors
BLUE    = \033[1;34m
ORANGE  = \033[1;31m
PURPLE  = \033[1;35m
GREEN   = \033[22;38;5;46m
RESET   = \033[0m

# Rules
.PHONY: all
all: install

$(VENV):
	@echo "$(ORANGE)Creating Python virtual environment...$(GREEN)"
	@python3 -m venv $(VENV)
	@echo "$(ORANGE)Installing development tools (flake8, mypy)...$(GREEN)"
	@$(PIP) install --upgrade pip
	@$(PIP) install -q -r requirements.txt
	@echo "$(PURPLE)Environment ready. Now you can run $(BLUE)'make run' $(PURPLE)or $(BLUE)'make lint'...$(RESET)"

.PHONY: install
install: $(VENV)

.PHONY: run
run: $(VENV)
	$(PYTHON) $(NAME) $(CONFIG)

.PHONY: debug
debug: $(VENV)
	$(PYTHON) -m pdb $(NAME) $(CONFIG)

.PHONY: clean
clean:
	@echo "$(ORANGE)Cleaning cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .mypy_cache
	@rm -rf .pytest_cache
	@rm -rf *.egg-info
	@rm -rf build dist
	@rm -rf maze.txt
	@echo "$(PURPLE)Cleanup completed.$(RESET)"

.PHONY: fclean
fclean: clean
	@rm -rf $(VENV)
	@echo "$(ORANGE)Removing virtual environment..."
	@echo "$(PURPLE)Virtual environment removed.$(RESET)"

.PHONY: re
re: fclean all

.PHONY: lint
lint: $(VENV)
	@echo "$(ORANGE)Running flake8..."
	@$(VENV)/bin/flake8 . --exclude=.venv
	@echo "$(ORANGE)Running mypy..."
	@$(VENV)/bin/mypy . --exclude=.venv
	@echo "$(PURPLE)Code is clean!$(RESET)"

.PHONY: lint-strict
lint-strict: $(VENV)
	@echo "$(ORANGE)Running flake8..."
	@$(VENV)/bin/flake8 . --exclude=.venv
	@echo "$(ORANGE)Running mypy --strict..."
	@$(VENV)/bin/mypy . --exclude=.venv --strict
	@echo "$(PURPLE)Code is perfect!$(RESET)"

.PHONY: test
test: $(VENV)
	@echo "$(ORANGE)Running unit tests...$(GREEN)"
	@PYTHONPATH=. $(VENV)/bin/pytest tests/ -v
	@echo "$(PURPLE)Tests completed.$(RESET)"