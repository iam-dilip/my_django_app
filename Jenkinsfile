// Jenkinsfile (place this in the root of your Git repository)

// Define the Docker registry credentials ID if you plan to push to a private registry
// Replace 'dockerhub-credentials' with the actual ID of your Docker Hub credentials
// configured in Jenkins (e.g., Username with password).
def DOCKER_REGISTRY_CREDENTIALS_ID = 'dockerhub-credentials' // IMPORTANT: Change this!
def DOCKER_IMAGE_NAME = 'dilip10jan/my-django-app' // IMPORTANT: Change 'dilip10jan' to your Docker Hub username!

pipeline {
    agent any // You can specify a more specific agent if you have labels (e.g., agent { label 'docker-agent' })

    stages {
        stage('Checkout') {
            steps {
                echo 'Cloning the Git repository...'
                // Assumes your Jenkins project is configured to use SCM (Git)
                // 'checkout scm' automatically checks out the code configured in the job
                git branch: 'main', url: 'https://github.com/dilip10jan/my_django_app.git' // Replace with your actual repo URL if different
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building the Docker image...'
                script {
                    // Build the Docker image
                    // The '.' refers to the current directory (where Jenkins checked out the code)
                    // The image will be tagged with the DOCKER_IMAGE_NAME and the current build number
                    docker.build("${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}", ".")
                    docker.build("${DOCKER_IMAGE_NAME}:latest", ".") // Also tag as latest
                }
            }
        }

        stage('Run Basic Checks') {
            steps {
                echo 'Running basic Django checks inside a temporary container...'
                script {
                    // Run Django's system checks in a temporary container
                    // This ensures the project is configured correctly before deployment
                    // --rm removes the container after it exits
                    // -v $(pwd):/app mounts the current workspace into the container
                    // This assumes the base image used for building has python and manage.py available
                    sh "docker run --rm -v \$(pwd):/app ${DOCKER_IMAGE_NAME}:latest python manage.py check"
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                echo 'Pushing Docker image to registry...'
                script {
                    // Use withRegistry to authenticate with Docker Hub
                    // You need to configure a 'Username with password' credential in Jenkins
                    // with your Docker Hub username and Personal Access Token (PAT)
                    // and use its ID here.
                    withRegistry("https://registry.hub.docker.com", dockerhub-credentials) {
                        docker.image("${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}").push()
                        docker.image("${DOCKER_IMAGE_NAME}:latest").push()
                    }
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished.'
            // Clean up Docker images if needed (use with caution in production)
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
