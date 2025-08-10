// Jenkins Pipeline for GopiAI Testing
// This file should be used as a Jenkinsfile in your repository

pipeline {
    agent any
    
    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['development', 'staging', 'production'],
            description: 'Target environment for testing'
        )
        string(
            name: 'TEST_TYPES',
            defaultValue: 'unit integration',
            description: 'Space-separated list of test types to run'
        )
        booleanParam(
            name: 'SKIP_SLOW_TESTS',
            defaultValue: true,
            description: 'Skip slow-running tests'
        )
        booleanParam(
            name: 'GENERATE_REPORTS',
            defaultValue: true,
            description: 'Generate detailed test reports'
        )
    }
    
    environment {
        PYTHON_VERSION = '3.9'
        VIRTUAL_ENV = 'venv'
        LOG_LEVEL = 'INFO'
        PYTEST_ARGS = '--tb=short --strict-markers'
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 60, unit: 'MINUTES')
        timestamps()
        ansiColor('xterm')
    }
    
    triggers {
        // Run tests daily at 2 AM
        cron('0 2 * * *')
        // Trigger on SCM changes
        pollSCM('H/5 * * * *')
    }
    
    stages {
        stage('Checkout') {
            steps {
                script {
                    echo "🔄 Checking out code..."
                    checkout scm
                    
                    // Set build description
                    currentBuild.description = "Environment: ${params.ENVIRONMENT}, Tests: ${params.TEST_TYPES}"
                }
            }
        }
        
        stage('Setup Environment') {
            steps {
                script {
                    echo "🐍 Setting up Python environment..."
                    
                    // Create virtual environment
                    sh """
                        python${PYTHON_VERSION} -m venv ${VIRTUAL_ENV}
                        source ${VIRTUAL_ENV}/bin/activate
                        pip install --upgrade pip setuptools wheel
                    """
                    
                    // Install dependencies
                    sh """
                        source ${VIRTUAL_ENV}/bin/activate
                        pip install -r requirements.txt
                        pip install -e ./GopiAI-Core
                        pip install -e ./GopiAI-UI
                        pip install -e ./GopiAI-CrewAI
                    """
                }
            }
        }
        
        stage('Code Quality Checks') {
            parallel {
                stage('Linting') {
                    steps {
                        script {
                            echo "🔍 Running code linting..."
                            sh """
                                source ${VIRTUAL_ENV}/bin/activate
                                flake8 . --format=junit-xml --output-file=flake8-report.xml || true
                            """
                        }
                    }
                    post {
                        always {
                            publishTestResults testResultsPattern: 'flake8-report.xml'
                        }
                    }
                }
                
                stage('Security Scan') {
                    steps {
                        script {
                            echo "🔒 Running security scan..."
                            sh """
                                source ${VIRTUAL_ENV}/bin/activate
                                bandit -r . -f json -o bandit-report.json || true
                                safety check --json --output safety-report.json || true
                            """
                        }
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: '*-report.json', allowEmptyArchive: true
                        }
                    }
                }
                
                stage('Type Checking') {
                    steps {
                        script {
                            echo "📝 Running type checking..."
                            sh """
                                source ${VIRTUAL_ENV}/bin/activate
                                mypy GopiAI-Core/gopiai/ --ignore-missing-imports --junit-xml mypy-report.xml || true
                            """
                        }
                    }
                    post {
                        always {
                            publishTestResults testResultsPattern: 'mypy-report.xml'
                        }
                    }
                }
            }
        }
        
        stage('Unit Tests') {
            steps {
                script {
                    echo "🧪 Running unit tests..."
                    sh """
                        source ${VIRTUAL_ENV}/bin/activate
                        python ci_cd/automated_test_runner.py \\
                            --environment ${params.ENVIRONMENT} \\
                            --test-types unit \\
                            --config ci_cd/config/jenkins.json
                    """
                }
            }
            post {
                always {
                    publishTestResults testResultsPattern: 'ci_cd/reports/*/junit_results.xml'
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'ci_cd/reports',
                        reportFiles: '*/test_report.html',
                        reportName: 'Unit Test Report'
                    ])
                }
            }
        }
        
        stage('Integration Tests') {
            when {
                anyOf {
                    expression { params.TEST_TYPES.contains('integration') }
                    expression { params.ENVIRONMENT != 'development' }
                }
            }
            steps {
                script {
                    echo "🔗 Running integration tests..."
                    
                    // Start required services
                    sh """
                        source ${VIRTUAL_ENV}/bin/activate
                        python test_infrastructure/service_manager.py --start-all
                    """
                    
                    // Run integration tests
                    sh """
                        source ${VIRTUAL_ENV}/bin/activate
                        python ci_cd/automated_test_runner.py \\
                            --environment ${params.ENVIRONMENT} \\
                            --test-types integration \\
                            --config ci_cd/config/jenkins.json
                    """
                }
            }
            post {
                always {
                    // Stop services
                    sh """
                        source ${VIRTUAL_ENV}/bin/activate
                        python test_infrastructure/service_manager.py --stop-all || true
                    """
                    
                    publishTestResults testResultsPattern: 'ci_cd/reports/*/junit_results.xml'
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'ci_cd/reports',
                        reportFiles: '*/test_report.html',
                        reportName: 'Integration Test Report'
                    ])
                }
            }
        }
        
        stage('UI Tests') {
            when {
                expression { params.TEST_TYPES.contains('ui') }
            }
            steps {
                script {
                    echo "🖥️ Running UI tests..."
                    sh """
                        source ${VIRTUAL_ENV}/bin/activate
                        xvfb-run -a python ci_cd/automated_test_runner.py \\
                            --environment ${params.ENVIRONMENT} \\
                            --test-types ui \\
                            --config ci_cd/config/jenkins.json
                    """
                }
            }
            post {
                always {
                    publishTestResults testResultsPattern: 'ci_cd/reports/*/junit_results.xml'
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'ci_cd/reports',
                        reportFiles: '*/test_report.html',
                        reportName: 'UI Test Report'
                    ])
                }
            }
        }
        
        stage('E2E Tests') {
            when {
                anyOf {
                    expression { params.TEST_TYPES.contains('e2e') }
                    expression { params.ENVIRONMENT == 'staging' }
                }
            }
            steps {
                script {
                    echo "🎯 Running E2E tests..."
                    sh """
                        source ${VIRTUAL_ENV}/bin/activate
                        xvfb-run -a python ci_cd/automated_test_runner.py \\
                            --environment ${params.ENVIRONMENT} \\
                            --test-types e2e \\
                            --config ci_cd/config/jenkins.json
                    """
                }
            }
            post {
                always {
                    publishTestResults testResultsPattern: 'ci_cd/reports/*/junit_results.xml'
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'ci_cd/reports',
                        reportFiles: '*/test_report.html',
                        reportName: 'E2E Test Report'
                    ])
                }
            }
        }
        
        stage('Performance Tests') {
            when {
                anyOf {
                    expression { params.TEST_TYPES.contains('performance') }
                    triggeredBy 'TimerTrigger'
                }
            }
            steps {
                script {
                    echo "⚡ Running performance tests..."
                    sh """
                        source ${VIRTUAL_ENV}/bin/activate
                        python ci_cd/automated_test_runner.py \\
                            --environment ${params.ENVIRONMENT} \\
                            --test-types performance \\
                            --config ci_cd/config/jenkins.json
                    """
                }
            }
            post {
                always {
                    publishTestResults testResultsPattern: 'ci_cd/reports/*/junit_results.xml'
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'ci_cd/reports',
                        reportFiles: '*/test_report.html',
                        reportName: 'Performance Test Report'
                    ])
                }
            }
        }
        
        stage('Security Tests') {
            when {
                expression { params.TEST_TYPES.contains('security') }
            }
            steps {
                script {
                    echo "🛡️ Running security tests..."
                    sh """
                        source ${VIRTUAL_ENV}/bin/activate
                        python ci_cd/automated_test_runner.py \\
                            --environment ${params.ENVIRONMENT} \\
                            --test-types security \\
                            --config ci_cd/config/jenkins.json
                    """
                }
            }
            post {
                always {
                    publishTestResults testResultsPattern: 'ci_cd/reports/*/junit_results.xml'
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'ci_cd/reports',
                        reportFiles: '*/test_report.html',
                        reportName: 'Security Test Report'
                    ])
                }
            }
        }
        
        stage('Generate Reports') {
            when {
                expression { params.GENERATE_REPORTS }
            }
            steps {
                script {
                    echo "📊 Generating comprehensive reports..."
                    sh """
                        source ${VIRTUAL_ENV}/bin/activate
                        python ci_cd/generate_ci_report.py \\
                            --artifacts-dir ci_cd/reports \\
                            --output-dir final-report \\
                            --format html json
                    """
                }
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'final-report',
                        reportFiles: 'index.html',
                        reportName: 'Comprehensive Test Report'
                    ])
                    
                    archiveArtifacts artifacts: 'final-report/**/*', allowEmptyArchive: true
                }
            }
        }
        
        stage('Deploy') {
            when {
                allOf {
                    branch 'main'
                    expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
                    expression { params.ENVIRONMENT == 'production' }
                }
            }
            steps {
                script {
                    echo "🚀 Deploying to production..."
                    
                    // Add deployment logic here
                    sh """
                        source ${VIRTUAL_ENV}/bin/activate
                        python ci_cd/deploy.py \\
                            --environment production \\
                            --version ${BUILD_NUMBER}
                    """
                }
            }
        }
    }
    
    post {
        always {
            script {
                echo "🧹 Cleaning up..."
                
                // Archive logs and artifacts
                archiveArtifacts artifacts: 'ci_cd/logs/**/*', allowEmptyArchive: true
                archiveArtifacts artifacts: 'ci_cd/reports/**/*', allowEmptyArchive: true
                archiveArtifacts artifacts: '.coverage*', allowEmptyArchive: true
                
                // Clean up virtual environment
                sh "rm -rf ${VIRTUAL_ENV} || true"
            }
        }
        
        success {
            script {
                echo "✅ Pipeline completed successfully!"
                
                // Send success notification
                sh """
                    python ci_cd/send_notification.py \\
                        --type pipeline \\
                        --status success \\
                        --environment ${params.ENVIRONMENT} \\
                        --build-number ${BUILD_NUMBER}
                """
            }
        }
        
        failure {
            script {
                echo "❌ Pipeline failed!"
                
                // Send failure notification
                sh """
                    python ci_cd/send_notification.py \\
                        --type pipeline \\
                        --status failure \\
                        --environment ${params.ENVIRONMENT} \\
                        --build-number ${BUILD_NUMBER}
                """
            }
        }
        
        unstable {
            script {
                echo "⚠️ Pipeline completed with warnings!"
                
                // Send warning notification
                sh """
                    python ci_cd/send_notification.py \\
                        --type pipeline \\
                        --status unstable \\
                        --environment ${params.ENVIRONMENT} \\
                        --build-number ${BUILD_NUMBER}
                """
            }
        }
    }
}