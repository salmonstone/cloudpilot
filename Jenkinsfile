pipeline {
  agent any
  environment {
    DOCKERHUB_CREDENTIALS = credentials('dockerhub-creds')
    DOCKERHUB_REPO        = 'salmonstone/cloudpilot'
    IMAGE_TAG             = "${BUILD_NUMBER}"
    GROQ_API_KEY          = credentials('groq-api-key')
    K8S_NAMESPACE         = 'cloudpilot'
    CLUSTER_NAME          = 'cloudpilot-cluster'
    AWS_REGION            = 'ap-south-1'
  }

  stages {
    stage('Checkout') {
      steps {
        git branch: 'main',
            url: 'https://github.com/salmonstone/cloudpilot.git'
      }
    }

    stage('Docker Build') {
      steps {
        sh 'docker build -t ${DOCKERHUB_REPO}:${IMAGE_TAG} ./backend'
        sh 'docker tag ${DOCKERHUB_REPO}:${IMAGE_TAG} ${DOCKERHUB_REPO}:latest'
      }
    }

    stage('Trivy Security Scan') {
      steps {
        sh '''
          trivy image --exit-code 0 --severity HIGH,CRITICAL \
            --format json -o trivy-report.json \
            ${DOCKERHUB_REPO}:${IMAGE_TAG}
        '''
        archiveArtifacts 'trivy-report.json'
      }
    }

    stage('Push to DockerHub') {
      steps {
        sh 'echo ${DOCKERHUB_CREDENTIALS_PSW} | docker login -u ${DOCKERHUB_CREDENTIALS_USR} --password-stdin'
        sh 'docker push ${DOCKERHUB_REPO}:${IMAGE_TAG}'
        sh 'docker push ${DOCKERHUB_REPO}:latest'
      }
    }

    stage('Terraform Provision') {
      steps {
        dir('infrastructure/terraform') {
          sh 'terraform init'
          sh 'terraform apply -auto-approve'
        }
      }
    }

    stage('Configure kubectl') {
      steps {
        sh '''
          aws eks update-kubeconfig \
            --region ${AWS_REGION} \
            --name ${CLUSTER_NAME}
          kubectl cluster-info
        '''
      }
    }

    stage('Namespace + Secrets') {
      steps {
        sh '''
          kubectl create namespace cloudpilot    --dry-run=client -o yaml | kubectl apply -f -
          kubectl create namespace logging        --dry-run=client -o yaml | kubectl apply -f -
          kubectl create namespace monitoring     --dry-run=client -o yaml | kubectl apply -f -
          kubectl create namespace argocd         --dry-run=client -o yaml | kubectl apply -f -
          kubectl create namespace ingress-nginx  --dry-run=client -o yaml | kubectl apply -f -
          kubectl create secret generic cloudpilot-secrets \
            --from-literal=GROQ_API_KEY=${GROQ_API_KEY} \
            -n cloudpilot --dry-run=client -o yaml | kubectl apply -f -
        '''
      }
    }

    stage('Nginx Ingress') {
      steps {
        sh '''
          helm upgrade --install ingress-nginx ingress-nginx \
            --repo https://kubernetes.github.io/ingress-nginx \
            --namespace ingress-nginx \
            --set controller.service.type=LoadBalancer \
            --wait --timeout 5m || true
          kubectl wait --namespace ingress-nginx \
            --for=condition=ready pod \
            --selector=app.kubernetes.io/component=controller \
            --timeout=120s
        '''
      }
    }

   stage('ELK Stack') {
  steps {
    sh '''
      # Only deploy if not already running
      if ! kubectl get statefulset elasticsearch -n logging 2>/dev/null; then
        kubectl apply -f elk/01-elasticsearch.yaml -n logging
        kubectl wait --for=condition=ready pod -l app=elasticsearch \
          -n logging --timeout=180s
      else
        echo "Elasticsearch already running - skipping"
      fi
      kubectl apply -f elk/02-logstash.yaml    -n logging || true
      kubectl apply -f elk/03-kibana.yaml      -n logging || true
      kubectl apply -f elk/04-filebeat.yaml    -n logging || true
    '''
  }
}

    stage('ArgoCD + Monitoring') {
      steps {
        sh '''
          kubectl apply -n argocd \
            -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
          helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
          helm repo update
          helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
            --namespace monitoring --wait
          kubectl apply -f k8s/monitoring/alertmanager-rules.yaml -n monitoring
        '''
      }
    }

    stage('Helm Deploy') {
      steps {
        sh '''
          helm upgrade --install cloudpilot ./helm/cloudpilot \
            --namespace ${K8S_NAMESPACE} \
            --set image.tag=${IMAGE_TAG} \
            --set image.repository=${DOCKERHUB_REPO} \
            --atomic --wait --timeout 5m
        '''
      }
    }

    stage('Health Check') {
      steps {
        script {
          sleep(30)
          def status = sh(
            script: "curl -s -o /dev/null -w '%{http_code}' https://pilotcost.online/health",
            returnStdout: true).trim()
          if (status == '200') {
            echo 'Health check PASSED — deployment successful!'
          } else {
            sh 'helm rollback cloudpilot 0 -n cloudpilot'
            error("Health check FAILED (HTTP ${status}) — rolled back")
          }
        }
      }
    }
  }

  post {
    always   { sh 'docker image prune -f || true' }
    success  { echo 'PIPELINE SUCCEEDED — CloudPilot is live at https://pilotcost.online' }
    failure  {
      sh 'helm rollback cloudpilot 0 -n cloudpilot || true'
      echo 'PIPELINE FAILED — rolled back. Check logs above.'
    }
  }
}
