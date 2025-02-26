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
    stage('Checkout Terraform') {
      steps {
        checkout([
            $class: 'GitSCM',
            branches: [[name: "${TERRAFORM_REPO_BRANCH}"]],
            userRemoteConfigs: [[
                url: 'https://github.com/rsrprojects/rsr-stocknewsapplication-terraform-.git',
                credentialsId: 'GITHUB_API_KEY'
            ]]
        ])
        sh 'ls -la'
      }  
    }
    stage('Install Terraform') {
      steps {
        sh '''
          curl -fsSL https://apt.releases.hashicorp.com/gpg | tee /etc/apt/trusted.gpg.d/hashicorp.asc
          echo "deb [signed-by=/etc/apt/trusted.gpg.d/hashicorp.asc] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list
          apt-get update && apt-get install -y terraform
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
        docker image rm "${DOCKER_IMAGE}:${IMAGE_TAG}" || true
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
