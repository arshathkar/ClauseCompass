.PHONY: dev demo lint typecheck test e2e a11y eval audit size doctor record-fixtures ci-e2e help

# Default target
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Development ──────────────────────────────────────────────────────────────

dev: ## Start backend + frontend in replay mode (no API key needed)
	@echo "Starting ClauseCompass in replay mode..."
	@cp -n .env.example .env 2>/dev/null || true
	$(MAKE) -j2 dev-backend dev-frontend

dev-backend:
	cd backend && python -m uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

demo: ## Production-like local build in replay mode
	@echo "Starting ClauseCompass demo..."
	@cp -n .env.example .env 2>/dev/null || true
	@LLM_MODE=replay $(MAKE) -j2 dev-backend dev-frontend

# ── Quality ──────────────────────────────────────────────────────────────────

lint: ## Lint backend (ruff) and frontend (eslint)
	cd backend && python -m ruff check . && python -m ruff format --check .
	cd frontend && npm run lint

typecheck: ## Type-check backend (mypy) and frontend (tsc)
	cd backend && python -m mypy --strict app
	cd frontend && npm run typecheck

test: ## Run unit + integration tests
	cd backend && python -m pytest --cov=app --cov-fail-under=80 -q
	cd frontend && npm run test -- --run

e2e: ## Playwright end-to-end tests (replay mode)
	cd frontend && npx playwright test

a11y: ## Accessibility tests (axe + Lighthouse)
	cd frontend && npx playwright test --grep @a11y
	python scripts/check_contrast.py

eval: ## Golden-set + red-team evals
	python scripts/run_evals.py --mode replay

ci-e2e: ## CI: start backend in replay mode + run Playwright
	@LLM_MODE=replay cd backend && python -m uvicorn app.main:app --port 8000 &
	@sleep 3
	cd frontend && npm run build && npx playwright test
	@kill %1 2>/dev/null || true

# ── Security & Compliance ────────────────────────────────────────────────────

audit: ## Security audits (pip-audit, npm audit, bandit, gitleaks)
	cd backend && pip-audit && python -m bandit -r app -q
	cd frontend && npm audit --audit-level=high
	gitleaks detect --source . -v

doctor: ## Probe all configured model IDs
	python scripts/doctor.py

# ── Data & Fixtures ──────────────────────────────────────────────────────────

record-fixtures: ## Record live LLM responses for synthetic samples
	python -m backend.app.llm.recording

# ── Repo Health ──────────────────────────────────────────────────────────────

size: ## Check repo size (< 8 MB)
	bash scripts/check_repo_size.sh

# ── Docker ───────────────────────────────────────────────────────────────────

docker-up: ## Start with Docker Compose
	docker-compose up --build

docker-down: ## Stop Docker Compose
	docker-compose down
