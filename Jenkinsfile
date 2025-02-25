pipeline {
  agent any
  environment {
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
        sh '''
        which python3 || (apt-get update && apt-get install -y python3 python3-venv)
        python3 -m venv venv
        ./venv/bin/pip install -r requirements.txt
        '''
      }
    }
    stage('Test') {
      steps {
        sh './venv/bin/python -m pytest tests/'
      }
    }
    stage('Build Docker Image') {
      steps {
        sh 'docker build -t $DOCKER_IMAGE:$IMAGE_TAG .'
      }
    }
    stage('Connect to DockerHub') {
      when { branch 'master' }
      steps {
        withCredentials([usernamePassword(credentialsId: 'DOCKER_CREDENTIALS', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
        }
      }
    }
    stage('Deploy') {
      steps {
        sh '''
        docker rm -f news-app || true
        docker run -d -p 5000:5000 --env-file .env --name news-app $DOCKER_IMAGE:$IMAGE_TAG
        '''
      }
    }
    stage('Push image to dockerhub') {
      steps {
        sh 'docker push $DOCKER_IMAGE:$IMAGE_TAG'
      }
    }
    stage('Test Application Deployment') {
      steps {
        script {
          sleep(time: 10, unit: 'SECONDS')
          def response = sh(script: 'curl -s http://localhost:5000', returnStdout: true)
          if (!response.contains('Expected Keyword')) {
            error("Deployment verification failed: expected content not found.")
          } 
          else {
             echo "Deployment Test Passed!"
          }
        }
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
      // sh '''
      //   docker stop news-app || true
      //   docker rm news-app || true
      // '''
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
