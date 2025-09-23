# Cyngn Interview Prep - Full Stack Makefile

# Default target - complete setup
default: build-backend build-frontend
	@echo ""
	@echo "Setup complete! Backend and frontend ready."
	@echo ""
	@echo "To start development servers:"
	@echo "  Terminal 1: make run"
	@echo "  Terminal 2: make react"
	@echo ""

populate: backend/member.db
	sqlite3 backend/member.db "DELETE FROM member;"
	sqlite3 backend/member.db < backend/populate.sql

# Build backend with dependency checking and error handling
build-backend:
	@echo "Setting up backend..."
	@if [ ! -d "backend/venv" ]; then \
		echo "Creating virtual environment..."; \
		cd backend && python3 -m venv venv > /dev/null 2>&1 || (echo "Failed to create virtual environment" && exit 1); \
	fi
	@echo "Installing Python dependencies..."
	@cd backend && source venv/bin/activate && pip install -r requirements.txt > /tmp/pip-install.log 2>&1 && \
		echo "Python dependencies installed" || \
		(echo "Python dependency installation failed. Check /tmp/pip-install.log for details" && cat /tmp/pip-install.log | tail -10 && exit 1)
	@cd backend && sqlite3 member.db < schema.sql
	@echo "Backend setup complete"

# Build frontend with dependency checking and error handling
build-frontend:
	@echo "Setting up frontend..."
	@if [ ! -d "frontend/node_modules" ]; then \
		echo "Installing Node.js dependencies..."; \
		cd frontend && npm install > /tmp/npm-install.log 2>&1 && \
			echo "Node.js dependencies installed" || \
			(echo "Node.js dependency installation failed. Check /tmp/npm-install.log for details" && cat /tmp/npm-install.log | tail -10 && exit 1); \
	else \
		echo "Node.js dependencies already installed"; \
	fi
	@echo "Frontend setup complete"

# Run Flask backend server
run:
	@echo "Starting Flask backend server at http://localhost:5000"
	cd backend && source venv/bin/activate && python src/app.py

# Run React frontend server
react:
	@echo "Starting React frontend server at http://localhost:5173"
	cd frontend && npm run dev

# Alternative names for clarity
run-backend: run
run-frontend: react

# Testing
test-backend:
	cd backend && source venv/bin/activate && PYTHONPATH=src pytest tests/

test: test-backend
	@echo "Backend tests complete. Frontend tests not configured yet."

# Database tools
db-view:
	cd backend && sqlite3 -header -column member.db "SELECT * FROM member;"

db-shell:
	cd backend && sqlite3 member.db

# Cleanup
clean:
	@echo "Cleaning up build artifacts..."
	rm -rf backend/venv/
	rm -rf frontend/node_modules/
	rm -f /tmp/pip-install.log /tmp/npm-install.log
	@echo "Clean complete"

clean-db:
	rm -f backend/member.db

full-clean: clean clean-db
	@echo "Full clean complete"

# Development helpers
backend-shell:
	cd backend && source venv/bin/activate && bash

# Show detailed logs from last install
show-logs:
	@echo "=== Python install log ==="
	@cat /tmp/pip-install.log 2>/dev/null || echo "No Python install log found"
	@echo ""
	@echo "=== Node.js install log ==="
	@cat /tmp/npm-install.log 2>/dev/null || echo "No Node.js install log found"

# Show clean project structure
tree:
	tree -I 'node_modules|venv|__pycache__|*.pyc|*.db'

# Show help
help:
	@echo "Available targets:"
	@echo "  (default)       - Complete setup: build backend and frontend"
	@echo "  run             - Start Flask backend server"
	@echo "  react           - Start React frontend server"
	@echo "  test            - Run backend tests"
	@echo "  db-view         - View all database records"
	@echo "  db-shell        - Open interactive database shell"
	@echo "  clean           - Remove venv and node_modules"
	@echo "  clean-db        - Delete database file"
	@echo "  full-clean      - Remove everything (venv, node_modules, database)"
	@echo "  show-logs       - View detailed installation logs"
	@echo "  backend-shell   - Open shell with Python venv activated"
	@echo "  tree            - Draw relevant directory structure"
	@echo "  help            - Show this help message"