pipeline {
    agent any

    environment {
        APP_PORT = '8111'
    }

    stages {
        stage('Deploy Simple') {
            steps {
                sh '''
                    echo "🚀 Simple deployment on host server..."
                    
                    # Just start the app directly on host
                    cd /var/jenkins_home/workspace/project-management
                    python3 -m venv host_venv
                    . host_venv/bin/activate
                    pip install fastapi uvicorn
                    
                    # Stop any running instance
                    pkill -f "uvicorn main:app" || true
                    
                    # Start app
                    nohup python -m uvicorn main:app --host 0.0.0.0 --port ${APP_PORT} > host_app.log 2>&1 &
                    
                    echo "✅ App should be running"
                    echo "🌐 Try: http://143.1.1.128:8111/"
                '''
            }
        }
    }
}
