pipeline {
    agent {
        docker {
            image 'python:3.9'
            // make sudo commands
            args '-u root:root'
        }
    }

    stages {

        stage('checkout') {
            steps {
                checkout scm
            }
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