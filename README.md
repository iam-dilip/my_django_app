Django CI/CD Project: Simple Web App with Automated Deployment
This project demonstrates a basic Django web application, containerized with Docker, and integrated into a Continuous Integration/Continuous Delivery (CI/CD) pipeline using Jenkins. The pipeline automates building the Docker image, running basic checks, and pushing the image to Docker Hub.

1. Project Overview
This repository contains a simple Django web application (my_django_app) that displays a "Hello World" message and a list of messages retrieved from a SQLite database. The application is designed to be easily containerized using Docker.

The core of this project's automation lies in its Jenkinsfile, which defines a multi-stage pipeline:

Checkout: Fetches the latest code from the Git repository.

Build Docker Image: Creates a Docker image for the Django application.

Run Basic Checks: Executes Django's system checks within a container to ensure project integrity.

Push Docker Image: Authenticates with Docker Hub and pushes the newly built image with both a build-specific tag and a latest tag.

Deploy (Placeholder): A stage ready for your actual deployment logic (e.g., to Kubernetes, a cloud VM).

2. Prerequisites
Before you begin, ensure you have the following installed and configured:

Git: For version control.

Python 3.x: (Recommended 3.10+) For local Django development.

pip: Python's package installer.

venv: Python's virtual environment module.

Docker: Docker Engine installed and running on your local machine and your Jenkins agent.

Docker Hub Account: A free account on hub.docker.com to store your Docker images.

Personal Access Token (PAT): Generate a PAT with Read & Write permissions from Docker Hub > Account Settings > Security. Copy this token immediately; it's only shown once.

Jenkins: A running Jenkins instance (version 2.300+ recommended for Declarative Pipelines).

Jenkins Plugins:

Git Plugin: For SCM integration.

Pipeline Plugin: Core for running pipelines.

Docker Pipeline Plugin: Essential for docker commands in Jenkinsfile.

Credentials Plugin: For managing sensitive credentials.

(Optional) Blue Ocean Plugin: For a more visual pipeline interface.

3. Local Development Setup
Follow these steps to get the Django application running on your local machine:

Clone the Repository:

git clone https://github.com/dilip10jan/my_django_app.git
cd my_django_app

Create and Activate a Virtual Environment:

python3 -m venv venv
source venv/bin/activate

Install Django and Dependencies:

pip install django
pip freeze > requirements.txt # Generate requirements.txt

Apply Database Migrations:

python manage.py makemigrations hello_app
python manage.py migrate

Create a Superuser (for Django Admin):

python manage.py createsuperuser
# Follow the prompts to set a username, email (optional), and password.

Run the Development Server:

python manage.py runserver

Access the app at http://127.0.0.1:8000/.
Access the admin panel at http://127.0.0.1:8000/admin/ and log in with your superuser credentials.

4. Dockerization
Containerize the Django application for consistent environments.

Ensure requirements.txt is Up-to-Date:
(If you added any new Python packages locally)

pip freeze > requirements.txt

Create .dockerignore:
Create a file named .dockerignore in the root of your my_django_app directory to exclude unnecessary files from the Docker image.

.git
.gitignore
*.pyc
*.log
__pycache__/
venv/
.env
db.sqlite3
media/
static_files/

Create Dockerfile:
Create a file named Dockerfile (no extension) in the root of your my_django_app directory.

# Use a slim Python base image from Debian 11 (Bullseye) or 12 (Bookworm)
# These versions include SQLite 3.31+ required by Django 5.x
FROM python:3.10-slim-bullseye # Or python:3.10-slim-bookworm

# Set the working directory inside the container
WORKDIR /app

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies, including updated SQLite3 libraries
# build-essential, libssl-dev, libffi-dev are often needed for Python package compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 libsqlite3-dev build-essential libssl-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Django project into the container
COPY . /app/

# Expose the port that Django will run on
EXPOSE 8000

# Command to run the Django application: migrate database and start the development server
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"]

Build the Docker Image Locally:

docker build -t dilip10jan/my-django-app . # Replace 'dilip10jan' with your Docker Hub username

Run the Docker Container Locally:

docker run -p 8000:8000 --name my-django-web dilip10jan/my-django-app

Access the app at http://localhost:8000/.

Create Superuser in Container (if not using persistent volume):
If you're not using a Docker volume for db.sqlite3, the superuser created locally won't be in the container's database. Create one inside the running container:

docker exec -it my-django-web python manage.py createsuperuser
# Follow prompts to create username/password

Then log in to http://localhost:8000/admin/ with these new credentials.

5. CI/CD with Jenkins
This section details how to set up the Jenkins pipeline to automate the build and push process.

5.1. Docker Hub Setup
Create Repository: Log in to hub.docker.com and create a public repository named my-django-app under your username (e.g., dilip10jan/my-django-app). Ensure the name matches exactly, including casing.

Generate PAT: If you haven't already, generate a Personal Access Token (PAT) with Read & Write permissions from Docker Hub > Account Settings > Security.

5.2. Jenkins Credentials Configuration
Log in to Jenkins as an administrator.

Navigate to Manage Jenkins > Manage Credentials.

