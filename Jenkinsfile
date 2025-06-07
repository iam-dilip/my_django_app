// Jenkinsfile (place this in the root of your Git repository: https://github.com/iam-dilip/my_django_app.git)

pipeline {
    agent any

    environment {
        // IMPORTANT: Replace 'dockerhub-credentials' with the actual ID of your Docker Hub credentials
        DOCKER_REGISTRY_CREDENTIALS_ID = 'dockerhub-credentials'

        // User's Docker Hub username (iamdilipkumar)
        DOCKER_USER_ID = 'iamdilipkumar'
        DOCKER_IMAGE_NAME = "${env.DOCKER_USER_ID}/my-django-app"

        // SonarQube specific definitions
        SONARQUBE_SERVER_NAME = 'My SonarQube Server'
        SONARQUBE_CREDENTIAL_ID = 'sonarqube-token'
        SONARQUBE_PROJECT_KEY = 'my-django-app'
        SONARQUBE_PROJECT_NAME = 'My Django App'

        // Kubeconfig path for Jenkins to access Minikube (from previous successful setup)
        JENKINS_KUBECONFIG_PATH = '/tmp/minikube-kubeconfig-for-jenkins' // Ensure Jenkins has read access here
    }

    stages {
        stage('Checkout Application Code') {
            steps {
                echo 'Cloning the application Git repository...'
                // Using the updated GitHub repository URL
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
                            -Dsonar.python.coverage.reportPaths=xml:coverage.xml"
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

        // Deploy to Minikube Stage (direct deployment, no Argo CD)
        stage('Deploy to Minikube') {
            steps {
                echo 'Starting Minikube for deployment...'
                script {
                    sh '/usr/local/bin/minikube start --driver=docker --wait=all --embed-certs'
                    sh '/usr/local/bin/minikube addons enable ingress'

                    echo 'Deploying application to Minikube...'
                    // Ensure the image tag in your local django-deployment.yaml matches the newly built image
                    sh "sed -i 's|image: ${env.DOCKER_USER_ID}/my-django-app:.*|image: ${env.DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}|g' django-deployment.yaml"
                    sh '/usr/local/bin/minikube kubectl -- apply -f django-deployment.yaml'
                    sh '/usr/local/bin/minikube kubectl -- apply -f django-service.yaml'

                    // Add a wait for rollout to complete to ensure the pod is truly ready
                    echo 'Waiting for Django app deployment rollout to complete (max 120s)...'
                    sh '/usr/local/bin/minikube kubectl -- rollout status deployment/django-app-deployment --timeout=120s'

                    echo 'Attempting to get Minikube service URL...'
                    // Use || true to prevent this step from failing the pipeline, as it prints the URL regardless
                    def serviceUrl = sh(script: '/usr/local/bin/minikube service django-app-service --url || true', returnStdout: true).trim()
                    echo "Django application deployed and accessible at: ${serviceUrl}"

                    // IMPORTANT: Generate kubeconfig for 'dilip' user to access Minikube
                    echo 'Generating kubeconfig for dilip user...'
                    sh(script: """
                        # Get the kubeconfig content
                        KUBECONFIG_CONTENT=\$(/usr/local/bin/minikube kubectl -- config view --flatten --minify)

                        # Define a shared path for the kubeconfig (accessible by dilip)
                        KUBECONFIG_FOR_DILIP="/tmp/minikube-kubeconfig-for-dilip"

                        # Write to the shared file
                        echo "\${KUBECONFIG_CONTENT}" > "\${KUBECONFIG_FOR_DILIP}"

                        # Set read permissions for others (Dilip)
                        chmod o+r "\${KUBECONFIG_FOR_DILIP}"
                        echo "Kubeconfig for dilip user saved to: \${KUBECONFIG_FOR_DILIP} with read permissions."
                    """)
                }
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
            script {
                echo 'Stopping and deleting Minikube due to pipeline failure...'
                sh '/usr/local/bin/minikube stop || true'
                sh '/usr/local/bin/minikube delete || true'
            }
        }
    }
}
