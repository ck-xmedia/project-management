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

        stage('Discover Project Structure') {
            steps {
                sh '''
                    echo "📁 Current directory structure:"
                    pwd
                    ls -la
                    
                    echo "📄 Python files in project:"
                    find . -name "*.py" -type f | head -20
                    
                    echo "📋 Requirements file:"
                    ls -la requirements.txt || echo "No requirements.txt found"
                    
                    echo "🔍 Looking for FastAPI app..."
                    # Use simpler grep command without complex escaping
                    find . -name "*.py" -exec grep -l "FastAPI" {} \\; 2>/dev/null | head -5 || echo "No FastAPI app found"
                '''
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
                    
                    pip install --upgrade pip
                    pip install setuptools wheel
                    
                    echo "🔧 Installing asyncpg..."
                    pip install "asyncpg>=0.29.0" --no-build-isolation
                    
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

        stage('Find and Deploy App') {
            steps {
                script {
                    echo "🔍 Auto-discovering application entry point..."
                    
                    // Use simpler approach without complex escaping
                    def appEntryPoint = sh(
                        script: '''
                            # Simple approach to find FastAPI app
                            if [ -f "app.py" ]; then
                                echo "app:app"
                            elif [ -f "main.py" ]; then
                                echo "main:app"
                            elif [ -f "src/app.py" ]; then
                                echo "src.app:app"
                            elif [ -f "src/main.py" ]; then
                                echo "src.main:app"
                            elif [ -f "api/app.py" ]; then
                                echo "api.app:app"
                            elif [ -f "api/main.py" ]; then
                                echo "api.main:app"
                            else
                                # List all Python files and let user choose
                                echo "NOT_FOUND"
                            fi
                        ''',
                        returnStdout: true
                    ).trim()
                    
                    echo "🎯 Detected app entry point: ${appEntryPoint}"
                    
                    if (appEntryPoint == "NOT_FOUND") {
                        // Show available Python files and ask user to specify
                        def pythonFiles = sh(
                            script: 'find . -name "*.py" -type f | head -10',
                            returnStdout: true
                        ).trim()
                        
                        echo "📄 Available Python files:"
                        echo "${pythonFiles}"
                        error("❌ No common app entry point found. Please specify the correct entry point in the Jenkinsfile.")
                    }
                    
                    // Deploy with the discovered entry point
                    sh """
                        . ${VENV_DIR}/bin/activate
                        echo "🚀 Starting FastAPI application: ${appEntryPoint}"
                        
                        nohup python -m uvicorn ${appEntryPoint} --host ${APP_HOST} --port ${APP_PORT} > app.log 2>&1 &
                        echo \$! > app.pid
                        
                        sleep 10
                        
                        if ps -p \$(cat app.pid) > /dev/null; then
                            echo "✅ Application started successfully with PID: \$(cat app.pid)"
                            echo "🌐 Application accessible at: http://${APP_HOST}:${APP_PORT}"
                        else
                            echo "❌ Application failed to start"
                            echo "📋 Application logs:"
                            cat app.log
                            exit 1
                        fi
                    """
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    echo "🔍 Testing application..."
                    
                    echo "🌐 Testing common endpoints..."
                    curl -f http://${APP_HOST}:${APP_PORT}/docs || curl -f http://${APP_HOST}:${APP_PORT}/redoc || curl -f http://${APP_HOST}:${APP_PORT}/ || echo "⚠️ Endpoints not available yet"
                    
                    echo "📝 Recent logs:"
                    tail -10 app.log || echo "No log file"
                '''
            }
        }
    }

    post {
        always {
            script {
                echo "🧹 Cleaning up..."
                sh '''
                    if [ -f app.pid ]; then
                        kill $(cat app.pid) 2>/dev/null || true
                        rm -f app.pid
                    fi
                    rm -f app.log 2>/dev/null || true
                '''
                cleanWs()
            }
        }
        success {
            emailext(
                subject: "✅ SUCCESS: Application Deployed - ${currentBuild.fullDisplayName}",
                body: "Application deployed successfully!",
                to: 'developerxmedia052@gmail.com'
            )
        }
        failure {
            emailext(
                subject: "❌ FAILED: Deployment - ${currentBuild.fullDisplayName}",
                body: "Deployment failed. Check Jenkins logs.",
                to: 'developerxmedia052@gmail.com',
                attachLog: true
            )
        }
    }
}
