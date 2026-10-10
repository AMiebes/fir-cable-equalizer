pipeline {
    agent any 

    options {
        // bricht die Pipeline ab, falls Docker Build/Tests länger als 30 Min dauern
        timeout(time: 30, unit: 'MINUTES')
        // behält nur die letzten 10 Runs auf dem Jenkins-Server
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    triggers {
        // Prüft alle 5 Minuten (mit Zufalls-Hash 'H' zur Lastverteilung) auf neue Git Commits
        pollSCM('H/5 * * * *')
    }

    environment {
        DOCKER_IMAGE = "cocotb-jenkins-env"
        PORTFOLIO_URL = "https://github.com/AMiebes/fir-cable-equalizer.git"
    }

    stages {
        stage('Cleanup Workspace') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'rm -rf tb/sim_build tb/__pycache__ tb/results.xml tb/*.vcd'
                    } else {
                        bat 'if exist tb\\sim_build rd /s /q tb\\sim_build'
                        bat 'if exist tb\\__pycache__ rd /s /q tb\\__pycache__'
                        bat 'if exist tb\\results.xml del /f /q tb\\results.xml'
                        bat 'if exist tb\\*.vcd del /f /q tb\\*.vcd'
                    }
                }
            }
        }

        stage('Build Environment') {
            steps {
                echo "Baue Docker-Umgebung..."
                script {
                    def buildCmd = "docker build -t ${DOCKER_IMAGE} ."
                    isUnix() ? sh(buildCmd) : bat(buildCmd)
                }
            }
        }

        stage('Run Cocotb Tests') {
            steps {
                echo "Starte Simulation im Container (DooD)..."
                script {
                    def hostWorkspace = env.HOST_JENKINS_HOME ? WORKSPACE.replace('/var/jenkins_home', env.HOST_JENKINS_HOME) : WORKSPACE
                    def runCmd = "docker run --rm -e COCOTB_WAVES=1 -v \"${hostWorkspace}\":/work -w /work ${DOCKER_IMAGE} make test"
        
                    if (isUnix()) {
                        sh runCmd
                    } else {
                        bat runCmd
                    }
                }
            }
        }
    }

    post {
        always {
            echo "--------------------------------------------------"
            echo "🔗 Project Repo & Portfolio: ${PORTFOLIO_URL}"
            echo "--------------------------------------------------"
            
            // JUnit-Auswertung aus tb/results.xml
            junit allowEmptyResults: true, testResults: 'tb/results.xml'
            
            // Artifact-Archivierung für VCD und XML
            archiveArtifacts artifacts: 'tb/results.xml, tb/**/*.vcd', allowEmptyArchive: true
        }
        success {
            echo "Tests erfolgreich bestanden! ✅"
        }
        failure {
            echo "Tests oder Build fehlgeschlagen. ❌"
        }
    }
}