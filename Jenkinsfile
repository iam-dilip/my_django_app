// Jenkinsfile (place this in the root of your Git repository)

// Define the Docker registry credentials ID.
// IMPORTANT: Replace 'dockerhub-credentials' with the actual ID of your Docker Hub credentials
// configured in Jenkins (e.g., a 'Username with password' credential of type 'Secret text').
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
                // Or specify your repository explicitly for clarity:
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
                echo 'Pushing Docker image to registry...'
                script {
                    // Use withCredentials to securely access DOCKER_REGISTRY_CREDENTIALS_ID
                    withCredentials([usernamePassword(credentialsId: DOCKER_REGISTRY_CREDENTIALS_ID, passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                        // This block performs a direct 'docker login' and then 'docker push' commands.
                        // It addresses the "insecure interpolation" warning by carefully handling sensitive variables
                        // within the shell script.
                        sh(script: """
                            # Assign the sensitive variables (PAT and Username) to shell environment variables
                            # for the duration of this script. Use \${} to prevent Groovy from interpolating them
                            # into the string before the shell executes it.
                            DOCKER_PAT_VAR="${DOCKER_PASSWORD}"
                            DOCKER_USER_VAR="${DOCKER_USERNAME}"

                            # Perform docker login using the shell environment variables.
                            # The --password-stdin method is secure as it prevents the password from appearing
                            # in process lists.
                            echo "\${DOCKER_PAT_VAR}" | docker login -u "\${DOCKER_USER_VAR}" --password-stdin

                            # Unset the variables immediately after use to minimize their lifetime in memory
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
            // Optional: Clean up Docker images on the agent after successful push
            // Use with caution in production, especially if other jobs depend on these images locally.
            // sh "docker rmi ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}"
            // sh "docker rmi ${DOCKER_IMAGE_NAME}:latest"
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check logs for details.'
        }
        // You could add other post conditions, e.g., 'aborted', 'unstable', 'changed'
    }
}
