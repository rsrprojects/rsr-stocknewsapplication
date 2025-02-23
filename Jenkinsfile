pipeline {
  agent any
  environment {
    DOCKER_HOST = 'tcp://docker-in-docker:2375'
    API_KEY = credentials('NEWS_API_KEY')
    DOCKER_IMAGE = 'rsrprojects/flask-news-app'
    IMAGE_TAG = 'v1.0'
    DOCKERHUB_CREDS = credentials('DOCKER_CREDENTIALS')
  }
  stages {
    stage('Checkout') {
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
        '''
      }
    }
    stage('Setup') {
      steps {
        sh 'python3 -m venv venv'
        sh './venv/bin/pip install -r requirements.txt'
      }
    }
    stage('Test') {
      steps {
        sh './venv/bin/python -m unittest discover tests'
      }
    }
    stage('Build Docker Image') {
      steps {
        sh 'docker build -t $DOCKER_IMAGE:latest .'
      }
    }
    stage('Push to Docker Hub') {
      when { branch 'main' }
      steps {
        withCredentials([usernamePassword(credentialsId: 'DOCKER_CREDENTIALS', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
        }
        sh 'docker push $DOCKER_IMAGE:$IMAGE_TAG'
      }
    }
    stage('Deploy') {
      steps {
        sh 'docker network connect jenkins flask-news-app || true' // Ensure correct networking
        sh 'docker run -d --rm --network jenkins -p 5000:5000 --env-file .env --name news-app $DOCKER_IMAGE:latest'
      }
    }
    stage('Logout') {
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
