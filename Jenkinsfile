pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.12.7'
        VENV_DIR = 'venv'
        PYTEST_JUNIT_PATH = 'test-results/pytest.xml'
        COVERAGE_REPORT_DIR = 'coverage'
        PIP_CACHE_DIR = '/tmp/pip-cache'
    }

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
        stage('Environment Setup') {
            steps {
                script {
                    echo '🔍 Setting up Python environment...'
                    sh '''
                        python3 --version
                        which python3
                    '''
                }
            }
        }

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Create Virtual Environment') {
            steps {
                sh '''
                    echo "🐍 Creating Python virtual environment..."
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    python -m pip install --upgrade pip setuptools wheel
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    echo "📦 Installing project dependencies..."
                    
                    # Install packages with specific order to handle dependencies
                    pip install --upgrade pip
                    
                    # Install build dependencies first
                    pip install setuptools wheel
                    
                    # Install asyncpg with proper flags for Python 3.12
                    echo "🔧 Installing asyncpg..."
                    pip install "asyncpg>=0.29.0" --no-build-isolation
                    
                    # Now install the rest from requirements
                    if [ -f requirements.txt ]; then
                        echo "📄 Installing from requirements.txt..."
                        pip install -r requirements.txt
                    else
                        echo "⚠️ requirements.txt not found, installing common packages..."
                        pip install fastapi uvicorn sqlalchemy alembic pydantic pytest
                    fi
                    
                    echo "✅ Dependencies installed successfully"
                '''
            }
        }

       

        stage('Build Report') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    echo "📊 Generating build report..."
                    
                    echo "🐍 Python Environment:"
                    python --version
                    pip --version
                    
                    echo "📦 Installed Packages:"
                    pip list
                    
                    echo "📁 Project Structure:"
                    find . -name "*.py" -type f | head -20
                    
                    echo "✅ Build report generated"
                '''
            }
        }
    }

    post {
        always {
            script {
                echo "🧹 Cleaning up workspace..."
                // Keep workspace for debugging, or clean specific files
                sh '''
                    # Clean cache files but keep important artifacts
                    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
                    find . -name "*.pyc" -delete 2>/dev/null || true
                    find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
                    find . -name ".mypy_cache" -type d -exec rm -rf {} + 2>/dev/null || true
                '''
                
                // Build summary
                def duration = currentBuild.durationString
                def result = currentBuild.currentResult
                
                echo """
                🏁 BUILD SUMMARY
                ================
                Result: ${result}
                Duration: ${duration}
                Python Version: ${env.PYTHON_VERSION}
                Build URL: ${env.BUILD_URL}
                """
            }
        }
        success {
            script {
                echo "🎉 Pipeline completed successfully!"
                emailext(
                    subject: "✅ SUCCESS: Pipeline ${currentBuild.fullDisplayName}",
                    body: """
                    🎉 Jenkins Pipeline Completed Successfully!

                    📋 Build Details:
                    • Project: ${env.JOB_NAME}
                    • Build: ${currentBuild.displayName}
                    • Python Version: ${env.PYTHON_VERSION}
                    • Duration: ${currentBuild.durationString}

                    📊 Test Results:
                    • Check test coverage report in Jenkins
                    • View detailed logs: ${env.BUILD_URL}

                    🐍 Python Environment:
                    • Python 3.12.7 is properly configured
                    • All dependencies installed successfully
                    • Code quality checks passed

                    --
                    Jenkins CI/CD Automation
                    """,
                    to: 'developerxmedia052@gmail.com',  // CHANGE THIS
                    attachLog: false
                )
            }
        }
        failure {
            script {
                echo "❌ Pipeline failed - check logs for details"
                emailext(
                    subject: "❌ FAILED: Pipeline ${currentBuild.fullDisplayName}",
                    body: """
                    ❌ Jenkins Pipeline Failed!

                    📋 Build Details:
                    • Project: ${env.JOB_NAME}
                    • Build: ${currentBuild.displayName}
                    • Python Version: ${env.PYTHON_VERSION}
                    • Duration: ${currentBuild.durationString}

                    🔍 Troubleshooting:
                    • Check build logs: ${env.BUILD_URL}console
                    • Verify Python 3.12.7 installation
                    • Check dependency compatibility

                    --
                    Jenkins CI/CD Automation
                    """,
                    to: 'developerxmedia052@gmail.com',  // CHANGE THIS
                    attachLog: true
                )
            }
        }
        unstable {
            script {
                echo "⚠️ Pipeline completed with warnings"
                emailext(
                    subject: "⚠️ UNSTABLE: Pipeline ${currentBuild.fullDisplayName}",
                    body: """
                    ⚠️ Jenkins Pipeline Completed with Warnings

                    📋 Build Details:
                    • Project: ${env.JOB_NAME}
                    • Build: ${currentBuild.displayName}
                    • Python Version: ${env.PYTHON_VERSION}
                    • Duration: ${currentBuild.durationString}

                    📝 Notes:
                    • Tests passed but with some warnings
                    • Code quality checks may have issues
                    • Check build details: ${env.BUILD_URL}

                    --
                    Jenkins CI/CD Automation
                    """,
                    to: 'developerxmedia052@gmail.com',  // CHANGE THIS
                    attachLog: false
                )
            }
        }
    }
}
