pipeline {
  agent any
  environment {
    API_KEY = credentials('NEWS_API_KEY')
    DOCKER_IMAGE = 'rsrprojects/flask-news-app'
    IMAGE_TAG = 'test'
    DOCKERHUB_CREDS = credentials('DOCKER_CREDENTIALS')
    // TERRAFORM_REPO_BRANCH = 'testing-tf'
    TF_API_TOKEN = credentials('TERRAFORM_CLOUD_API')
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
    stage('Trigger Terraform Apply') {
      steps {
        sh '''
        curl -X POST https://app.terraform.io/api/v2/runs \
        -H "Authorization: Bearer ${TF_API_TOKEN}" \
        -H "Content-Type: application/vnd.api+json" \
        --data '{
          "data": {
            "attributes": {
              "message": "Trigger Terraform Apply via Jenkins",
              "workspace-id": "your-terraform-workspace-id",
              "auto-apply": true
            }
          }
        }'
        '''
      }
    }
    stage('Wait for EC2 & Run Tests') {
      steps {
        script {
          sleep(time: 120, unit: 'SECONDS')
          sh '''
          EC2_IP=$(terraform output -raw ec2_public_ip)
          echo "EC2 Public IP: $EC2_IP"
          curl -f http://$EC2_IP:5000 || exit 1
          '''
        }
      }
    }
    stage('Destroy EC2 Instance') {
      when {
        expression { return currentBuild.result == 'SUCCESS' }
      }
      steps {
        sh '''
        curl -X POST https://app.terraform.io/api/v2/runs \
        -H "Authorization: Bearer ${TF_API_TOKEN}" \
        -H "Content-Type: application/vnd.api+json" \
        --data '{
          "data": {
            "attributes": {
              "message": "Trigger Terraform Destroy via Jenkins",
              "workspace-id": "your-terraform-workspace-id",
              "is-destroy": true
            }
          }
        }'
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
