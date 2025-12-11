pipeline {
    agent any

    environment {
        // Just a helper var; we still call venv directly
        PY_VENV = "venv"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python venv & deps') {
            steps {
                sh '''
                    # Create virtualenv if not exists
                    if [ ! -d "venv" ]; then
                      python3 -m venv venv
                    fi

                    # Activate venv and install deps
                    . venv/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Docker Compose Up') {
            steps {
                sh '''
                    # Ensure Docker CLI is in PATH for Jenkins
                    export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"

                    echo "[INFO] Bringing down any existing stack..."
                    docker compose down || true

                    echo "[INFO] Starting microservices stack..."
                    docker compose up -d

                    echo "[INFO] Waiting for services to be ready..."
                    sleep 10
                '''
            }
        }

        stage('Run PyTest BDD API Flow') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest tests/steps -v
                '''
            }
        }
        
	 stage('Run k6 Load Test') {
            steps {
                sh '''
                    # Ensure Docker CLI is available
                    export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"

                    echo "[INFO] Running k6 smoke test against Docker services..."

                    docker run --rm \
                      --network microservices-checkout-quality-gate_default \
                      -v "$PWD/load_tests":/scripts \
                      grafana/k6 run /scripts/checkout-smoke.js
                '''
            }
        }

        stage('Run Newman API Smoke Tests') {
            steps {
                sh '''
                    # Try to locate newman (global npm install)
                    export PATH="/usr/local/bin:/opt/homebrew/bin:$HOME/.npm-global/bin:$HOME/.npm-packages/bin:$PATH"

                    echo "[INFO] Using PATH: $PATH"
                    if ! command -v newman >/dev/null 2>&1; then
                      echo "[ERROR] Newman CLI not found in PATH."
                      echo "Install it with: npm install -g newman"
                      exit 1
                    fi

                    newman -v

                    newman run postman/checkout-microservices.postman_collection.json \
                      -e postman/test-environment.postman_environment.json
                '''
            }
        }

        stage('Run Selenium UI Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest tests/selenium -v
                '''
            }
        }
    }

    post {
        always {
            sh '''
                # Ensure Docker CLI in PATH
                export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"

                echo "[INFO] Tearing down Docker stack..."
                docker compose down || true
            '''
        }
    }
}

