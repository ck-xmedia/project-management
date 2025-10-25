pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        APP_PORT = '8111'
        APP_HOST = '0.0.0.0'
        APP_ENTRY_POINT = 'main:app'
        JENKINS_IP = '143.1.1.128'  // Your Jenkins server IP
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Show Structure') {
            steps {
                sh '''
                    echo "📁 Project structure:"
                    ls -la
                    echo "📄 Python files:"
                    find . -name "*.py" -type f | grep -v venv
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    echo "🐍 Setting up environment..."
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt || pip install fastapi uvicorn
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    echo "🚀 Starting: ${APP_ENTRY_POINT}"
                    
                    # Stop any previous instance
                    if [ -f "app.pid" ]; then
                        echo "🛑 Stopping previous instance..."
                        kill $(cat app.pid) 2>/dev/null || true
                        rm -f app.pid
                    fi
                    
                    # Start the application
                    nohup python -m uvicorn ${APP_ENTRY_POINT} --host ${APP_HOST} --port ${APP_PORT} > app.log 2>&1 &
                    echo $! > app.pid
                    sleep 5
                    echo "📝 Logs:"
                    tail -n 20 app.log
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    echo "🔍 Verifying deployment..."
                    
                    # Check if process is running
                    if ps -p $(cat app.pid) > /dev/null; then
                        echo "✅ Application is running with PID: $(cat app.pid)"
                        
                        # Test local access
                        echo "🌐 Testing local access..."
                        curl -f http://localhost:${APP_PORT}/ && echo "✅ Local access works" || echo "⚠️ Local access failed"
                        
                        # Display access information
                        echo ""
                        echo "🎉 DEPLOYMENT SUCCESSFUL!"
                        echo "🌐 Your application is accessible at:"
                        echo "   http://${JENKINS_IP}:${APP_PORT}"
                        echo "   http://${JENKINS_IP}:${APP_PORT}/docs"
                        echo ""
                        echo "📊 Process Info:"
                        ps -p $(cat app.pid) -o pid,cmd
                    else
                        echo "❌ Application failed to start"
                        cat app.log
                        exit 1
                    fi
                '''
            }
        }
    }

    post {
        always {
            script {
                echo "🏁 Pipeline completed"
                echo "📝 Application is kept running"
                echo "💡 To stop manually: kill \$(cat app.pid)"
                
                // Only clean cache files, NOT the entire workspace
                sh '''
                    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
                    find . -name "*.pyc" -delete 2>/dev/null || true
                '''
            }
        }
        success {
            emailext(
                subject: "✅ SUCCESS: FastAPI App Deployed - ${currentBuild.fullDisplayName}",
                body: """
                🎉 FastAPI Application Successfully Deployed!

                📋 Build Details:
                • Project: ${env.JOB_NAME}
                • Build: ${currentBuild.displayName}

                🌐 Access Your Application:
                • URL: http://${JENKINS_IP}:${APP_PORT}
                • API Docs: http://${JENKINS_IP}:${APP_PORT}/docs

                🔧 Process ID: $(readFile('app.pid').trim())
                """,
                to: 'developerxmedia052@gmail.com'
            )
        }
    }
}
