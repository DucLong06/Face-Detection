pipeline {
    agent any

    options{
        // Max number of build logs to keep and days to keep
        buildDiscarder(logRotator(numToKeepStr: '5', daysToKeepStr: '5'))
        // Enable timestamp at each job in the pipeline
        timestamps()
    }

    environment{
        registry = 'longhd06/face-detection'
        registryCredential = 'dockerhub'      
    }

    stages {
        stage('Test') {
           
            steps {
                  sh '''
                        # Add your test commands here
                        echo 'Running tests...'
                    '''
            }
        }
        stage('Build') {
            steps {
                dir('app') {
                    script {
                        echo 'Building image for deployment..'
                        dockerImage = docker.build registry + ":$BUILD_NUMBER" 
                        echo 'Pushing image to dockerhub..'
                        docker.withRegistry( '', registryCredential ) {
                            dockerImage.push()
                            dockerImage.push('latest')
                        }
                    }
                }
            }
        }
        stage('Deploy') {
            agent {
                kubernetes {
                    containerTemplate {
                        name 'helm' // Name of the container to be used for helm upgrade
                        image 'longhd06/jenkins-docker-helm:latest' // The image containing helm
                        alwaysPullImage true // Always pull image in case of using the same tag
                    }
                }
            }
            steps {
                dir('app'){
                    script {
                        container('helm') {
                            sh("helm upgrade --install face-detection ./deployments/face-detection --namespace model-serving")
                        }
                    }
                }
            }
        }
    }
}