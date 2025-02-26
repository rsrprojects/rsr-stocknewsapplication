pipeline {
  agent any
  environment {
    API_KEY = credentials('NEWS_API_KEY')
    DOCKER_IMAGE = 'rsrprojects/flask-news-app'
    IMAGE_TAG = 'test'
    DOCKERHUB_CREDS = credentials('DOCKER_CREDENTIALS')
    TERRAFORM_REPO_BRANCH = 'main'
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
      steps {
        withCredentials([usernamePassword(credentialsId: 'DOCKER_CREDENTIALS', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
        }
      }
    }
    stage('Push image to dockerhub') {
      steps {
        sh 'docker push $DOCKER_IMAGE:$IMAGE_TAG'
      }
    }
    stage('Pull The App And Test It') {
      agent {
        docker {
          image '$DOCKER_IMAGE:$IMAGE_TAG'
          args '''
            -p 5000:5000
            -e FLASK_APP=app.main
            -e FLASK_ENV=development
            --rm
          '''
        }
        steps {
          sh 'curl http://localhost:5000'
        }
      }
    }
    stage('Checkout Terraform') {
      steps {
        checkout scmGit(
          branches: [[name: $TERRAFORM_REPO_BRANCH]],
          userRemoteConfigs: [[url: 'https://github.com/rsrprojects/rsr-stocknewsapplication-terraform-.git']])
      }
    }
    stage('Install Terraform') {
      steps {
        sh '''
          sudo apt-get install terraform -y
          terraform --version || true
        '''
      }
    }
    stage('Terraform Plan') {
      steps {
        sh '''
          terraform plan
        '''
      }
    }
  }
  post {
    always {
      sh '''
        docker logout
        docker image rm $DOCKER_IMAGE:$IMAGE_TAG || true
      '''
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
