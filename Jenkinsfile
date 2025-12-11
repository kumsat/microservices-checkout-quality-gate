pipeline {
    agent any

    environment {
        PY_HOME = "${WORKSPACE}/venv"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python venv') {
            steps {
                sh '''
                    python3 -m venv venv
                    source venv/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Docker Compose Up') {
            steps {
                sh '''
                    docker compose down || true
                    docker compose up -d
                    sleep 10
                '''
            }
        }

        stage('Run PyTest BDD Tests') {
            steps {
                sh '''
                    source venv/bin/activate
                    pytest tests/steps -v
                '''
            }
        }

        stage('Run Newman API Tests') {
            steps {
                sh '''
                    newman run postman/checkout-microservices.postman_collection.json \
                        -e postman/test-environment.postman_environment.json
                '''
            }
        }

        stage('Run Selenium UI Tests') {
            steps {
                sh '''
                    source venv/bin/activate
                    pytest tests/selenium -v
                '''
            }
        }
    }

    post {
        always {
            sh 'docker compose down || true'
        }
    }
}

