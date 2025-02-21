pipeline {
  agent {
    docker {
        image 'python:3.9'
        args '--user root'
    }
  }
  options {
    skipDefaultCheckout(true)
  }
  environment {
    API_KEY = credentials('NEWS_API_KEY')
    DOCKER_REGISTRY = 'rsrprojects'
    IMAGE_NAME = 'news-app'
    IMAGE_TAG = 'v1.0'
    DOCKERHUB_CREDS = credentials('DOCKER_CREDENTIALS')
  }  
  stages {
    
    stage('checkout') {
      steps {
          checkout scm
      }
    }  
    stage('Prepare Environment') {
      steps {
        sh '''
          echo "NEWS_API_KEY=${API_KEY}" > .env
          echo "Debug: Content of .env file"
          cat .env
          chmod 644 .env
          chown 1000:1000 .env
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
        sh '''
          echo "Running Linter..."
          flake8 . || echo "Linting completed with warnings."
        '''
      }
    }
    stage('Security Scan') {
      steps {
        sh '''
          echo "Running security scan with Bandit..."
          bandit -r . --severity-level medium || echo "Bandit scan completed with warnings."
        '''
      }
    }
    stage('Unit Tests') {
      steps {
        sh '''
          echo "Running unit tests..."
          PYTHONPATH=$PYTHONPATH:. pytest tests/ --maxfail=1
        '''
      }
    }
    stage('Stash Code') {
      steps {
        sh 'ls -la'
        stash(includes: '**', excludes: '.pytest_cache/**, .env', name: 'workspace')
      }
    }
    stage('unstash code') {
      agent any
      steps {
        script {
          unstash 'workspace'
        }
        sh '''
          echo "Recreating .env file..."
          echo "NEWS_API_KEY=${API_KEY}" > .env
          echo "Debug: Content of .env file"
          cat .env
        '''
      }
    }   
    stage('build') {
      agent any
      steps {
        sh '''
        echo "Checking workspace files:"
        ls -la
        echo "Building Docker image..."
        sleep 5
        docker build -t ${DOCKER_REGISTRY}/somthing:latest .
        '''
      }
    }

    stage('login') {
      agent any
      steps {
        sh 'echo $DOCKERHUB_CREDS_PSW | docker login -u $DOCKERHUB_CREDS_USR --password-stdin'
      }
    }

    stage('push') {
      agent any
      steps {
        sh 'docker push ${DOCKER_REGISTRY}/somthing:latest'
      }
    }

    stage('logout') {
      agent any
      steps {
        sh 'docker logout'
      }
    }
  }

  post {
    always {
      echo 'Pipeline finished.'
    }

    success {
      echo 'All checks passed successfully! Image has been built and pushed.'
    }

    failure {
      echo 'One or more checks failed. Docker build will be skipped.'
    }
  }
}
