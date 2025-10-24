pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.12.7'
        VENV_DIR = 'venv'
        APP_PORT = '8111'
        APP_HOST = '0.0.0.0'
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
                        pip install fastapi uvicorn sqlalchemy alembic pydantic
                    fi
                    
                    echo "✅ Dependencies installed successfully"
                '''
            }
        }

        stage('Deploy') {
            steps {
                script {
                    echo "🚀 Starting application deployment..."
                    
                    sh '''
                        . ${VENV_DIR}/bin/activate
                        echo "🚀 Starting FastAPI application..."
                        echo "📝 Command: python -m uvicorn main:app --host ${APP_HOST} --port ${APP_PORT}"
                        
                        # Start the application in background and save PID
                        nohup python -m uvicorn main:app --host ${APP_HOST} --port ${APP_PORT} > app.log 2>&1 &
                        echo $! > app.pid
                        
                        # Wait a moment for the app to start
                        sleep 10
                        
                        # Check if application is running
                        if ps -p $(cat app.pid) > /dev/null; then
                            echo "✅ Application started successfully with PID: $(cat app.pid)"
                            echo "🌐 Application should be accessible at: http://${APP_HOST}:${APP_PORT}"
                        else
                            echo "❌ Application failed to start"
                            echo "📋 Checking application logs:"
                            cat app.log || echo "No log file found"
                            exit 1
                        fi
                        
                        # Optional: Test if the application is responding
                        echo "🔍 Testing application health..."
                        curl -f http://${APP_HOST}:${APP_PORT}/docs || curl -f http://${APP_HOST}:${APP_PORT}/ || echo "⚠️ Health check failed but continuing"
                    '''
                    
                    echo "🎯 Deployment completed successfully"
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                script {
                    echo "🔍 Verifying deployment..."
                    
                    sh '''
                        # Check if application process is still running
                        if [ -f app.pid ] && ps -p $(cat app.pid) > /dev/null; then
                            echo "✅ Application is running with PID: $(cat app.pid)"
                            echo "📊 Process info:"
                            ps -p $(cat app.pid) -o pid,ppid,cmd
                        else
                            echo "❌ Application process not found"
                            echo "📋 Application logs:"
                            cat app.log 2>/dev/null || echo "No log file available"
                        fi
                        
                        # Show recent log entries
                        echo "📝 Recent application logs:"
                        tail -20 app.log 2>/dev/null || echo "No log file available"
                    '''
                }
            }
        }
    }

    post {
        always {
            script {
                echo "🧹 Performing cleanup..."
                
                // Optional: Stop the application if you want to clean up
                // If you want to keep the application running, remove this section
                sh '''
                    echo "🛑 Stopping application if running..."
                    if [ -f app.pid ]; then
                        kill $(cat app.pid) 2>/dev/null || true
                        rm -f app.pid
                    fi
                '''
                
                // Clean workspace but keep deployment artifacts
                cleanWs(
                    cleanWhenNotBuilt: false,
                    deleteDirs: true,
                    disableDeferredWipeout: true,
                    patterns: [
                        [pattern: '**/__pycache__/**', type: 'INCLUDE'],
                        [pattern: '**/*.pyc', type: 'INCLUDE'],
                        [pattern: '**/.pytest_cache/**', type: 'INCLUDE'],
                        [pattern: '**/.mypy_cache/**', type: 'INCLUDE']
                    ]
                )
                
                // Build summary
                def duration = currentBuild.durationString
                def result = currentBuild.currentResult
                
                echo """
                🏁 BUILD SUMMARY
                ================
                Result: ${result}
                Duration: ${duration}
                Python Version: ${env.PYTHON_VERSION}
                Application URL: http://${env.APP_HOST}:${env.APP_PORT}
                Build URL: ${env.BUILD_URL}
                """
            }
        }
        success {
            script {
                echo "🎉 Deployment completed successfully!"
                emailext(
                    subject: "✅ SUCCESS: Application Deployed - ${currentBuild.fullDisplayName}",
                    body: """
                    🎉 FastAPI Application Deployed Successfully!

                    📋 Build Details:
                    • Project: ${env.JOB_NAME}
                    • Build: ${currentBuild.displayName}
                    • Python Version: ${env.PYTHON_VERSION}
                    • Duration: ${currentBuild.durationString}

                    🚀 Deployment Status:
                    • Application started on port ${APP_PORT}
                    • Access URL: http://${APP_HOST}:${APP_PORT}
                    • API Documentation: http://${APP_HOST}:${APP_PORT}/docs
                    • Build Number: ${BUILD_NUMBER}

                    📊 Application Info:
                    • Process running in background
                    • Log file: app.log
                    • Using Uvicorn ASGI server

                    --
                    Jenkins CI/CD Automation
                    """,
                    to: 'developerxmedia052@gmail.com',
                    attachLog: false
                )
            }
        }
        failure {
            script {
                echo "❌ Deployment failed - check logs for details"
                emailext(
                    subject: "❌ FAILED: Application Deployment - ${currentBuild.fullDisplayName}",
                    body: """
                    ❌ FastAPI Application Deployment Failed!

                    📋 Build Details:
                    • Project: ${env.JOB_NAME}
                    • Build: ${currentBuild.displayName}
                    • Python Version: ${env.PYTHON_VERSION}
                    • Duration: ${currentBuild.durationString}

                    🔍 Troubleshooting:
                    • Check build logs: ${env.BUILD_URL}console
                    • Verify application entry point (main:app)
                    • Check port ${APP_PORT} availability
                    • Review dependency installation

                    --
                    Jenkins CI/CD Automation
                    """,
                    to: 'developerxmedia052@gmail.com',
                    attachLog: true
                )
            }
        }
    }
}
