pipeline {
    agent { label 'python_agent' }

    triggers {
        githubPush()
    }

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
    }

    environment {
        APP_NAME = 'python-expense-tracker'
        VENV_DIR = '.venv'
        PACKAGE_DIR = 'dist'
        DEPLOY_DIR = "${WORKSPACE}/deploy"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                sh '''
                    python3 --version

                    rm -rf "$VENV_DIR"
                    python3 -m venv "$VENV_DIR"

                    "$VENV_DIR/bin/python" -m pip install --upgrade pip
                    "$VENV_DIR/bin/python" -m pip install -r requirements.txt
                    "$VENV_DIR/bin/python" -m pip install .
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '''
                    "$VENV_DIR/bin/python" -m flake8 expense_tracker tests
                '''
            }
        }

        stage('Unit Test') {
            steps {
                sh '''
                    "$VENV_DIR/bin/python" -m pytest \
                        --junitxml=test-results.xml \
                        --cov=expense_tracker \
                        --cov-report=term-missing \
                        --cov-report=xml:coverage.xml
                '''
            }

            post {
                always {
                    junit(
                        testResults: 'test-results.xml',
                        allowEmptyResults: true
                    )
                }
            }
        }

        stage('SonarQube Static Code Analysis') {
            steps {
                script {
                    // Must match:
                    // Manage Jenkins → Tools → SonarQube Scanner
                    def scannerHome = tool 'SonarScanner'

                    // Must match:
                    // Manage Jenkins → System → SonarQube installations
                    withSonarQubeEnv('SonarQube') {
                        sh """
                            ${scannerHome}/bin/sonar-scanner
                        """
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 10, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Package') {
            steps {
                sh '''
                    rm -rf build dist *.egg-info

                    "$VENV_DIR/bin/python" setup.py \
                        sdist \
                        bdist_wheel

                    tar -czf "${APP_NAME}-${BUILD_NUMBER}.tar.gz" \
                        expense_tracker \
                        requirements.txt \
                        README.md
                '''
            }
        }

        stage('Archive Artifacts') {
            steps {
                archiveArtifacts(
                    artifacts: 'dist/*,*.tar.gz,coverage.xml,test-results.xml',
                    fingerprint: true
                )
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    mkdir -p "$DEPLOY_DIR"

                    cp "${APP_NAME}-${BUILD_NUMBER}.tar.gz" \
                       "$DEPLOY_DIR/"

                    "$VENV_DIR/bin/python" -m expense_tracker.app

                    echo "Deployment simulation completed."
                    echo "Artifact copied to: $DEPLOY_DIR"
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully.'
        }

        failure {
            echo 'Pipeline failed. Check the failed stage and console output.'
        }

        always {
            echo "Job name: ${JOB_NAME}"
            echo "Build number: ${BUILD_NUMBER}"
            echo "Build URL: ${BUILD_URL}"

            cleanWs(
                deleteDirs: true,
                patterns: [
                    [pattern: 'deploy/**', type: 'EXCLUDE']
                ]
            )
        }
    }
}