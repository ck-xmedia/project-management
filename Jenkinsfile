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
                    
                    echo "🔍 Looking for FastAPI app entry points..."
                    find . -name "*.py" -type f -exec grep -l "FastAPI\|app = FastAPI" {} \\; 2>/dev/null || echo "No FastAPI app found in Python files"
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
                    
                    // First, try to find the correct app entry point
                    def appEntryPoint = sh(
                        script: '''
                            # Look for common FastAPI patterns
                            if [ -f "app.py" ] && grep -q "FastAPI" app.py; then
                                echo "app:app"
                            elif [ -f "main.py" ] && grep -q "FastAPI" main.py; then
                                echo "main:app"
                            elif [ -f "src/main.py" ] && grep -q "FastAPI" src/main.py; then
                                echo "src.main:app"
                            elif [ -f "api/main.py" ] && grep -q "FastAPI" api/main.py; then
                                echo "api.main:app"
                            else
                                # Find first Python file with FastAPI
                                FILE=$(find . -name "*.py" -type f -exec grep -l "FastAPI" {} \\; | head -1)
                                if [ -n "$FILE" ]; then
                                    # Convert file path to module path
                                    MODULE_PATH=$(echo "$FILE" | sed 's/\.py$//' | sed 's/^\.\\///' | tr '/' '.')
                                    echo "${MODULE_PATH}:app"
                                else
                                    echo "NOT_FOUND"
                                fi
                            fi
                        ''',
                        returnStdout: true
                    ).trim()
                    
                    echo "🎯 Detected app entry point: ${appEntryPoint}"
                    
                    if (appEntryPoint == "NOT_FOUND") {
                        error("❌ No FastAPI application found. Please check your project structure.")
                    }
                    
                    // Now deploy with the discovered entry point
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
                    
                    # Try multiple common endpoints
                    echo "🌐 Testing /docs endpoint..."
                    curl -f http://${APP_HOST}:${APP_PORT}/docs || echo "⚠️ /docs not available"
                    
                    echo "🌐 Testing /redoc endpoint..."
                    curl -f http://${APP_HOST}:${APP_PORT}/redoc || echo "⚠️ /redoc not available"
                    
                    echo "🌐 Testing root endpoint..."
                    curl -f http://${APP_HOST}:${APP_PORT}/ || echo "⚠️ Root endpoint not available"
                    
                    echo "📝 Recent logs:"
                    tail -10 app.log
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
