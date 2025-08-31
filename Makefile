# Makefile for Advanced Prompt Engineering Tool

# Variables
PYTHON := python3
PIP := pip3
STREAMLIT := streamlit
APP := app.py
PORT := 8501

# Colors for terminal output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

.PHONY: help install run dev docker-build docker-run docker-stop clean test lint format setup

help: ## Show this help message
	@echo '$(GREEN)Advanced Prompt Engineering Tool - Makefile$(NC)'
	@echo ''
	@echo 'Usage:'
	@echo '  $(YELLOW)make$(NC) $(GREEN)<target>$(NC)'
	@echo ''
	@echo 'Targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

install: ## Install dependencies
	@echo "$(GREEN)Installing dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)Dependencies installed successfully!$(NC)"

setup: ## Initial setup (install deps + create directories)
	@echo "$(GREEN)Setting up project...$(NC)"
	$(MAKE) install
	mkdir -p .streamlit
	mkdir -p data
	mkdir -p logs
	cp .env.example .env 2>/dev/null || true
	@echo "$(GREEN)Setup complete! Edit .env file with your API keys$(NC)"

run: ## Run the Streamlit app
	@echo "$(GREEN)Starting Streamlit app on port $(PORT)...$(NC)"
	$(STREAMLIT) run $(APP) --server.port=$(PORT)

dev: ## Run in development mode with auto-reload
	@echo "$(GREEN)Starting in development mode...$(NC)"
	$(STREAMLIT) run $(APP) --server.runOnSave=true --server.port=$(PORT)

docker-build: ## Build Docker image
	@echo "$(GREEN)Building Docker image...$(NC)"
	docker build -t prompt-engineering-tool .
	@echo "$(GREEN)Docker image built successfully!$(NC)"

docker-run: ## Run with Docker
	@echo "$(GREEN)Starting Docker container...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)Container started! Access at http://localhost:$(PORT)$(NC)"

docker-stop: ## Stop Docker container
	@echo "$(YELLOW)Stopping Docker container...$(NC)"
	docker-compose down
	@echo "$(GREEN)Container stopped!$(NC)"

docker-logs: ## View Docker logs
	docker-compose logs -f

clean: ## Clean cache and temporary files
	@echo "$(YELLOW)Cleaning cache and temporary files...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	@echo "$(GREEN)Cleanup complete!$(NC)"

test: ## Run tests (if implemented)
	@echo "$(GREEN)Running tests...$(NC)"
	$(PYTHON) -m pytest tests/ -v
	@echo "$(GREEN)Tests complete!$(NC)"

lint: ## Run code linting
	@echo "$(GREEN)Running linting...$(NC)"
	$(PYTHON) -m flake8 $(APP) --max-line-length=120
	$(PYTHON) -m pylint $(APP)
	@echo "$(GREEN)Linting complete!$(NC)"

format: ## Format code with black
	@echo "$(GREEN)Formatting code...$(NC)"
	$(PYTHON) -m black $(APP)
	@echo "$(GREEN)Code formatted!$(NC)"

check-env: ## Check if environment variables are set
	@echo "$(GREEN)Checking environment variables...$(NC)"
	@if [ -f .env ]; then \
		echo "$(GREEN).env file found$(NC)"; \
		grep -E "^[A-Z_]+=" .env | while read line; do \
			key=$$(echo $$line | cut -d'=' -f1); \
			value=$$(echo $$line | cut -d'=' -f2); \
			if [ -z "$$value" ] || [ "$$value" = "your-*" ]; then \
				echo "$(RED)❌ $$key is not set$(NC)"; \
			else \
				echo "$(GREEN)✓ $$key is configured$(NC)"; \
			fi \
		done; \
	else \
		echo "$(RED).env file not found! Copy .env.example to .env$(NC)"; \
	fi

deploy-streamlit: ## Deploy to Streamlit Cloud
	@echo "$(GREEN)Preparing for Streamlit Cloud deployment...$(NC)"
	@echo "$(YELLOW)Steps to deploy:$(NC)"
	@echo "1. Push your code to GitHub"
	@echo "2. Go to https://share.streamlit.io"
	@echo "3. Connect your GitHub repository"
	@echo "4. Set up secrets in Streamlit Cloud dashboard"
	@echo "5. Click Deploy!"

deploy-heroku: ## Deploy to Heroku
	@echo "$(GREEN)Deploying to Heroku...$(NC)"
	heroku create
	git push heroku main
	heroku open
	@echo "$(GREEN)Deployment complete!$(NC)"

logs: ## View application logs
	@echo "$(GREEN)Viewing logs...$(NC)"
	tail -f logs/*.log 2>/dev/null || echo "$(YELLOW)No logs found$(NC)"

update: ## Update dependencies
	@echo "$(GREEN)Updating dependencies...$(NC)"
	$(PIP) install --upgrade -r requirements.txt
	@echo "$(GREEN)Dependencies updated!$(NC)"

version: ## Show version information
	@echo "$(GREEN)Version Information:$(NC)"
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Pip: $$($(PIP) --version)"
	@echo "Streamlit: $$($(STREAMLIT) --version)"

# Default target
.DEFAULT_GOAL := help