pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        APP_PORT = '8111'
        APP_HOST = '0.0.0.0'
        APP_ENTRY_POINT = 'main:app'  // change if path differs
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
                    find . -name "*.py" -type f
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
                    nohup python -m uvicorn ${APP_ENTRY_POINT} --host ${APP_HOST} --port ${APP_PORT} > app.log 2>&1 &
                    echo $! > app.pid
                    sleep 5
                    echo "📝 Logs:"
                    tail -n 20 app.log
                '''
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning workspace..."
            cleanWs()
        }
    }
}
