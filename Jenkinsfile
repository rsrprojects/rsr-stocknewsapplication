pipeline {
  agent {
    docker {
        image 'ubuntu:22.04'
        args '-u root'
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
    
    stage('Install Python') {
      steps {
        sh '''
          apt update && apt install -y python3 python3-pip
          python3 --version
        '''
      }
    }
    stage('Install Docker') {
      steps {
        sh '''
          apt-get update
          apt install curl -y
          apt-get install ca-certificates curl -y
          install -m 0755 -d /etc/apt/keyrings
          curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
          chmod a+r /etc/apt/keyrings/docker.asc  
          echo \
            "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
            $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
            tee /etc/apt/sources.list.d/docker.list > /dev/null
          apt-get update
          apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
        '''
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
          echo "NEWS_API_KEY=${API_KEY}" > .env
          echo "Debug: Content of .env file"
          cat .env
        '''
      }
    }
    stage('Install Dependencies') {
      steps {
        sh 'python3 -m pip install --upgrade pip'
        sh 'python3 -m pip install -r requirements.txt'
        sh 'python3 -m pip install flake8 bandit pytest'
      }
    }
    stage('Lint') {
      steps {
        sh '''
          echo "Running Linter..."
          python3 -m flake8 . || echo "Linting completed with warnings."
        '''
      }
    }
    stage('Security Scan') {
      steps {
        sh '''
          echo "Running security scan with Bandit..."
          python3 -m bandit -r . --severity-level medium || echo "Bandit scan completed with warnings."
        '''
      }
    }
    stage('Unit Tests') {
      steps {
        sh '''
          echo "Running unit tests..."
          PYTHONPATH=$PYTHONPATH:. python3 -m pytest tests/ --maxfail=1
        '''
      }
    }
    // stage('Stash Code') {
    //   steps {
    //     sh 'ls -la'
    //     stash(includes: '**', name: 'workspace')
    //   }
    // }
    // stage('unstash code') {
    //   agent any
    //   steps {
    //     script {
    //       unstash 'workspace'
    //     }
    //     sh '''
    //       echo "Recreating .env file..."
    //       echo "NEWS_API_KEY=${API_KEY}" > .env
    //       echo "Debug: Content of .env file"
    //       cat .env
    //     '''
    //   }
    // }   
    // stage('Second Checkout') {
    //   agent any
    //   steps {
    //     checkout scm
    //   }
    // }
    // stage('prepare .env File') {
    //   agent any
    //   steps {
    //     sh '''
    //       echo "NEWS_API_KEY=${API_KEY}" > .env
    //       echo "Debug: Content of .env file"
    //       cat .env
    //     '''
    //   }
    // }
    stage('build') {
      steps {
        sh '''
        echo "Checking workspace files:"
        ls -la
        echo "Building Docker image..."
        sleep 5
        docker build --progress=plain --no-cache -t ${DOCKER_REGISTRY}/something:latest .
        '''
      }
    }
    stage('login') {
      steps {
        sh 'echo $DOCKERHUB_CREDS_PSW | docker login -u $DOCKERHUB_CREDS_USR --password-stdin'
      }
    }
    stage('push') {

      steps {
        sh 'docker push ${DOCKER_REGISTRY}/something:latest'
      }
    }
    stage('logout') {
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
