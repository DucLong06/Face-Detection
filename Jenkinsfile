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
        DOCKER_FILE = 'Dockerfile'
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
        
        stage('Build') {
            steps {
                script {
                    sh 'pwd' 
                    sh 'ls -la'
                    echo 'Building image for deployment..'
                    def buildCmd = "-f ${DOCKER_FILE} ${DOCKER_CONTEXT}"
                    echo "Docker build command: docker build -t ${REGISTRY}:${BUILD_NUMBER} ${buildCmd}"
                    dockerImage = docker.build("${REGISTRY}:${BUILD_NUMBER}", "-f ${DOCKER_FILE} ${DOCKER_CONTEXT}")
                    docker.withRegistry( '', REGISTRY_CREDENTIAL ) {
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