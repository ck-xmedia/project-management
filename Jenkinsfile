pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.12'
        PIP_CACHE_DIR = '~/.cache/pip'
        VENV_DIR = 'venv'
        PYTEST_JUNIT_PATH = 'test-results/pytest.xml'
        COVERAGE_REPORT_DIR = 'coverage'
    }

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
    }

    stages {
        stage('Environment Setup') {
            steps {
                script {
                    echo '🔍 Checking required environments...'

                    // Check Python version
                    def pythonInstalled = false
                    def pythonVersionCorrect = false

                    try {
                        def pythonVersion = sh(
                            script: 'python3 --version',
                            returnStdout: true
                        ).trim()

                        echo "✅ Found Python: ${pythonVersion}"
                        pythonInstalled = true

                        def versionMatch = pythonVersion =~ /Python (\d+\.\d+\.\d+)/
                        if (versionMatch) {
                            def currentVersion = versionMatch[0][1]
                            def requiredVersion = '3.12'

                            def currentParts = currentVersion.tokenize('.')
                            def requiredParts = requiredVersion.tokenize('.')

                            def versionOk = true
                            for (int i = 0; i < Math.min(currentParts.size(), requiredParts.size()); i++) {
                                if (currentParts[i].toInteger() < requiredParts[i].toInteger()) {
                                    versionOk = false
                                    break
                                } else if (currentParts[i].toInteger() > requiredParts[i].toInteger()) {
                                    break
                                }
                            }

                            if (versionOk) {
                                pythonVersionCorrect = true
                            }
                        }
                    } catch (Exception e) {
                        echo "❌ Python not found: ${e.message}"
                    }

                    if (!pythonInstalled || !pythonVersionCorrect) {
                        echo "📦 Installing Python 3.12..."
                        try {
                            sh 'sudo apt-get update'
                            sh 'sudo add-apt-repository -y ppa:deadsnakes/ppa'
                            sh 'sudo apt-get update'
                            sh 'sudo apt-get install -y python3.12 python3.12-venv python3.12-dev'
                            echo "✅ Python 3.12 installed successfully1"
                        } catch (Exception e) {
                            error("Failed to install Python 3.12: ${e.message}")
                        }
                    }
                }
            }
        }

        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/ck-xmedia/project-management.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'python3 -m venv ${VENV_DIR}'
                sh '''
                    source ${VENV_DIR}/bin/activate
                    python3 -m pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Code Quality') {
            steps {
                sh '''
                    source ${VENV_DIR}/bin/activate
                    pip install black ruff
                    black --check .
                    ruff check .
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    source ${VENV_DIR}/bin/activate
                    mkdir -p test-results
                    pytest --junitxml=${PYTEST_JUNIT_PATH} --cov=app --cov-report=xml:${COVERAGE_REPORT_DIR}/coverage.xml --cov-report=html:${COVERAGE_REPORT_DIR}/html
                '''
            }
            post {
                always {
                    junit testResults: "${PYTEST_JUNIT_PATH}", allowEmptyResults: true
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
                    [pattern: '**/venv/**', type: 'INCLUDE'],
                    [pattern: '**/__pycache__/**', type: 'INCLUDE'],
                    [pattern: '**/*.pyc', type: 'INCLUDE'],
                    [pattern: '**/test-results/**', type: 'INCLUDE'],
                    [pattern: '**/coverage/**', type: 'INCLUDE']
                ]
            )
        }
        success {
            emailext(
                subject: "Pipeline Successful: ${currentBuild.fullDisplayName}",
                body: "The pipeline completed successfully.",
                recipientProviders: [[$class: 'DevelopersRecipientProvider']]
            )
        }
        failure {
            emailext(
                subject: "Pipeline Failed: ${currentBuild.fullDisplayName}",
                body: "The pipeline failed. Please check the build logs.",
                recipientProviders: [[$class: 'DevelopersRecipientProvider']]
            )
        }
    }
}
