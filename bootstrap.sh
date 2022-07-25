#!/usr/bin/env bash
set -ev

# Upgrade the system.
apt-get update
apt-get upgrade -y

# Install Docker.
apt-get install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io
mkdir /etc/systemd/system/docker.service.d
{
    echo "[Service]"
    echo "ExecStart="
    echo "ExecStart=/usr/bin/dockerd"
} > /etc/systemd/system/docker.service.d/override.conf
echo "{\"hosts\": [\"unix:///var/run/docker.sock\", \"tcp://0.0.0.0:2375\"]}" > /etc/docker/daemon.json
systemctl daemon-reload
systemctl restart docker

# Allow vagrant user to use Docker CLI directly.
usermod -aG docker vagrant
