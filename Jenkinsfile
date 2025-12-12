pipeline {
    agent any

    environment {
        PATH = "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
        PYTHONPATH = "./"
    }

    stages {

        /* ---------------------------
        CHECKOUT CODE
        ----------------------------*/
        stage('Checkout') {
            steps {
                checkout scm
                echo "[INFO] Code checked out"
            }
        }

        /* ---------------------------
        SETUP PYTHON VENV
        ----------------------------*/
        stage('Setup Python venv') {
            steps {
                sh '''
                    if [ ! -d venv ]; then
                        python3 -m venv venv
                    fi
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        /* ---------------------------
        START DOCKER MICRO-SERVICES
        ----------------------------*/
        stage('Docker Compose Up') {
            steps {
                sh '''
                    echo "[INFO] Stopping running containers..."
                    docker compose down || true

                    echo "[INFO] Starting microservices..."
                    docker compose up -d

                    echo "[INFO] Waiting for services..."
                    sleep 15
                '''
            }
        }

        /* ---------------------------
        RUN PYTEST BDD API TESTS
        ----------------------------*/
        stage('Run PyTest BDD API Flow') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest tests/steps -v --junitxml=reports/pytest-results.xml
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/pytest-results.xml', fingerprint: true
                }
            }
        }

        /* ---------------------------
        k6 LOAD TEST
        ----------------------------*/
        stage('Run k6 Load Test') {
            steps {
                sh '''
                    echo "[INFO] Running k6 load test..."
                    mkdir -p reports/k6

                    docker run --rm \
                        --network microservices-checkout-quality-gate_default \
                        -v $WORKSPACE/load_tests:/scripts \
                        grafana/k6 run /scripts/checkout-smoke.js \
                        --out json=/scripts/k6-output.json || true
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'load_tests/k6-output.json', allowEmptyArchive: true
                }
            }
        }

        /* ---------------------------
        OWASP ZAP SECURITY SCAN
        ----------------------------*/
        stage('OWASP ZAP Baseline Scan') {
            steps {
                sh '''
                    echo "[INFO] Running ZAP baseline security scan..."

                    mkdir -p security/zap_reports

                    docker pull owasp/zap2docker-stable

                    docker run --rm \
                        --network microservices-checkout-quality-gate_default \
                        -v $WORKSPACE/security/zap_reports:/zap/wrk \
                        owasp/zap2docker-stable zap-baseline.py \
                        -t http://ui-service:5006 \
                        -r zap-baseline-report.html \
                        -x zap-baseline-report.xml \
                        -J zap-baseline-report.json \
                        -m 5 || true
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'security/zap_reports/*', allowEmptyArchive: true
                }
            }
        }

        /* ---------------------------
        NEWMAN POSTMAN API SMOKE TESTS
        ----------------------------*/
        stage('Run Newman API Smoke Tests') {
            steps {
                sh '''
                    echo "[INFO] Running Postman API tests..."
                    mkdir -p reports/newman

                    /opt/homebrew/bin/newman run postman/checkout-microservices.postman_collection.json \
                        -e postman/test-environment.postman_environment.json \
                        --reporters cli,json \
                        --reporter-json-export reports/newman/newman-report.json || true
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/newman/*', allowEmptyArchive: true
                }
            }
        }

        /* ---------------------------
        SELENIUM UI TESTS
        ----------------------------*/
        stage('Run Selenium UI Tests') {
            steps {
                sh '''
                    echo "[INFO] Running Selenium UI tests..."
                    . venv/bin/activate
                    pytest tests/selenium -v --junitxml=reports/selenium-results.xml || true
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/selenium-results.xml', allowEmptyArchive: true
                }
            }
        }

        /* ---------------------------
        PLAYWRIGHT UI TESTS
        ----------------------------*/
        stage('Run Playwright UI Tests') {
            steps {
                dir('ui-tests') {
                    sh '''
                        echo "[INFO] Running Playwright UI tests..."
                        npx playwright install || true
                        npx playwright test --reporter=line,junit --output=test-results || true
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'ui-tests/test-results/**/*', allowEmptyArchive: true
                }
            }
        }

    } // stages

    /* ---------------------------
    POST ACTION → ALWAYS clean Docker
    ----------------------------*/
    post {
        always {
            sh '''
                echo "[INFO] Cleaning up Docker..."
                docker compose down || true
            '''
        }
    }
}

