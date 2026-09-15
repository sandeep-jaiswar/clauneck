.PHONY: help build test run clean

help:
	@echo "Clauneck Scientific Prototyping Platform"
	@echo ""
	@echo "Available targets:"
	@echo "  make build          Build all modules (Java + Python)"
	@echo "  make test           Run all tests (Java + Python)"
	@echo "  make run            Start services (engine + web spring boot)"
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
	gradle clean
	cd engine && rm -rf build dist *.egg-info __pycache__ .pytest_cache || true
	@echo "✓ Clean complete"

# Java / Gradle targets
core-build:
	@echo "Building core module..."
	gradle :core:build

core-test:
	@echo "Testing core module..."
	gradle :core:test

# Python engine targets
engine-build:
	@echo "Building Python engine..."
	cd engine && python -m pip install -e . > /dev/null 2>&1
	@echo "✓ Engine installed"

engine-test:
	@echo "Testing Python engine..."
	cd engine && python -m pip install -e ".[dev]" > /dev/null 2>&1
	cd engine && python -m pytest tests/ -v

# Run targets
run: engine-run-bg
	@echo "Clauneck services running:"
	@echo "  Engine: http://localhost:8001/docs (Swagger UI)"
	@echo "  Web:    http://localhost:8080 (coming soon)"
	@sleep 2 && curl -s http://localhost:8001/health | python -m json.tool || echo "Engine starting..."

engine-run-bg:
	@echo "Starting Python engine (background)..."
	cd engine && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 > /tmp/engine.log 2>&1 &
	@sleep 1
	@echo "✓ Engine started (PID logged)"

.DEFAULT_GOAL := help
