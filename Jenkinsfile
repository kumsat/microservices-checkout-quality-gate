pipeline {
    agent any

    environment {
        // Make sure Docker + Python are accessible
        PATH = "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:${env.PATH}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo "[INFO] Code checked out"
            }
        }

        stage('Setup Python venv') {
            steps {
                sh '''
                    if [ ! -d "venv" ]; then
                      python3 -m venv venv
                    fi

                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

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

        stage('Run PyTest BDD API Flow') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest tests/steps -v --junitxml=reports/pytest-results.xml
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/pytest-results.xml', allowEmptyArchive: true
                }
            }
        }

        stage('Run k6 Load Test') {
            steps {
                sh '''
                    echo "[INFO] Running k6 load test..."
                    mkdir -p reports/k6

                    docker run --rm \
                      --network microservices-checkout-quality-gate_default \
                      -v "${WORKSPACE}/load_tests:/scripts" \
                      grafana/k6 run /scripts/checkout-smoke.js \
                      --out json=/scripts/k6-output.json
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'load_tests/k6-output.json', allowEmptyArchive: true
                }
            }
        }

        stage('OWASP ZAP Baseline Scan') {
            steps {
                script {
                    // Make ZAP NON-BLOCKING for the pipeline
                    catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                        sh '''
                            echo "[INFO] Running ZAP baseline security scan..."
                            mkdir -p security/zap_reports

                            # Run ZAP from the weekly image (more up to date)
                            docker run --rm \
                              --network microservices-checkout-quality-gate_default \
                              -v "${WORKSPACE}/security/zap_reports:/zap/wrk" \
                              owasp/zap2docker-weekly zap-baseline.py \
                                -t http://ui-service:5006 \
                                -r zap-baseline-report.html \
                                -x zap-baseline-report.xml \
                                -J zap-baseline-report.json \
                                -m 5
                        '''
                    }
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'security/zap_reports/*', allowEmptyArchive: true
                }
            }
        }

        // You can flesh these out later – they are placeholders for now
        stage('Run Newman API Smoke Tests') {
            when { expression { false } }  // disabled for now
            steps {
                echo "[INFO] Newman stage placeholder"
            }
        }

        stage('Run Selenium UI Tests') {
            when { expression { false } }  // disabled for now
            steps {
                echo "[INFO] Selenium stage placeholder"
            }
        }

        stage('Run Playwright UI Tests') {
            when { expression { false } }  // disabled for now
            steps {
                echo "[INFO] Playwright stage placeholder"
            }
        }
    }

    post {
        always {
            sh '''
                echo "[INFO] Cleaning up Docker..."
                docker compose down || true
            '''
        }
    }
}

