// Jenkinsfile (place this in the root of your Git repository)

pipeline {
    agent any

    environment {
        // ... (existing DOCKER_REGISTRY_CREDENTIALS_ID and DOCKER_IMAGE_NAME definitions)

        // SonarQube specific definitions
        // IMPORTANT: This is the NAME of the SonarQube server configured in Jenkins
        SONARQUBE_SERVER_NAME = 'My SonarQube Server' // Use the name you gave in Jenkins global config
        // IMPORTANT: This is the CREDENTIAL ID of the SonarQube token you configured in Jenkins Credentials
        SONARQUBE_CREDENTIAL_ID = 'sonarqube-token' // <--- CHANGE THIS TO YOUR ACTUAL SONARQUBE TOKEN CREDENTIAL ID
        // IMPORTANT: This should be the Project Key you created in SonarQube UI
        SONARQUBE_PROJECT_KEY = 'my-django-app'
        // IMPORTANT: This should be the Project Name you created in SonarQube UI
        SONARQUBE_PROJECT_NAME = 'My Django App'
    }

    stages {
        // ... (Checkout, Build Docker Image, Run Basic Checks stages)

        stage('SonarQube Analysis') {
            steps {
                echo 'Running SonarQube analysis...'
                script {
                    // Use 'server' parameter for the SonarQube server NAME
                    // Use 'credentialsId' parameter for the SonarQube TOKEN CREDENTIAL ID
                    withSonarQubeEnv(server: env.SONARQUBE_SERVER_NAME, credentialsId: env.SONARQUBE_CREDENTIAL_ID, scannerHome: 'SonarScanner CLI') {
                        sh "sonar-scanner \
                            -Dsonar.projectKey=${env.SONARQUBE_PROJECT_KEY} \
                            -Dsonar.projectName=${env.SONARQUBE_PROJECT_NAME} \
                            -Dsonar.sources=./ \
                            -Dsonar.python.version=3.10"
                    }
                }
            }
        }

        // ... (SonarQube Quality Gate, Push Docker Image, Deploy stages)
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
