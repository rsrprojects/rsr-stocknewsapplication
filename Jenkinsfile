pipeline {
  agent any
  environment {
    API_KEY = credentials('NEWS_API_KEY')
    DOCKER_IMAGE = 'rsrprojects/flask-news-app'
    IMAGE_TAG = 'test'
    DOCKERHUB_CREDS = credentials('DOCKER_CREDENTIALS')
    TF_API_TOKEN = credentials('TERRAFORM_CLOUD_API')
    WORKSPACE_ID = 'ws-sbPFYMrFfwvtFurY'
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Prepare Environment') {
      steps {
        sh '''
        echo "NEWS_API_KEY=${API_KEY}" > .env
        cat .env
        '''
      }
    }

    stage('Setup') {
      steps {
        sh '''
        which python3 || (apt-get update && apt-get install -y python3 python3-venv jq)
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

    stage('Build & Push Docker Image') {
      steps {
        sh '''
        echo "Building Docker Image..."
        docker build -t $DOCKER_IMAGE:$IMAGE_TAG .
        echo "Logging into DockerHub..."
        echo $DOCKERHUB_CREDS_PSW | docker login -u $DOCKERHUB_CREDS_USR --password-stdin
        echo "Pushing Docker Image..."
        docker push $DOCKER_IMAGE:$IMAGE_TAG
        '''
      }
    }

    stage('Trigger Terraform Apply in Terraform Cloud') {
      steps {
        script {
          def apply_run_id = sh(script: '''
            curl -s -X POST https://app.terraform.io/api/v2/runs \
            -H "Authorization: Bearer ${TF_API_TOKEN}" \
            -H "Content-Type: application/vnd.api+json" \
            --data '{
              "data": {
                "attributes": {
                  "message": "Terraform Apply Triggered by Jenkins",
                  "auto-apply": true
                },
                "relationships": {
                  "workspace": {
                    "data": { "type": "workspaces", "id": "'${WORKSPACE_ID}'" }
                  }
                }
              }
            }' | jq -r '.data.id'
          ''', returnStdout: true).trim()

          echo "Terraform Apply Run ID: ${apply_run_id}"

          if (!apply_run_id || apply_run_id == "null") {
            error("Terraform Apply Failed to Start!")
          }

          sh '''
          echo "Waiting for Terraform Apply to Complete..."
          while true; do
            STATUS=$(curl -s -X GET "https://app.terraform.io/api/v2/runs/${apply_run_id}" \
            -H "Authorization: Bearer ${TF_API_TOKEN}" | jq -r '.data.attributes.status')

            echo "Terraform Apply Status: $STATUS"

            if [[ "$STATUS" == "applied" ]]; then
              break
            elif [[ "$STATUS" == "errored" ]]; then
              echo "Terraform Apply Failed!"
              exit 1
            fi

            sleep 10
          done
          '''
        }
      }
    }

    stage('Retrieve EC2 Public IP & Run Tests') {
      steps {
        script {
          def state_version_id = sh(script: '''
            curl -s --request GET \
              --url "https://app.terraform.io/api/v2/workspaces/${WORKSPACE_ID}/current-state-version" \
              --header "Authorization: Bearer ${TF_API_TOKEN}" \
              --header "Content-Type: application/vnd.api+json" | jq -r '.data.id'
          ''', returnStdout: true).trim()

          if (!state_version_id || state_version_id == "null") {
            error("Failed to retrieve Terraform state version ID!")
          }

          def ec2_ip = sh(script: '''
            curl -s --request GET \
              --url "https://app.terraform.io/api/v2/state-versions/${state_version_id}" \
              --header "Authorization: Bearer ${TF_API_TOKEN}" \
              --header "Content-Type: application/vnd.api+json" | jq -r '.data.attributes.outputs.ec2_public_ip.value'
          ''', returnStdout: true).trim()

          echo "EC2 Public IP: ${ec2_ip}"

          if (!ec2_ip || ec2_ip == "null") {
            error("EC2 IP not found! Check Terraform Outputs.")
          }

          echo "Running Health Check..."
          sh "curl -f http://${ec2_ip}:5000/health || exit 1"
        }
      }
    }

    stage('Trigger Terraform Destroy in Terraform Cloud') {
      when {
        expression { return currentBuild.result == 'SUCCESS' }
      }
      steps {
        script {
          def destroy_run_id = sh(script: '''
            curl -s -X POST https://app.terraform.io/api/v2/runs \
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
                    "data": { "type": "workspaces", "id": "'${WORKSPACE_ID}'" }
                  }
                }
              }
            }' | jq -r '.data.id'
          ''', returnStdout: true).trim()

          echo "Terraform Destroy Run ID: ${destroy_run_id}"

          if (!destroy_run_id || destroy_run_id == "null") {
            error("Terraform Destroy Failed to Start!")
          }
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
      echo 'Pipeline completed successfully! Image built, pushed, tested, deployed, and destroyed.'
    }
    failure {
      echo 'Pipeline failed! Review logs for details.'
    }
  }
}
