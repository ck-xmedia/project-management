pipeline {
    agent any
    
    environment {
        APP_PORT = '8080'  # Try different port
    }
    
    stages {
        stage('Deploy on 8080') {
            steps {
                sh '''
                    cd /var/jenkins_home/workspace/project-management
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install fastapi uvicorn
                    
                    pkill -f "uvicorn main:app" || true
                    nohup python -m uvicorn main:app --host 0.0.0.0 --port ${APP_PORT} > app.log 2>&1 &
                    
                    echo "✅ Try: http://143.1.1.128:${APP_PORT}/"
                '''
            }
        }
    }
}
