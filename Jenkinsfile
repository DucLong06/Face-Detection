pipeline {
    agent any
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '5', daysToKeepStr: '5'))
        timestamps()
    }
    
    environment {
        REGISTRY = 'longhd06/face-detection'
        REGISTRY_CREDENTIAL = 'dockerhub'
        DOCKER_CONTEXT= '.'
        DOCKER_FILE = 'app/'
        HELM_FACE_DETECTION_PATH = 'app/deployments/face-detection'
        HELM_NGINX_PATH = 'app/deployments/nginx-ingress'
    }
    
    stages {
        stage('Test') {
            steps {
                dir('app') {
                    sh '''
                        # Add your test commands here
                        echo 'Running tests...'
                        # Example: python -m pytest src/tests/
                    '''
                }
            }
        }
        
        stage('Build and Push Docker Image') {
            steps {
                script {
                  dir('app') {
                    echo 'Building Docker image...'
                    dockerImage = docker.build ("${REGISTRY}:$BUILD_NUMBER","-f dockerfile .")
                  }
               
                    // Push Docker image
                    echo 'Pushing Docker image to registry...'
                    docker.withRegistry('', REGISTRY_CREDENTIAL) {
                        dockerImage.push()
                        dockerImage.push('latest')
                    }
                }
            }
        }
        
        // stage('Deploy to Kubernetes') {
        //     agent {
        //         kubernetes {
        //             containerTemplate {
        //                 name 'helm'
        //                 image "${REGISTRY}:latest"
        //                 alwaysPullImage true
        //             }
        //         }
        //     }
        //     steps {
        //         script {
        //             container('helm') {
        //                 // Deploy Face Detection application
        //                 sh """
        //                     helm upgrade --install face-detection \
        //                         ${HELM_FACE_DETECTION_PATH} \
        //                         --namespace model-serving \
        //                         --create-namespace
        //                 """
                        
        //                 // Deploy Nginx Ingress
        //                 sh """
        //                     helm upgrade --install nginx-ingress \
        //                         ${HELM_NGINX_PATH} \
        //                         --namespace ingress-nginx \
        //                         --create-namespace
        //                 """
        //             }
        //         }
        //     }
        // }
    }
    
 
}