pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.12'
        PIP_CACHE_DIR = '.pip-cache'
        PYTEST_JUNIT_PATH = 'test-results/pytest-results.xml'
        COVERAGE_REPORT_PATH = 'coverage-reports/'
        VENV_PATH = 'venv'
    }
    
    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                script {
                    if (isUnix()) {
                        sh """
                            python${PYTHON_VERSION} -m venv ${VENV_PATH}
                            . ${VENV_PATH}/bin/activate
                            python -m pip install --upgrade pip
                        """
                    } else {
                        bat """
                            python -m venv ${VENV_PATH}
                            ${VENV_PATH}\\Scripts\\activate.bat
                            python -m pip install --upgrade pip
                        """
                    }
                }
            }
        }
        
        stage('Install Dependencies') {
            steps {
                script {
                    if (isUnix()) {
                        sh """
                            . ${VENV_PATH}/bin/activate
                            pip install -r requirements.txt
                        """
                    } else {
                        bat """
                            ${VENV_PATH}\\Scripts\\activate.bat
                            pip install -r requirements.txt
                        """
                    }
                }
            }
        }
        
        stage('Code Quality') {
            parallel {
                stage('Black Format Check') {
                    steps {
                        script {
                            if (isUnix()) {
                                sh """
                                    . ${VENV_PATH}/bin/activate
                                    pip install black
                                    black --check .
                                """
                            } else {
                                bat """
                                    ${VENV_PATH}\\Scripts\\activate.bat
                                    pip install black
                                    black --check .
                                """
                            }
                        }
                    }
                }
                
                stage('Ruff Linting') {
                    steps {
                        script {
                            if (isUnix()) {
                                sh """
                                    . ${VENV_PATH}/bin/activate
                                    pip install ruff
                                    ruff check .
                                """
                            } else {
                                bat """
                                    ${VENV_PATH}\\Scripts\\activate.bat
                                    pip install ruff
                                    ruff check .
                                """
                            }
                        }
                    }
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                script {
                    if (isUnix()) {
                        sh """
                            . ${VENV_PATH}/bin/activate
                            mkdir -p test-results coverage-reports
                            pytest --junitxml=${PYTEST_JUNIT_PATH} --cov=app --cov-report=xml:${COVERAGE_REPORT_PATH}/coverage.xml --cov-report=html:${COVERAGE_REPORT_PATH}/html
                        """
                    } else {
                        bat """
                            ${VENV_PATH}\\Scripts\\activate.bat
                            if not exist test-results mkdir test-results
                            if not exist coverage-reports mkdir coverage-reports
                            pytest --junitxml=${PYTEST_JUNIT_PATH} --cov=app --cov-report=xml:${COVERAGE_REPORT_PATH}/coverage.xml --cov-report=html:${COVERAGE_REPORT_PATH}/html
                        """
                    }
                }
            }
            post {
                always {
                    junit testResults: 'test-results/pytest-results.xml'
                }
            }
        }
    }
    
    post {
        always {
            cleanWs(
                cleanWhenNotBuilt: false,
                deleteDirs: true,
                disableDeferredWipeout: true,
                patterns: [
                    [pattern: '**/__pycache__/**', type: 'INCLUDE'],
                    [pattern: '**/*.pyc', type: 'INCLUDE'],
                    [pattern: '**/venv/**', type: 'INCLUDE'],
                    [pattern: '.pytest_cache/**', type: 'INCLUDE'],
                    [pattern: '.coverage', type: 'INCLUDE']
                ]
            )
        }
        success {
            script {
                if (env.BRANCH_NAME == 'main') {
                    slackSend(
                        color: 'good',
                        message: "Build Successful: ${env.JOB_NAME} #${env.BUILD_NUMBER}\nMore info at: ${env.BUILD_URL}"
                    )
                }
            }
        }
        failure {
            script {
                slackSend(
                    color: 'danger',
                    message: "Build Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}\nMore info at: ${env.BUILD_URL}"
                )
                
                emailext(
                    subject: "Build Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                    body: """
                        Build failed for ${env.JOB_NAME} #${env.BUILD_NUMBER}
                        
                        Check console output at: ${env.BUILD_URL}
                    """,
                    recipientProviders: [[$class: 'DevelopersRecipientProvider']]
                )
            }
        }
    }
}