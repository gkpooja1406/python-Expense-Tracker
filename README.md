# Python Expense Tracker — Jenkins, GitHub Webhook and SonarQube Activity

## Project idea

This is a tiny real-world command-line Expense Tracker. It validates expenses,
calculates the total expense, and calculates category-wise totals.

## Pipeline workflow

Developer Push  
↓  
GitHub Webhook  
↓  
Checkout  
↓  
Build  
↓  
Lint  
↓  
Unit Test  
↓  
SonarQube Static Code Analysis  
↓  
Quality Gate  
↓  
Package  
↓  
Archive Artifacts  
↓  
Deploy Simulation  
↓  
Post Actions

## 1. Test locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install .
flake8 expense_tracker tests
pytest --cov=expense_tracker --cov-report=xml:coverage.xml
python -m expense_tracker.app
```

## 2. Push the project to GitHub

Create an empty GitHub repository, then run:

```bash
git init
git add .
git commit -m "Add Jenkins SonarQube webhook activity"
git branch -M main
git remote add origin git@github.com:YOUR_USERNAME/python-expense-tracker.git
git push -u origin main
```

## 3. Jenkins plugins

Open **Manage Jenkins → Plugins → Available plugins**, then install:

- Pipeline
- Git
- GitHub
- GitHub Branch Source
- SonarQube Scanner
- JUnit
- Workspace Cleanup

Restart Jenkins if requested.

## 4. Start SonarQube using Docker Compose

On a machine with enough memory and Docker:

```bash
docker compose -f docker-compose-sonarqube.yml up -d
docker compose -f docker-compose-sonarqube.yml ps
```

Open:

```text
http://SONARQUBE_SERVER_IP:9000
```

Initial login is normally `admin` / `admin`; SonarQube will ask you to change it.

For AWS EC2, allow TCP port 9000 in the security group only from your IP or
from the Jenkins server as appropriate. Do not expose it openly for production.

## 5. Create a SonarQube token

1. Log in to SonarQube.
2. Click the user icon.
3. Open **My Account → Security**.
4. Enter a token name such as `jenkins-token`.
5. Generate the token.
6. Copy it immediately.

## 6. Save the token in Jenkins

1. Open **Manage Jenkins → Credentials**.
2. Select **System → Global credentials**.
3. Click **Add Credentials**.
4. Kind: **Secret text**.
5. Secret: paste the SonarQube token.
6. ID: `sonarqube-token`.
7. Description: `SonarQube token for Jenkins`.
8. Save.

## 7. Configure SonarQube server in Jenkins

1. Open **Manage Jenkins → System**.
2. Find **SonarQube installations**.
3. Click **Add SonarQube**.
4. Name: `SonarQube`.
5. Server URL: `http://SONARQUBE_SERVER_IP:9000`.
6. Server authentication token: select `sonarqube-token`.
7. Save.

The name must exactly match `withSonarQubeEnv('SonarQube')` in the Jenkinsfile.

## 8. Configure SonarScanner in Jenkins

1. Open **Manage Jenkins → Tools**.
2. Find **SonarQube Scanner installations**.
3. Click **Add SonarQube Scanner**.
4. Name: `SonarScanner`.
5. Select **Install automatically**.
6. Save.

The name must exactly match `sonarQube 'SonarScanner'` in the Jenkinsfile.

## 9. Configure SonarQube webhook for the Quality Gate

This webhook is from **SonarQube to Jenkins**, not GitHub to Jenkins.

1. In SonarQube, open **Administration → Configuration → Webhooks**.
2. Click **Create**.
3. Name: `Jenkins Quality Gate`.
4. URL:

```text
http://JENKINS_PUBLIC_IP:8080/sonarqube-webhook/
```

5. Save.

The trailing `/` is important. This webhook sends the completed analysis result
to Jenkins so `waitForQualityGate` can continue.

## 10. Create the Jenkins Pipeline job

