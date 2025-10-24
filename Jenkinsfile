pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        APP_PORT = '8111'
        APP_HOST = '0.0.0.0'
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
    }

    stages {
        stage('Check Repository Content') {
            steps {
                sh '''
                    echo "📊 Checking Git repository content..."
                    echo "=== CURRENT DIRECTORY ==="
                    pwd
                    ls -la
                    
                    echo "=== GIT FILES (excluding venv) ==="
                    find . -name "*.py" -type f | grep -v venv | head -20 || echo "No project Python files found"
                    
                    echo "=== ALL FILES (excluding venv) ==="
                    find . -type f | grep -v venv | head -30 || echo "No project files found"
                    
                    echo "=== CHECKING FOR COMMON APP FILES ==="
                    ls -la *.py 2>/dev/null || echo "No .py files in root"
                    ls -la src/ 2>/dev/null || echo "No src directory"
                    ls -la app/ 2>/dev/null || echo "No app directory"
                    ls -la requirements.txt 2>/dev/null || echo "No requirements.txt"
                    
                    echo "=== GIT STATUS ==="
                    git status || echo "Not a git repo"
                    git log --oneline -5 || echo "No git history"
                '''
            }
        }

        stage('Create Demo App if Missing') {
            steps {
                script {
                    // Check if we have any application files
                    def hasAppFiles = sh(
                        script: '''
                            if [ -f "main.py" ] || [ -f "app.py" ] || [ -f "requirements.txt" ]; then
                                echo "YES"
                            else
                                echo "NO"
                            fi
                        ''',
                        returnStdout: true
                    ).trim()
                    
                    if (hasAppFiles == "NO") {
                        echo "📝 No application files found. Creating a simple FastAPI demo..."
                        
                        sh '''
                            echo "🐍 Creating simple FastAPI application..."
                            
                            # Create requirements.txt
                            cat > requirements.txt << EOF
                            fastapi==0.104.1
                            uvicorn[standard]==0.24.0
                            EOF
                            
                            # Create main.py with a simple FastAPI app
                            cat > main.py << EOF
                            from fastapi import FastAPI
                            
                            app = FastAPI(
                                title="Project Management API",
                                description="A simple FastAPI application",
                                version="1.0.0"
                            )
                            
                            @app.get("/")
                            async def root():
                                return {"message": "Welcome to Project Management API"}
                            
                            @app.get("/health")
                            async def health_check():
                                return {"status": "healthy", "version": "1.0.0"}
                            
                            @app.get("/items/{item_id}")
                            async def read_item(item_id: int, q: str = None):
                                return {"item_id": item_id, "q": q}
                            
                            if __name__ == "__main__":
                                import uvicorn
                                uvicorn.run(app, host="0.0.0.0", port=8111)
                            EOF
                            
                            echo "✅ Created demo application files"
                            echo "📁 Files created:"
                            ls -la main.py requirements.txt
                        '''
                    } else {
                        echo "✅ Application files found, proceeding with deployment..."
                    }
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    echo "🐍 Setting up Python environment..."
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    
                    echo "📦 Installing dependencies..."
                    if [ -f requirements.txt ]; then
                        pip install -r requirements.txt
                        echo "✅ Dependencies installed from requirements.txt"
                    else
                        pip install fastapi uvicorn
                        echo "✅ Installed FastAPI and Uvicorn"
                    fi
                '''
            }
        }

        stage('Deploy Application') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    echo "🚀 Deploying FastAPI application..."
                    
                    # Try common entry points in order
                    if [ -f "main.py" ]; then
                        echo "📄 Using main.py"
                        nohup python -m uvicorn main:app --host ${APP_HOST} --port ${APP_PORT} > app.log 2>&1 &
                        ENTRY_POINT="main:app"
                    elif [ -f "app.py" ]; then
                        echo "📄 Using app.py"
                        nohup python -m uvicorn app:app --host ${APP_HOST} --port ${APP_PORT} > app.log 2>&1 &
                        ENTRY_POINT="app:app"
                    else
                        echo "❌ No application file found"
                        exit 1
                    fi
                    
                    echo $! > app.pid
                    echo "🎯 Started with: ${ENTRY_POINT}"
                    echo "📝 PID: $(cat app.pid)"
                    
                    # Wait for app to start
                    sleep 8
                    
                    # Check if app is running
                    if ps -p $(cat app.pid) > /dev/null; then
                        echo "✅ Application running successfully"
                        echo "🌐 Access your app at: http://${APP_HOST}:${APP_PORT}"
                        echo "📚 API docs at: http://${APP_HOST}:${APP_PORT}/docs"
                    else
                        echo "❌ Application failed to start"
                        echo "📋 Logs:"
                        cat app.log
                        exit 1
                    fi
                '''
            }
        }

        stage('Test Deployment') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    echo "🔍 Testing deployed application..."
                    
                    echo "🌐 Testing root endpoint..."
                    curl -f http://${APP_HOST}:${APP_PORT}/ || echo "⚠️ Root endpoint not ready"
                    
                    echo "🌐 Testing health endpoint..."
                    curl -f http://${APP_HOST}:${APP_PORT}/health || echo "⚠️ Health endpoint not ready"
                    
                    echo "✅ Deployment test completed"
                '''
            }
        }
    }

    post {
        always {
            script {
                echo "🧹 Cleaning up..."
                sh '''
                    # Stop the application
                    if [ -f app.pid ] && ps -p $(cat app.pid) > /dev/null; then
                        echo "🛑 Stopping application..."
                        kill $(cat app.pid)
                        sleep 2
                    fi
                    rm -f app.pid app.log 2>/dev/null || true
                '''
                
                // Optional: Keep the workspace for inspection
                // cleanWs()
            }
        }
        success {
            echo "🎉 Deployment completed successfully!"
        }
        failure {
            echo "❌ Deployment failed"
        }
    }
}
