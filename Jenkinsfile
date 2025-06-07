// Jenkinsfile (place this in the root of your Git repository: https://github.com/iam-dilip/my_django_app.git)

pipeline {
    agent any

    environment {
        // IMPORTANT: Replace 'dockerhub-credentials' with the actual ID of your Docker Hub credentials
        DOCKER_REGISTRY_CREDENTIALS_ID = 'dockerhub-credentials'

        // User's Docker Hub username (updated to iamdilipkumar)
        DOCKER_USER_ID = 'iamdilipkumar'
        DOCKER_IMAGE_NAME = "${env.DOCKER_USER_ID}/my-django-app"

        // SonarQube specific definitions
        SONARQUBE_SERVER_NAME = 'My SonarQube Server'
        SONARQUBE_CREDENTIAL_ID = 'sonarqube-token'
        SONARQUBE_PROJECT_KEY = 'my-django-app'
        SONARQUBE_PROJECT_NAME = 'My Django App'

        // Argo CD GitOps Repository Information
        // IMPORTANT: Replace with the clone URL of your NEW GitOps repository
        // This is a SEPARATE repo for your Kubernetes manifests (e.g., https://github.com/iam-dilip/my-django-app-k8s-manifests.git)
        GITOPS_REPO_URL = 'https://github.com/iam-dilip/my-django-app-k8s-manifests.git' // *** MAKE SURE THIS IS YOUR ACTUAL GITOPS MANIFESTS REPO ***
        GITOPS_REPO_BRANCH = 'main' // Or your desired branch in the GitOps repo
        GITOPS_MANIFEST_PATH = './' // Path within the GitOps repo where deployment.yaml resides

        // Credentials for pushing to GitOps Repo (if private)
        // If your GitOps repo is private, you'll need to create a Jenkins credential (e.g., type 'Username with password')
        // for GitHub access and replace 'YOUR_GITOPS_CREDENTIAL_ID' with that ID.
        // For a public repo, you might not need credentials here, but 'git push' might still prompt depending on setup.
        // If private, uncomment the withCredentials block in the 'Update GitOps Manifests for Argo CD' stage:
        // GITOPS_CREDENTIALS_ID = 'your-github-pat-credential-id'
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

        // NEW STAGE: Update Kubernetes Manifests in GitOps Repo for Argo CD
        stage('Update GitOps Manifests for Argo CD') {
            steps {
                echo 'Updating Kubernetes manifests in GitOps repository for Argo CD...'
                script {
                    // Create a temporary directory to clone the GitOps repo
                    dir("gitops-manifests-clone") {
                        // Clone the GitOps repository
                        // If your GitOps repo is private, uncomment the withCredentials block and replace GITOPS_CREDENTIALS_ID:
                        // withCredentials([usernamePassword(credentialsId: env.GITOPS_CREDENTIALS_ID, usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_TOKEN')]) {
                        //     sh "git clone https://\${GIT_USERNAME}:\${GIT_TOKEN}@github.com/iam-dilip/my-django-app-k8s-manifests.git ."
                        // }
                        git branch: env.GITOPS_REPO_BRANCH, url: env.GITOPS_REPO_URL

                        // Navigate into the specific path within the GitOps repo if needed
                        dir(env.GITOPS_MANIFEST_PATH) {
                            // Update the image tag in django-deployment.yaml
                            // This uses 'sed' to replace the image tag
                            // Ensure your deployment.yaml has the image line in the format: 'image: your_docker_hub_username/your_app_name:some_tag'
                            sh "sed -i 's|image: ${env.DOCKER_USER_ID}/my-django-app:.*|image: ${env.DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}|g' django-deployment.yaml"
                        }


                        // Stage and commit the changes
                        sh 'git add .'
                        sh 'git config user.email "jenkins@example.com"' // Set a dummy email for the commit
                        sh 'git config user.name "Jenkins CI/CD"'       // Set a dummy name for the commit
                        sh 'git commit -m "CI: Update Django app image to ${BUILD_NUMBER} for Argo CD"'

                        // Push the changes to the GitOps repository
                        // If private, use withCredentials:
                        // withCredentials([usernamePassword(credentialsId: env.GITOPS_CREDENTIALS_ID, usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_TOKEN')]) {
                        //     sh "git push https://\${GIT_USERNAME}:\${GIT_TOKEN}@github.com/iam-dilip/my-django-app-k8s-manifests.git ${env.GITOPS_REPO_BRANCH}"
                        // }
                        sh "git push origin ${env.GITOPS_REPO_BRANCH}" // Assuming public repo or PAT configured globally
                    }
                }
            }
        }

        // This stage now serves as a confirmation/pointer to Argo CD
        stage('Deployment Status (Managed by Argo CD)') {
            steps {
                echo 'Deployment is now managed by Argo CD. Jenkins has updated the GitOps repository.'
                echo 'Check Argo CD UI for live deployment status and health: https://localhost:8080 or https://localhost:8081' // Suggesting both for user's convenience
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
