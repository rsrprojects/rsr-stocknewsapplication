pipeline {
    agent {
        any
    }

    enviorment {
        API_KEY = credentials('NEWS_API_KEY') // Getting the API key from jenkins credentials
    }

    stages {

        stage('checkout') {
            steps {
                checkout scm
            }
        }

        stage('Prepere Enviorment') {
            steps {
                sh 'echo "${API_KEY}" > .env' // Create .env file in the working directory
            }

        stage('Install Dependencies') {
            steps{
                sh '''
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    # Install dev tools: Linting, testing, security scaning
                    pip install flake8 bandit pytest
                '''
            }
        }

        stage('Lint') {
            steps {
                sh(script: 'flake8 . || true', returnStatus: true)
            }
        }

        stage('Security Scan') {
            steps {
                sh 'bandit -r . --severity-level medium'
            }
        }

        stage('Unit Tests') {
            steps {
                sh 'PYTHONPATH=$PYTHONPATH:. pytest tests/ --maxfail=1'
            }
        }
    }

    post {
        always {
            echo 'Pipline finished.'
        }

        success {
            echo 'All checks passed successfully!'
        }

        failure {
            echo 'One or more checks failed.'
        }
    }
}