Click on (your Jenkins domain/store) > Global credentials (unrestricted).

Click Add Credentials.

Kind: Username with password

Scope: Global

Username: Your Docker Hub Username (e.g., dilip10jan)

Password: Your Docker Hub Personal Access Token (PAT)

ID: dockerhub-credentials (This ID is used in the Jenkinsfile and must match exactly).

Description: (Optional) e.g., "Docker Hub PAT for CI/CD".

Click Create.

5.3. Jenkins Job Configuration
Create a New Jenkins Job:

From the Jenkins dashboard, click New Item.

Enter an item name (e.g., my-django-app-pipeline).

Select Pipeline and click OK.

Configure the Pipeline:

In the job configuration page, scroll down to the Pipeline section.

Select Pipeline script from SCM.

SCM: Git

Repository URL: https://github.com/dilip10jan/my_django_app.git (Replace with your actual repository URL).

Credentials: Select None if your GitHub repo is public. If private, add GitHub credentials here.

Branches to build: */main (or your main branch name).

Script Path: Jenkinsfile (This is the default and should match the file you created in your repo).

Save the Job Configuration.

5.4. Running the Pipeline
Commit and Push Jenkinsfile: Ensure the Jenkinsfile (provided below) is in the root of your my_django_app repository and pushed to your main branch.

// Jenkinsfile (place this in the root of your Git repository)

// Define the Docker registry credentials ID.
def DOCKER_REGISTRY_CREDENTIALS_ID = 'dockerhub-credentials'

// Define your Docker image name.
def DOCKER_IMAGE_NAME = 'dilip10jan/my-django-app' // IMPORTANT: Change 'dilip10jan' to your Docker Hub username!

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

Run the Job:

In Jenkins, open your my-django-app-pipeline job.

Click Build Now from the left-hand menu.

6. Verification
After the Jenkins pipeline completes successfully:

Check Jenkins Build Status: The build should show as SUCCESS (green).

Inspect Jenkins Logs: Review the console output for each stage to ensure all steps executed as expected.

Verify Docker Image on Docker Hub:

Go to hub.docker.com and log in.

Navigate to your dilip10jan/my-django-app repository.

You should see at least two tags:

A tag corresponding to your Jenkins build number (e.g., 21).

The latest tag.

Pull and Run the Image (Optional):
You can pull the image from Docker Hub to confirm it runs:

docker pull dilip10jan/my-django-app:latest
docker run -p 8000:8000 --name my-django-hub-app dilip10jan/my-django-app:latest

Then access http://localhost:8000/.

7. Troubleshooting Tips
NameError: name 'include' is not defined: Ensure from django.urls import path, include in your myproject/urls.py.

TemplateDoesNotExist: Verify your template path is hello_app/templates/hello_app/hello_world.html. Django requires the nested app-name directory within templates/.

SQLite 3.31 or later is required: Update your Dockerfile base image to a newer Debian version, e.g., FROM python:3.10-slim-bullseye or python:3.10-slim-bookworm.

port is already allocated: Another process (like a previously run Docker container or local Django server) is using port 8000.

Find and stop/kill the process: sudo lsof -i :8000 then sudo kill -9 <PID>.

Stop/remove all Docker containers: docker stop $(docker ps -aq) && docker rm $(docker ps -aq).

No such property: docker or No such DSL method 'withRegistry':

Ensure the Docker Pipeline plugin is installed in Jenkins (Manage Jenkins > Plugins > Available Plugins).

Perform a full Jenkins restart (Your_Jenkins_URL/restart).

Check Manage Jenkins > In-process Script Approval for any pending approvals related to Docker.

denied: requested access to the resource is denied / unauthorized: authentication required during push:

Crucial: You must use a Docker Hub Personal Access Token (PAT) for Jenkins credentials, not your regular Docker Hub password.

Ensure the PAT has Read & Write permissions.

Verify the Docker Hub repository (dilip10jan/my-django-app) exists and is Public on hub.docker.com.

Double-check that the DOCKER_IMAGE_NAME in your Jenkinsfile exactly matches your Docker Hub username and repository name.

Re-enter your Docker Hub credentials in Jenkins carefully.

The Jenkinsfile provided in this README uses explicit docker login and docker push commands within withCredentials, which is a robust workaround for withDockerRegistry issues.

8. Future Enhancements
Automated Testing: Integrate pytest or Django's built-in test runner into the "Run Basic Checks" stage for more comprehensive testing.

Code Quality Checks: Add stages for linting (e.g., flake8, black) or security scanning (e.g., bandit).

Deployment Stage: Implement actual deployment to a target environment (e.g., Kubernetes, AWS ECS, Azure Container Instances).

Notifications: Configure Jenkins to send email or Slack notifications on build success/failure.

Database Migration Management: For production, consider external databases (PostgreSQL) and more robust migration strategies.

Docker Compose: Use docker-compose.yml for local multi-service development (e.g., Django + PostgreSQL).

Semantic Versioning: Implement a more sophisticated tagging strategy (e.g., v1.0.0, v1.0.1-rc1) instead of just latest and build numbers.
