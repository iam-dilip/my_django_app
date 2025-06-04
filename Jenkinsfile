// Jenkinsfile (place this in the root of your Git repository)

// ... (existing DOCKER_REGISTRY_CREDENTIALS_ID and DOCKER_IMAGE_NAME definitions)

// SonarQube specific definitions
// IMPORTANT: Match 'sonarqube-server-id' with the Name you configured in Jenkins -> Configure System -> SonarQube servers
def SONARQUBE_SERVER_ID = 'My SonarQube Server' // Use the name you gave in Jenkins global config
// IMPORTANT: This should be the Project Key you created in SonarQube UI
def SONARQUBE_PROJECT_KEY = 'my-django-app'
// IMPORTANT: This should be the Project Name you created in SonarQube UI
def SONARQUBE_PROJECT_NAME = 'My Django App'

pipeline {
    agent any

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
                    docker.build("${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}", ".")
                    docker.build("${DOCKER_IMAGE_NAME}:latest", ".")
                }
            }
        }

        stage('Run Basic Checks') {
            steps {
                echo 'Running basic Django checks inside a temporary container...'
                script {
                    sh "docker run --rm -v \$(pwd):/app ${DOCKER_IMAGE_NAME}:latest python manage.py check"
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo 'Running SonarQube analysis...'
                script {
                    // The 'withSonarQubeEnv' step injects the SonarQube server URL and token
                    // based on the server ID configured in Jenkins -> Manage Jenkins -> Configure System.
                    // The 'scannerHome' specifies the SonarScanner CLI installation configured in Global Tool Configuration.
                    withSonarQubeEnv(credentialsId: SONARQUBE_SERVER_ID, scannerHome: 'SonarScanner CLI') { // Use the name you gave in Global Tool Config
                        // The sonar-scanner command.
                        // sonar.sources points to the root of your project checked out by Jenkins.
                        // sonar.projectKey and sonar.projectName are unique identifiers for your project in SonarQube.
                        // sonar.python.version is important for Python analysis.
                        // sonar.python.coverage.reportPaths is for integrating coverage reports (e.g., from pytest-cov).
                        sh "sonar-scanner \
                            -Dsonar.projectKey=${SONARQUBE_PROJECT_KEY} \
                            -Dsonar.projectName=${SONARQUBE_PROJECT_NAME} \
                            -Dsonar.sources=./ \
                            -Dsonar.python.version=3.10"
                            // If you integrate Python unit tests and coverage, you'd add:
                            // -Dsonar.python.coverage.reportPaths=coverage.xml"
                            // -Dsonar.python.xunit.reportPaths=junit.xml"
                    }
                }
            }
        }

        stage('SonarQube Quality Gate') {
            steps {
                echo 'Waiting for Quality Gate status from SonarQube...'
                script {
                    // This step waits for SonarQube to complete its analysis and
                    // check against the defined Quality Gate.
                    // Timeout is important to prevent builds from hanging indefinitely.
                    timeout(time: 10, unit: 'MINUTES') { // Max 10 minutes to wait for Quality Gate
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
                    withCredentials([usernamePassword(credentialsId: DOCKER_REGISTRY_CREDENTIALS_ID, passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                        sh(script: """
                            DOCKER_PAT_VAR="${DOCKER_PASSWORD}"
                            DOCKER_USER_VAR="${DOCKER_USERNAME}"
                            echo "\${DOCKER_PAT_VAR}" | docker login -u "\${DOCKER_USER_VAR}" --password-stdin
                            unset DOCKER_PAT_VAR DOCKER_USER_VAR

                            echo 'Executing docker push for specific build number...'
                            docker push ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}

                            echo 'Executing docker push for latest tag...'
                            docker push ${DOCKER_IMAGE_NAME}:latest
                        """)
                    }
                }
            }
        }

        stage('Deploy (Placeholder)') {
            steps {
                echo 'Deployment stage: This is where you would add your deployment logic.'
                echo "Image to deploy: ${DOCKER_IMAGE_NAME}:latest"
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
