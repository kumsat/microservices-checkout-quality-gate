.PHONY: up down test-bdd test-ui test-all load zap ci-local

up:
	@echo "Starting Docker stack..."
	docker compose up -d

down:
	@echo "Stopping Docker stack..."
	docker compose down

test-bdd:
	@echo "Running PyTest BDD tests..."
	source venv/bin/activate && pytest tests/steps -v

test-ui:
	@echo "Running Selenium UI tests..."
	source venv/bin/activate && pytest tests/selenium -v

test-all: test-bdd test-ui

load:
	@echo "Running k6 load tests..."
	docker run --rm \
	  --network microservices-checkout-quality-gate_default \
	  -v "$$PWD/load_tests":/scripts \
	  grafana/k6 run /scripts/checkout-smoke.js

zap:
	@echo "Running OWASP ZAP baseline scan..."
	mkdir -p security/zap_reports
	docker run --rm \
	  --network microservices-checkout-quality-gate_default \
	  -v "$$PWD/security/zap_reports":/zap/wrk \
	  owasp/zap2docker-stable zap-baseline.py \
	    -t http://ui-service:5006 \
	    -r zap-baseline-report.html

ci-local: up test-bdd load zap test-ui down

