pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        APP_PORT = '8111'
        APP_HOST = '0.0.0.0'
        APP_ENTRY_POINT = 'main:app'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    echo "🐍 Setting up environment..."
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install fastapi uvicorn
                    
                    echo "🚀 Starting application..."
                    pkill -f "uvicorn main:app" || true
                    nohup python -m uvicorn ${APP_ENTRY_POINT} --host ${APP_HOST} --port ${APP_PORT} > app.log 2>&1 &
                    
                    sleep 5
                    echo "✅ DEPLOYMENT SUCCESSFUL!"
                    echo "🌐 OPEN YOUR BROWSER AND GO TO:"
                    echo "   http://143.1.1.128:8111/"
                    echo "   http://143.1.1.128:8111/docs"
                    echo "   http://143.1.1.128:8111/health"
                '''
            }
        }
    }
}
