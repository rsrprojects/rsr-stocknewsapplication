pipeline {
  agent any
  stages {
    stage('Prepare Environment') {
      steps {
        sh '''
                    echo "NEWS_API_KEY=${API_KEY}" > .env
                    echo "Debug: Content of .env file"
                    cat .env
                '''
      }
    }

    stage('Install Dependencies') {
      steps {
        sh '''
                    pip install --upgrade pip
                    pip install -r requirements.txt
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

    stage('Stash Code') {
      steps {
        sh 'ls -la'
        stash(includes: '**', name: 'workspace')
      }
    }

    stage('Docker Build and Push') {
      agent {
        label 'docker'
      }
      steps {
        unstash 'workspace'
        withCredentials(bindings: [usernamePassword(credentialsId: 'DOCKER_CREDENTIALS', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          sh '''
                        echo "Building Docker image..."
                        docker build -t ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} .
                        
                        echo "Logging into Docker Hub..."
                        echo "${DOCKER_PASS}" | docker login -u "${DOCKER_USER}" --password-stdin
                        
                        echo "Pushing Docker image..."
                        docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
                    '''
        }

      }
    }

  }
  environment {
    API_KEY = credentials('NEWS_API_KEY')
    DOCKER_REGISTRY = 'rsrprojects/nothing-special'
    IMAGE_NAME = 'news-app'
    IMAGE_TAG = 'v1.0'
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
  options {
    skipDefaultCheckout(true)
  }
}