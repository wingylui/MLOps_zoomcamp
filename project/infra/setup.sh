#!/bin/bash
set -e

echo "🛠️  Starting EC2 setup for House Price Prediction..."

# Update & install Docker and Docker Compose
if ! command -v docker &> /dev/null; then
  echo "Installing Docker..."
  sudo apt-get update
  sudo apt-get install -y docker.io
  sudo systemctl enable docker
  sudo systemctl start docker
  sudo usermod -aG docker $USER
fi

if ! command -v docker-compose &> /dev/null; then
  echo "Installing Docker Compose..."
  sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
fi

# Ensure ownership of project folder
sudo chown -R $USER:$USER .

# Login session refresh (just in case usermod requires relogin)
newgrp docker <<EONG
  echo "Building and launching Docker containers..."
  docker compose down || true
  docker compose build
  docker compose up -d
EONG

echo "✅ House Price Prediction app is deployed and running."

echo "🔎 Services Running:"
echo "- Flask API: http://<EC2-IP>:9696"
echo "- Adminer:   http://<EC2-IP>:8050"
echo "- Grafana:   http://<EC2-IP>:3000 (default login: admin / admin)"
