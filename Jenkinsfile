// Jenkinsfile (place this in the root of your Git repository)

pipeline {
    agent any

    environment {
        DOCKER_REGISTRY_CREDENTIALS_ID = 'dockerhub-credentials'
        DOCKER_IMAGE_NAME = 'dilip10jan/my-django-app'

        SONARQUBE_SERVER_NAME = 'My SonarQube Server'
        SONARQUBE_CREDENTIAL_ID = 'sonarqube-token'
        SONARQUBE_PROJECT_KEY = 'my-django-app'
        SONARQUBE_PROJECT_NAME = 'My Django App'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Cloning the Git repository...'
                git branch: 'main', url: 'https://github.com/dilip10jan/my_django_app.git'
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
                    sh "docker run --rm -v \$(pwd):/app ${env.DOCKER_IMAGE_NAME}:latest python manage.py check"
                }
            }
        }

        stage('Run Unit and Integration Tests') {
            steps {
                echo 'Running unit/integration tests...'
                script {
                    // Mount the current workspace to /app
                    // Use --verbose and specify the 'tests/' directory explicitly for pytest
                    // This tells pytest to look for tests specifically within the 'tests' folder.
                    sh "docker run --rm -v \$(pwd):/app ${env.DOCKER_IMAGE_NAME}:latest \
                        python -m pytest --verbose tests/ --junitxml=junit.xml --cov=. --cov-report=xml:coverage.xml"
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

        stage('Deploy (Placeholder)') {
            steps {
                echo 'Deployment stage: This is where you would add your deployment logic.'
                echo "Image to deploy: ${env.DOCKER_IMAGE_NAME}:latest"
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished.'
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check logs for details.'
        }
    }
}
