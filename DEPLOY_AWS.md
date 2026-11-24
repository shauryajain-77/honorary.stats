# Cloud Deployment Guide: Hackathon Prototype

Step-by-step terminal commands to deploy and host the merged prototype on AWS for a live public HTTPS URL, plus a 5-minute emergency backup on Render/Railway.

---

## Prerequisites
- Docker installed locally (`docker --version`).
- AWS CLI configured with credentials:
  ```bash
  aws configure
  # Enter AWS Access Key, Secret Key, and Region (e.g. ap-south-1)
  ```

---

## Option 1: AWS App Runner (Recommended - Instant Public HTTPS)

AWS App Runner provides an automatic public HTTPS link (`https://xxxx.awsapprunner.com`), zero server management, and automatic SSL.

### Step 1: Set AWS Variables
```bash
# In Bash / macOS / Linux:
export AWS_REGION="ap-south-1"
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export ECR_REPO="voice-skill-prototype"
export ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}"

# In Windows PowerShell:
$AWS_REGION = "ap-south-1"
$AWS_ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
$ECR_REPO = "voice-skill-prototype"
$ECR_URI = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}"
```

### Step 2: Create ECR Repository & Authenticate
```bash
# 1. Create ECR repo
aws ecr create-repository --repository-name $ECR_REPO --region $AWS_REGION

# 2. Login Docker to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URI
```

### Step 3: Build, Tag & Push Container
```bash
# 1. Build image
docker build -t $ECR_REPO .

# 2. Tag image for ECR
docker tag ${ECR_REPO}:latest ${ECR_URI}:latest

# 3. Push to ECR
docker push ${ECR_URI}:latest
```

### Step 4: Deploy to AWS App Runner
```bash
aws apprunner create-service \
  --service-name voice-skill-service \
  --source-configuration ImageRepository='{ImageIdentifier="'${ECR_URI}':latest",ImageRepositoryType="ECR",ImageConfiguration={Port="8000"}}' \
  --region $AWS_REGION
```

*Retrieve your live public HTTPS URL:*
```bash
aws apprunner list-services --query "ServiceSummaryList[?ServiceName=='voice-skill-service'].ServiceUrl" --output text
# Outputs: https://xxxxxxxxxx.ap-south-1.awsapprunner.com
```

---

## Option 2: AWS EC2 (Single VM Hosting)

If your team prefers a standard Ubuntu virtual machine:

### Step 1: Launch EC2 Instance
- **OS**: Ubuntu 22.04 or 24.04 LTS
- **Instance Type**: `t3.small` or `t2.micro`
- **Region**: `ap-south-1` (Mumbai)
- **Security Group Inbound Rules**:
  - HTTP (Port 80) -> `0.0.0.0/0`
  - HTTPS (Port 443) -> `0.0.0.0/0`
  - SSH (Port 22) -> `My IP`

### Step 2: SSH into Instance
```bash
ssh -i your-key.pem ubuntu@<YOUR_EC2_PUBLIC_IP>
```

### Step 3: Setup & Run Docker
```bash
# 1. Update and install Docker & Git
sudo apt-get update && sudo apt-get install -y docker.io git

# 2. Clone repository & enter directory
git clone <YOUR_GIT_REPO_URL> app
cd app

# 3. Create .env from example
cp .env.example .env
nano .env # Paste your real ELEVENLABS_API_KEY and other keys

# 4. Build and run container on Port 80
sudo docker build -t prototype .
sudo docker run -d --restart always -p 80:8000 --env-file .env --name voice_card_app prototype
```

Your service is immediately accessible at:
```
http://<YOUR_EC2_PUBLIC_IP>
```

---

## Option 3: 5-Minute Emergency Backup (Render / Railway)

If AWS account setup, permissions, or billing approval cause delays during the hackathon, use one of these instant 1-command alternatives:

### Backup A: Railway (Fastest CLI Deployment - ~3 mins)

```bash
# 1. Install Railway CLI
npm install -g @railway/cli
# Or on macOS/Linux: curl -fsSL https://railway.com/install.sh | sh

# 2. Login & deploy
railway login
railway init
railway up

# 3. Set environment variable & generate public HTTPS URL
railway variables set ELEVENLABS_API_KEY="your_actual_key"
railway domain
```
*Outputs an active public URL: `https://xxxx.up.railway.app`*

---

### Backup B: Render (Web UI / 1-Click Git Connect)

1. Push your code to GitHub.
2. Go to [dashboard.render.com](https://dashboard.render.com/) -> Click **New +** -> **Web Service**.
3. Select your repository.
4. Set:
   - **Environment**: `Docker`
   - **Region**: `Singapore` or `Frankfurt`
   - **Plan**: `Free`
5. In **Environment Variables**, add:
   - `ELEVENLABS_API_KEY` = `your_key`
   - `PUBLIC_BASE_URL` = `https://<your-service-name>.onrender.com`
6. Click **Create Web Service**. Your app is live with a free, valid SSL certificate in under 4 minutes.
