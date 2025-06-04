// Jenkinsfile (place this in the root of your Git repository)

// Define the Docker registry credentials ID.
// IMPORTANT: Replace 'dockerhub-credentials' with the actual ID of your Docker Hub credentials
// configured in Jenkins (e.g., a 'Username with password' credential).
def DOCKER_REGISTRY_CREDENTIALS_ID = 'dockerhub-credentials'

// Define your Docker image name.
// IMPORTANT: Change 'dilip10jan' to your actual Docker Hub username!
def DOCKER_IMAGE_NAME = 'dilip10jan/my-django-app'

pipeline {
    agent any // You can specify a more specific agent if you have labels (e.g., agent { label 'docker-agent' })

    stages {
        stage('Checkout') {
            steps {
                echo 'Cloning the Git repository...'
                // 'checkout scm' automatically checks out the code configured in the Jenkins job
                // Or specify your repository explicitly:
                git branch: 'main', url: 'https://github.com/dilip10jan/my_django_app.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building the Docker image...'
                script {
                    // Build the Docker image, tagging it with the current build number and 'latest'
                    docker.build("${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}", ".")
                    docker.build("${DOCKER_IMAGE_NAME}:latest", ".")
                }
            }
        }

        stage('Run Basic Checks') {
            steps {
                echo 'Running basic Django checks inside a temporary container...'
                script {
                    // Run Django's system checks in a temporary container
                    // The '\$(pwd)' is escaped to be correctly interpreted by the shell, not Groovy.
                    sh "docker run --rm -v \$(pwd):/app ${DOCKER_IMAGE_NAME}:latest python manage.py check"
                }
            }
        }

                stage('Push Docker Image') {
            steps {
                echo 'Attempting push with explicit docker login and push commands...'
                script {
                    // --- EXPLICIT LOGIN AND PUSH BLOCK ---
                    // This block will perform a direct 'docker login' and then 'docker push'
                    // commands, bypassing the withDockerRegistry step which seems to be problematic.
                    withCredentials([usernamePassword(credentialsId: DOCKER_REGISTRY_CREDENTIALS_ID, passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                        // 1. Perform a direct docker login using the credentials
                        // This ensures the Docker daemon has the necessary authentication token.
                        sh "echo \"$DOCKER_PASSWORD\" | docker login -u \"$DOCKER_USERNAME\" --password-stdin"

                        // 2. Perform the docker push commands directly
                        echo 'Executing docker push for specific build number...'
                        sh "docker push ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}"

                        echo 'Executing docker push for latest tag...'
                        sh "docker push ${DOCKER_IMAGE_NAME}:latest"
                    }
                    // --- END EXPLICIT LOGIN AND PUSH BLOCK ---

                    // REMOVE OR COMMENT OUT THE OLD withDockerRegistry BLOCK.
                    // It is no longer needed, as we are doing the push explicitly above.
                    /*
                    withDockerRegistry(url: "https://registry.hub.docker.com", credentialsId: DOCKER_REGISTRY_CREDENTIALS_ID) {
                        docker.image("${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}").push()
                        docker.image("${DOCKER_IMAGE_NAME}:latest").push()
                    }
                    */
                }
            }
        }

        stage('Deploy (Placeholder)') {
            steps {
                echo 'Deployment stage: This is where you would add your deployment logic.'
                echo 'For example, deploying to Kubernetes, a cloud VM, or another environment.'
                echo "Image to deploy: ${DOCKER_IMAGE_NAME}:latest"
                // Example:
                // sh 'kubectl apply -f k8s-deployment.yaml'
                // sh 'ansible-playbook deploy.yml'
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished.'
            // Optional: Clean up Docker images if needed (use with caution in production)
            // sh "docker rmi ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}"
            // sh "docker rmi ${DOCKER_IMAGE_NAME}:latest"
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check logs for details.'
        }
    }
}
