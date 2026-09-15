.PHONY: help build test run clean stop

help:
	@echo "Clauneck Scientific Prototyping Platform"
	@echo ""
	@echo "Available targets:"
	@echo "  make build          Build all modules (Java + Python)"
	@echo "  make test           Run all tests (Java + Python)"
	@echo "  make run            Start services (engine + web spring boot)"
	@echo "  make stop           Stop all running services"
	@echo "  make clean          Clean all build artifacts"
	@echo "  make engine-build   Build Python engine only"
	@echo "  make engine-test    Test Python engine only"
	@echo "  make core-build     Build Java core module only"
	@echo "  make core-test      Test Java core module only"

# Overall targets
build: core-build engine-build
	@echo "✓ All modules built successfully"

test: core-test engine-test
	@echo "✓ All tests passed"

clean:
	@echo "Cleaning all build artifacts..."
	./gradlew clean
	cd engine && rm -rf build dist *.egg-info __pycache__ .pytest_cache .venv || true
	@echo "✓ Clean complete"

# Java / Gradle targets
core-build:
	@echo "Building core module..."
	./gradlew :core:build

core-test:
	@echo "Testing core module..."
	./gradlew :core:test

# Python engine targets
engine-build:
	@echo "Building Python engine..."
	cd engine && python3 -m venv .venv 2>/dev/null || true
	cd engine && .venv/bin/python -m pip install --upgrade pip setuptools wheel > /dev/null 2>&1
	cd engine && .venv/bin/pip install -e . > /dev/null 2>&1
	@echo "✓ Engine installed"

engine-test:
	@echo "Testing Python engine..."
	cd engine && python3 -m venv .venv 2>/dev/null || true
	cd engine && .venv/bin/pip install -e ".[dev]" > /dev/null 2>&1
	cd engine && .venv/bin/pytest tests/ -v

# Run targets
run: engine-run-bg
	@echo "Clauneck services running:"
	@echo "  Engine: http://localhost:8001/docs (Swagger UI)"
	@echo "  Web:    http://localhost:8080 (coming soon)"
	@sleep 2 && curl -s http://localhost:8001/health | python3 -m json.tool || echo "Engine starting..."

engine-run-bg:
	@echo "Starting Python engine (background)..."
	cd engine && python3 -m venv .venv 2>/dev/null || true
	@mkdir -p .clauneck/run
	@cd engine; .venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 > /tmp/engine.log 2>&1 & echo $$! > ../.clauneck/run/engine.pid
	@sleep 1
	@echo "✓ Engine started (PID stored in .clauneck/run/engine.pid)"

# Stop targets
stop:
	@echo "Stopping all services..."
	@if test -f .clauneck/run/engine.pid && kill -0 "$$(cat .clauneck/run/engine.pid)" 2>/dev/null; then \
		kill "$$(cat .clauneck/run/engine.pid)" && echo "  Engine stopped"; \
	else echo "  Engine not running"; fi
	@rm -f .clauneck/run/engine.pid
	@if test -f .clauneck/run/web.pid && kill -0 "$$(cat .clauneck/run/web.pid)" 2>/dev/null; then \
		kill "$$(cat .clauneck/run/web.pid)" && echo "  Web server stopped"; \
	else echo "  Web server not running"; fi
	@rm -f .clauneck/run/web.pid
	@sleep 1
	@echo "✓ All services stopped"

.DEFAULT_GOAL := help
