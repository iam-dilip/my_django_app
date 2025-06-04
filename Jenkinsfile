// Jenkinsfile (place this in the root of your Git repository)

pipeline {
    agent any

    // Define environment variables at the pipeline level
    // These will be accessible as env.VARIABLE_NAME throughout the pipeline
    environment {
        // IMPORTANT: Replace 'dockerhub-credentials' with the actual ID of your Docker Hub credentials
        DOCKER_REGISTRY_CREDENTIALS_ID = 'dockerhub-credentials'

        // IMPORTANT: Change 'dilip10jan' to your actual Docker Hub username!
        DOCKER_IMAGE_NAME = 'dilip10jan/my-django-app'

        // SonarQube specific definitions
        // IMPORTANT: Match 'My SonarQube Server' with the Name you configured in Jenkins -> Configure System -> SonarQube servers
        SONARQUBE_SERVER_ID = 'My SonarQube Server'
        // IMPORTANT: This should be the Project Key you created in SonarQube UI
        SONARQUBE_PROJECT_KEY = 'my-django-app'
        // IMPORTANT: This should be the Project Name you created in SonarQube UI
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
                    // Now access variables via 'env.' prefix
                    docker.build("${env.DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}", ".")
                    docker.build("${env.DOCKER_IMAGE_NAME}:latest", ".")
                }
            }
        }

        stage('Run Basic Checks') {
            steps {
                echo 'Running basic Django checks inside a temporary container...'
                script {
                    // Access variables via 'env.' prefix
                    sh "docker run --rm -v \$(pwd):/app ${env.DOCKER_IMAGE_NAME}:latest python manage.py check"
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo 'Running SonarQube analysis...'
                script {
                    // Access variables via 'env.' prefix
                    withSonarQubeEnv(credentialsId: env.SONARQUBE_SERVER_ID, scannerHome: 'SonarScanner CLI') {
                        sh "sonar-scanner \
                            -Dsonar.projectKey=${env.SONARQUBE_PROJECT_KEY} \
                            -Dsonar.projectName=${env.SONARQUBE_PROJECT_NAME} \
                            -Dsonar.sources=./ \
                            -Dsonar.python.version=3.10"
                    }
                }
            }
        }

        stage('SonarQube Quality Gate') {
            steps {
                echo 'Waiting for Quality Gate status from SonarQube...'
                script {
                    timeout(time: 10, unit: 'MINUTES') {
                        def qg = waitForQualityGate()
                        if (qg.status != 'OK') {
                            error "Pipeline aborted due to Quality Gate failure: ${qg.status}"
                        }
                    }
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                echo 'Pushing Docker image to registry...'
                script {
                    // DOCKER_REGISTRY_CREDENTIALS_ID is accessed via env.
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
