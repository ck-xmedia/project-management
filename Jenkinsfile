pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.12'
        VENV_NAME = 'venv'
        PYTEST_REPORT = 'test-reports'
        COVERAGE_REPORT = 'coverage-reports'
        SONAR_PROJECT_KEY = 'project-management'
    }

    parameters {
        choice(name: 'ENVIRONMENT', choices: ['development', 'staging', 'production'], description: 'Deployment Environment')
        booleanParam(name: 'RUN_TESTS', defaultValue: true, description: 'Run Tests?')
        booleanParam(name: 'CODE_ANALYSIS', defaultValue: true, description: 'Run Code Analysis?')
    }

    options {
        timestamps()
        timeout(time: 1, unit: 'HOURS')
        disableConcurrentBuilds()
        ansiColor('xterm')
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
                    sh """
                        python${PYTHON_VERSION} -m venv ${VENV_NAME}
                        . ${VENV_NAME}/bin/activate
                        python -m pip install --upgrade pip
                        pip install -r requirements.txt
                    """
                }
            }
        }

        stage('Code Quality') {
            parallel {
                stage('Black Format Check') {
                    steps {
                        script {
                            sh """
                                . ${VENV_NAME}/bin/activate
                                pip install black
                                black --check .
                            """
                        }
                    }
                }

                stage('Ruff Linting') {
                    steps {
                        script {
                            sh """
                                . ${VENV_NAME}/bin/activate
                                pip install ruff
                                ruff check .
                            """
                        }
                    }
                }
            }
        }

        stage('Run Tests') {
            when {
                expression { params.RUN_TESTS }
            }
            steps {
                script {
                    sh """
                        . ${VENV_NAME}/bin/activate
                        mkdir -p ${PYTEST_REPORT} ${COVERAGE_REPORT}
                        pytest --junitxml=${PYTEST_REPORT}/junit.xml \
                              --cov=app \
                              --cov-report=xml:${COVERAGE_REPORT}/coverage.xml \
                              --cov-report=html:${COVERAGE_REPORT}/html
                    """
                }
            }
            post {
                always {
                    junit testResults: "${PYTEST_REPORT}/*.xml", allowEmptyResults: true
                    publishCoverage adapters: [coberturaAdapter("${COVERAGE_REPORT}/coverage.xml")]
                }
            }
        }

        stage('Security Scan') {
            when {
                expression { params.CODE_ANALYSIS }
            }
            steps {
                script {
                    sh """
                        . ${VENV_NAME}/bin/activate
                        pip install bandit safety
                        bandit -r . -f json -o bandit-report.json
                        safety check
                    """
                }
            }
        }

        stage('SonarQube Analysis') {
            when {
                expression { params.CODE_ANALYSIS }
            }
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh """
                        sonar-scanner \
                            -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                            -Dsonar.sources=. \
                            -Dsonar.python.coverage.reportPaths=${COVERAGE_REPORT}/coverage.xml \
                            -Dsonar.python.bandit.reportPaths=bandit-report.json
                    """
                }
            }
        }

        stage('Build and Package') {
            steps {
                script {
                    sh """
                        . ${VENV_NAME}/bin/activate
                        pip install build
                        python -m build
                    """
                }
                archiveArtifacts artifacts: 'dist/*', fingerprint: true
            }
        }

        stage('Deploy') {
            when {
                anyOf {
                    branch 'main'
                    branch 'release/*'
                }
            }
            steps {
                script {
                    def deployScript = """
                        . ${VENV_NAME}/bin/activate
                        echo "Deploying to ${params.ENVIRONMENT}"
                        # Add deployment steps here based on environment
                    """

                    timeout(time: 15, unit: 'MINUTES') {
                        sshagent(['deploy-key']) {
                            sh deployScript
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            cleanWs(
                deleteDirs: true,
                disableDeferredWipeout: true
            )
        }
        success {
            slackSend(
                color: 'good',
                message: "✅ Build Successful: ${env.JOB_NAME} #${env.BUILD_NUMBER}\n${env.BUILD_URL}"
            )
            emailext subject: "✅ Pipeline Successful: ${currentBuild.fullDisplayName}",
                     body: "The pipeline completed successfully.",
                     recipientProviders: [[$class: 'DevelopersRecipientProvider']]
        }
        failure {
            slackSend(
                color: 'danger',
                message: "❌ Build Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}\n${env.BUILD_URL}"
            )
            emailext subject: "❌ Pipeline Failed: ${currentBuild.fullDisplayName}",
                     body: "Please check Jenkins logs.",
                     recipientProviders: [[$class: 'DevelopersRecipientProvider']]
        }
    }
}