1. Jenkins dashboard → **New Item**.
2. Enter `python-expense-tracker`.
3. Select **Pipeline**, then click **OK**.
4. Under **General**, enter the GitHub repository URL in **GitHub project**.
5. Under **Build Triggers**, select:
   **GitHub hook trigger for GITScm polling**.
6. Under **Pipeline**:
   - Definition: **Pipeline script from SCM**
   - SCM: **Git**
   - Repository URL: your GitHub repository
   - Credentials: select credentials only for a private repository
   - Branch Specifier: `*/main`
   - Script Path: `Jenkinsfile`
7. Save.
8. Click **Build Now** once to verify the initial setup.

The Jenkinsfile also contains `triggers { githubPush() }`.

## 11. Configure the GitHub webhook

This webhook is from **GitHub to Jenkins** and triggers a build after a push.

1. Open the GitHub repository.
2. Go to **Settings → Webhooks → Add webhook**.
3. Payload URL:

```text
http://JENKINS_PUBLIC_IP:8080/github-webhook/
```

4. Content type: `application/json`.
5. Secret: optional for this basic activity.
6. Select **Just the push event**.
7. Keep **Active** selected.
8. Click **Add webhook**.

GitHub must be able to reach Jenkins. On AWS, allow TCP port 8080 from the
required source. For practice, confirm connectivity carefully; for production,
use HTTPS, a reverse proxy, authentication, and restricted network access.

## 12. Run the webhook activity

Webhook Test

Change a line in `expense_tracker/app.py`, then run:

```bash
git add .
git commit -m "Test GitHub webhook"
git push origin main
```

Expected behavior:

1. GitHub sends an HTTP POST request to `/github-webhook/`.
2. Jenkins receives the push event.
3. Jenkins automatically starts the Pipeline.
4. Jenkins checks out the latest commit.
5. Flake8 performs lint/static style checks.
6. Pytest runs unit tests and generates JUnit and coverage reports.
7. SonarScanner sends source and coverage information to SonarQube.
8. SonarQube evaluates the Quality Gate.
9. SonarQube calls `/sonarqube-webhook/` in Jenkins.
10. Jenkins continues only when the Quality Gate passes.
11. Jenkins packages and archives the application.
12. Jenkins runs the deployment simulation.
13. Post actions report the final status and clean the workspace.

## 13. How to verify the GitHub webhook

In GitHub:

1. Repository **Settings → Webhooks**.
2. Click the Jenkins webhook.
3. Open **Recent Deliveries**.
4. A successful delivery displays a green check.
5. Open a delivery to inspect request headers, payload and Jenkins response.

In Jenkins:

1. Open the job.
2. Confirm a new build starts immediately after the push.
3. Open **Console Output**.
4. Verify every stage.
5. Open **Build Artifacts** to download the package, coverage XML and test XML.

## 14. Expected screenshots for an assignment

1. GitHub repository showing project files and `Jenkinsfile`.
2. Jenkins installed plugins showing GitHub and SonarQube Scanner.
3. Jenkins SonarQube server configuration.
4. Jenkins SonarScanner tool configuration.
5. SonarQube token credential in Jenkins, hiding the token value.
6. SonarQube webhook pointing to `/sonarqube-webhook/`.
7. GitHub webhook pointing to `/github-webhook/`.
8. GitHub Recent Deliveries showing a green successful delivery.
9. Jenkins Stage View showing every stage in green.
10. Unit Test result in Jenkins.
11. SonarQube project dashboard.
12. SonarQube Quality Gate showing Passed.
13. Jenkins archived artifacts.
14. Jenkins console output showing automatic trigger and deployment simulation.

## Important distinction

- **GitHub webhook → Jenkins**: starts the build after a push.
- **SonarQube webhook → Jenkins**: sends the Quality Gate result back to the
  waiting Pipeline.
- A webhook is configured in the application UI. The Jenkinsfile declares that
  the Pipeline accepts GitHub push triggers, but it cannot by itself create the
  GitHub repository webhook.
