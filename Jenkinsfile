// Jenkinsfile (place this in the root of your Git repository)

pipeline {
    agent any

    environment {
        DOCKER_REGISTRY_CREDENTIALS_ID = 'dockerhub-credentials'
        DOCKER_IMAGE_NAME = 'iamdilipkumar/my-django-app'

        SONARQUBE_SERVER_NAME = 'My SonarQube Server'
        SONARQUBE_CREDENTIAL_ID = 'sonarqube-token'
        SONARQUBE_PROJECT_KEY = 'my-django-app'
        SONARQUBE_PROJECT_NAME = 'My Django App'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Cloning the Git repository...'
                git branch: 'main', url: 'https://github.com/iam-dilip/my_django_app.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building the Docker image...'
                script {
                    docker.build("${env.DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}", ".")
                    docker.build("${env.DOCKER_IMAGE_NAME}:latest", ".")
                }
            }
        }

        stage('Run Basic Checks') {
            steps {
                echo 'Running basic Django checks inside a temporary container...'
                script {
                    sh "docker run --rm -v \$(pwd):/app -e DJANGO_SETTINGS_MODULE=myproject.settings ${env.DOCKER_IMAGE_NAME}:latest python manage.py check"
                }
            }
        }

        stage('Run Unit and Integration Tests') {
            steps {
                echo 'Running unit/integration tests...'
                script {
                    sh "docker run --rm -v \$(pwd):/app -e DJANGO_SETTINGS_MODULE=myproject.settings ${env.DOCKER_IMAGE_NAME}:latest sh -c \"\
                        echo 'Listing contents of /app/tests/:' && \
                        ls -R tests/ && \
                        echo '--- End tests directory listing ---' && \
                        python -m pytest --verbose tests/ --junitxml=junit.xml --cov=. --cov-report=xml:coverage.xml \
                    \""
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo 'Running SonarQube analysis...'
                script {
                    def sonarScannerHome = tool 'SonarScanner CLI'

                    withSonarQubeEnv(server: env.SONARQUBE_SERVER_NAME, credentialsId: env.SONARQUBE_CREDENTIAL_ID) {
                        sh "${sonarScannerHome}/bin/sonar-scanner \
                            -Dsonar.projectKey=${env.SONARQUBE_PROJECT_KEY} \
                            -Dsonar.projectName='${env.SONARQUBE_PROJECT_NAME}' \
                            -Dsonar.sources=./ \
                            -Dsonar.python.version=3.10 \
                            -Dsonar.exclusions='venv/**,**/__pycache__/**,db.sqlite3,**/migrations/**,.git/**' \
                            -Dsonar.python.xunit.reportPaths=junit.xml \
                            -Dsonar.python.coverage.reportPaths=coverage.xml"
                    }
                }
            }
        }

        stage('SonarQube Quality Gate (Non-Blocking)') {
            steps {
                echo 'SonarQube analysis submitted. Proceeding without waiting for Quality Gate status.'
            }
        }

        stage('Push Docker Image') {
            steps {
                echo 'Pushing Docker image to registry...'
                script {
                    withCredentials([usernamePassword(credentialsId: env.DOCKER_REGISTRY_CREDENTIALS_ID, passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                        sh(script: """
                            DOCKER_PAT_VAR="${DOCKER_PASSWORD}"
                            DOCKER_USER_VAR="${DOCKER_USERNAME}"
                            echo "\${DOCKER_PAT_VAR}" | docker login -u "\${DOCKER_USER_VAR}" --password-stdin
                            unset DOCKER_PAT_VAR DOCKER_USER_VAR

                            echo 'Executing docker push for specific build number...'
                            docker push ${env.DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}

                            echo 'Executing docker push for latest tag...'
                            docker push ${env.DOCKER_IMAGE_NAME}:latest
                        """)
                    }
                }
            }
        }

        // Deploy to Minikube Stage - Minikube lifecycle managed by Jenkins
        stage('Deploy to Minikube') {
            steps {
                echo 'Starting Minikube for deployment...'
                script {
                    sh '/usr/local/bin/minikube start --driver=docker --wait=all --embed-certs'
                    sh '/usr/local/bin/minikube addons enable ingress'

                    echo 'Deploying application to Minikube...'
                    sh '/usr/local/bin/minikube kubectl -- apply -f django-deployment.yaml'
                    sh '/usr/local/bin/minikube kubectl -- apply -f django-service.yaml'

                    // --- DEBUGGING & URL RETRIEVAL ---
                    echo 'Waiting for Pods to be ready (max 120 seconds)...'
                    // This command will wait for the deployment to roll out successfully.
                    sh '/usr/local/bin/minikube kubectl -- rollout status deployment/django-app-deployment --timeout=120s'

                    echo 'Getting Pods status:'
                    sh '/usr/local/bin/minikube kubectl -- get pods -o wide'

                    echo 'Describing Pods for django-app-deployment (check Events for errors):'
                    def podName = sh(script: '/usr/local/bin/minikube kubectl -- get pods -l app=django-app -o jsonpath="{.items[0].metadata.name}" --sort-by=.metadata.creationTimestamp', returnStdout: true).trim()
                    if (podName) {
                        sh "/usr/local/bin/minikube kubectl -- describe pod ${podName}"
                        echo "Fetching logs from pod ${podName}:"
                        sh "/usr/local/bin/minikube kubectl -- logs ${podName}"
                    } else {
                        echo "No pod found for django-app-deployment yet."
                    }
                    echo '--- End Pod Debugging ---'

                    echo 'Attempting to get Minikube service URL...'
                    // Use '|| true' to make the command succeed in Jenkins, even if minikube service
                    // returns an error code due to its internal checks, as it prints the URL anyway.
                    def serviceUrl = sh(script: '/usr/local/bin/minikube service django-app-service --url || true', returnStdout: true).trim()
                    echo "Django application deployed and accessible at: ${serviceUrl}"
                    // --- END DEBUGGING & URL RETRIEVAL ---
                }
            }
        }

        stage('Deploy (Placeholder)') {
            steps {
                echo 'Deployment stage is now handled in "Deploy to Minikube".'
                echo 'This placeholder stage is no longer strictly necessary.'
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished.'
        }
        success {
            echo 'Pipeline completed successfully!'
            // Minikube cleanup removed from here to keep it running after successful build
            // You will need to manually stop/delete Minikube when done:
            // minikube stop
            // minikube delete
        }
        failure {
            echo 'Pipeline failed. Check logs for details.'
            // Keep cleanup on failure to free up resources if something went wrong
            script {
                echo 'Stopping and deleting Minikube due to pipeline failure...'
                sh '/usr/local/bin/minikube stop || true'
                sh '/usr/local/bin/minikube delete || true'
            }
        }
    }
}
