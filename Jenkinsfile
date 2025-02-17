pipeline {
    agent {
        docker {
            image 'python:3.9'
            // make sudo commands
            args '-u root:root'
        }
    }

    environment {
        API_KEY = credentials('NEWS_API_KEY') // Getting the API key from Jenkins credentials
    }

    stages {

        stage('Debug') {
            steps {
                sh 'echo "Cheking Jenkins..."'
            }
        }

        stage('checkout') {
            steps {
                checkout scm
            }
        }

        stage('Prepare Environment') {
            steps {
                sh '''
                echo "NEWS_API_KEY=${API_KEY}" > .env // Create .env file in the working directory
                echo "Debug: Contant of .env file"
                cat .env
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    // Install dev tools: Linting, testing, security scanning
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
                sh '''
                    PYTHONPATH=$PYTHONPATH:. pytest tests/ --maxfail=1
                '''
            }
        }
    }


    post {
        always {
            echo 'Pipeline finished.'
        }

        success {
            echo 'All checks passed successfully!'
        }

        failure {
            echo 'One or more checks failed.'
        }
    }
}
