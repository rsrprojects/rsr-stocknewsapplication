pipeline {
  agent any
  environment {
    API_KEY = credentials('NEWS_API_KEY')
    DOCKER_IMAGE = 'rsrprojects/flask-news-app'
    IMAGE_TAG = 'test'
    DOCKERHUB_CREDS = credentials('DOCKER_CREDENTIALS')
    TF_API_TOKEN = credentials('TERRAFORM_CLOUD_API')
    WORKSPACE_ID = 'ws-sbPFYMrFfwvtFurY'
    GITHUB_TOKEN = credentials('GITHUB_TOKEN')
    d_branchName = 'master'
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
    stage('Install jq') {
      steps {
        sh 'apt-get update && apt-get install -y jq'
      }
    }
    stage('Trigger Terraform Plan in Terraform Cloud') {
      steps {
        sh '''
        curl -X POST https://app.terraform.io/api/v2/runs \
        -H "Authorization: Bearer ${TF_API_TOKEN}" \
        -H "Content-Type: application/vnd.api+json" \
        --data '{
          "data": {
            "attributes": {
              "message": "Triggered by Jenkins",
              "auto-apply": true
            },
            "relationships": {
              "workspace": {
                "data": {
                  "type": "workspaces",
                  "id": "'${WORKSPACE_ID}'"
                }
              }
            }
          }
        }'
        '''
      }
    }
    stage('Wait for EC2 & Run Tests') {
      steps {
        script {
          sleep(time: 180, unit: 'SECONDS')
          sh '''
          echo "Fetching OUTPUT_URL from Terraform Cloud..."
          OUTPUTS_URL=$(curl -s --request GET \
            --url "https://app.terraform.io/api/v2/workspaces/${WORKSPACE_ID}/current-state-version" \
            --header "Authorization: Bearer ${TF_API_TOKEN}" \
            --header "Content-Type: application/vnd.api+json" | jq -r '.data.relationships.outputs.links.related')
            
          echo "OUTPUT_URL: $OUTPUTS_URL"

          echo "Fetching EC2 Public IP from Terraform Cloud Outputs..."
          EC2_IP=$(curl -s --request GET \
            --url "https://app.terraform.io$OUTPUTS_URL" \
            --header "Authorization: Bearer ${TF_API_TOKEN}" \
            --header "Content-Type: application/vnd.api+json" | jq -r '.data[0].attributes.value')

          echo "EC2 Public IP: $EC2_IP"
          
          if [ "$EC2_IP" == "null" ] || [ "$EC2_IP" == "" ]; then
            echo "Error: EC2 IP not found in Terraform Cloud!"
            exit 1
          fi

          echo "Running Health Check..."
          for i in {1..5}; do
            if curl -fs http://$EC2_IP:5000 | head -n 5; then
              echo "Health check successful!"
              break
            fi
            echo "Retrying health check..."
            sleep 10
          done
          '''
        }
      }
    }
    stage('Trigger Terraform Destroy in Terraform Cloud') {
      steps {
        sh '''
        curl -X POST https://app.terraform.io/api/v2/runs \
        -H "Authorization: Bearer ${TF_API_TOKEN}" \
        -H "Content-Type: application/vnd.api+json" \
        --data '{
          "data": {
            "attributes": {
              "message": "Terraform Destroy Triggered by Jenkins",
              "is-destroy": true,
              "auto-apply": true
            },
            "relationships": {
              "workspace": {
                "data": {
                  "type": "workspaces",
                  "id": "'${WORKSPACE_ID}'"
                }
              }
            }
          }
        }'
        '''
      }
    }
    stage('Create Pull Request') {
      steps {
        script {
          def branchName = "auto-pr-${BUILD_NUMBER}"

          sh '''
           which gh || (apt-get update && apt-get install -y gh)

           git config --global user.email "jenkins@example.com"
           git config --global user.name "Jenkins CI"

           git status
          '''
        }
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
