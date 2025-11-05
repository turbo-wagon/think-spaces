# 🚀 Think Spaces Deployment Guide

This guide covers deploying Think Spaces using Docker on various environments, with a focus on Proxmox self-hosting.

---

## 📦 Quick Start (Docker Compose)

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- Git

### Deploy in 3 Commands
```bash
# Clone the repository
git clone https://github.com/yourusername/think-spaces.git
cd think-spaces

# (Optional) Set API keys
export OPENAI_API_KEY="sk-..."

# Start the application
docker-compose up -d
```

Access at: **http://localhost:8000/ui/spaces**

---

## 🖥️ Proxmox Deployment

### Option A: Docker in LXC Container (Recommended)

**Advantages:**
- Lower resource usage than VM
- Fast startup
- Easy backups via Proxmox
- Near-native performance

#### 1. Create LXC Container in Proxmox

```bash
# In Proxmox web UI:
# Create CT → Ubuntu 22.04 → 2GB RAM, 10GB disk
# Important: Check "Unprivileged container" = NO (required for Docker)
```

**Settings:**
- **Hostname:** thinkspaces
- **CPU:** 2 cores
- **RAM:** 2048 MB
- **Disk:** 10 GB
- **Network:** Bridge, DHCP or static IP
- **Features:** Enable "Nesting" and "keyctl"

#### 2. Install Docker in LXC

SSH into the container:
```bash
# From Proxmox host
pct enter <CTID>

# Or via SSH
ssh root@<container-ip>
```

Install Docker:
```bash
# Update packages
apt-get update && apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt-get install -y docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

#### 3. Deploy Think Spaces

```bash
# Install git
apt-get install -y git

# Clone repository
cd /opt
git clone https://github.com/yourusername/think-spaces.git
cd think-spaces

# (Optional) Set environment variables
cat > .env <<EOF
OPENAI_API_KEY=sk-your-key-here
OLLAMA_BASE_URL=http://your-proxmox-host:11434
EOF

# Start the application
docker compose up -d

# Check logs
docker compose logs -f
```

#### 4. Access the Application

From your network:
- **UI:** http://<container-ip>:8000/ui/spaces
- **API Docs:** http://<container-ip>:8000/docs

---

### Option B: Docker in Proxmox VM

If you prefer a full VM:

#### 1. Create VM in Proxmox

- **OS:** Ubuntu 22.04 Server
- **CPU:** 2 cores
- **RAM:** 4096 MB
- **Disk:** 20 GB
- **Network:** Bridge to your LAN

#### 2. Install Docker

SSH into VM and follow standard Docker installation:
```bash
# Update packages
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose plugin
sudo apt-get install -y docker-compose-plugin
```

#### 3. Deploy Think Spaces

Follow same steps as Option A, step 3.

---

## 🔧 Configuration

### Environment Variables

The application automatically loads environment variables from a `.env` file in the project root.

**Setup:**
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your values
nano .env  # or vim, emacs, etc.
```

**Example `.env` file:**
```bash
# OpenAI API Key (optional, for GPT models)
OPENAI_API_KEY=sk-your-key-here

# Groq API Key (optional, FREE fast inference)
# Get your key at https://console.groq.com
GROQ_API_KEY=gsk_your-key-here

# Ollama Base URL (optional, for local models)
# If Ollama is on Proxmox host, use host IP
OLLAMA_BASE_URL=http://192.168.1.100:11434

# Custom port (optional, default: 8000)
PORT=8000
```

**Security Note:** The `.env` file is automatically excluded from Git (via `.gitignore`). Never commit API keys to version control.

### Recommended: Use Groq for Free, Fast Inference

Groq provides **free API access** to powerful open-source models with **extremely fast inference** (150+ tokens/sec):

1. **Get your free API key:** https://console.groq.com
2. **Add to `.env`:**
   ```bash
   GROQ_API_KEY=gsk_your-key-here
   ```
3. **In the UI, create an agent with:**
   - Provider: `groq`
   - Model: `llama-3.1-70b-versatile` (recommended) or `llama-3.1-8b-instant` (faster)

**Available Groq Models:**
- `llama-3.1-70b-versatile` - Most capable, great reasoning
- `llama-3.1-8b-instant` - Fastest, good for simple tasks
- `mixtral-8x7b-32768` - Large context window
- `gemma2-9b-it` - Google's Gemma 2

### Using Ollama on Proxmox Host

If Ollama is running on your Proxmox host and you want the container to access it:

1. **From LXC container:**
   ```bash
   # Find your Proxmox host's IP on the bridge network
   ip route | grep default
   # Usually something like 192.168.1.1 or 10.0.0.1
   ```

2. **Set in .env:**
   ```bash
   OLLAMA_BASE_URL=http://192.168.1.1:11434
   ```

3. **Ensure Ollama is listening on all interfaces:**
   ```bash
   # On Proxmox host
   OLLAMA_HOST=0.0.0.0:11434 ollama serve
   ```

---

## 🔄 Updates & Maintenance

### Update Application

```bash
cd /opt/think-spaces

# Pull latest code
git pull

# Rebuild and restart
docker compose down
docker compose up -d --build

# View logs
docker compose logs -f
```

### Backup Data

Think Spaces stores data in two locations:

```bash
# Backup database
cp thinkspaces.db thinkspaces.db.backup

# Backup uploads
tar -czf uploads-backup.tar.gz uploads/

# Or use Proxmox LXC snapshots
# From Proxmox host:
pct snapshot <CTID> backup-$(date +%Y%m%d)
```

### Restore Data

```bash
# Stop application
docker compose down

# Restore database
cp thinkspaces.db.backup thinkspaces.db

# Restore uploads
tar -xzf uploads-backup.tar.gz

# Start application
docker compose up -d
```

---

## 🌐 Reverse Proxy (Optional)

### Nginx Reverse Proxy

To access via domain name (e.g., `thinkspaces.yourdomain.com`):

#### 1. Install Nginx on Proxmox host or separate container

```bash
apt-get install -y nginx certbot python3-certbot-nginx
```

#### 2. Configure Nginx

```bash
# Create config
cat > /etc/nginx/sites-available/thinkspaces <<EOF
server {
    listen 80;
    server_name thinkspaces.yourdomain.com;

    location / {
        proxy_pass http://<container-ip>:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/thinkspaces /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

#### 3. Add SSL (Optional)

```bash
certbot --nginx -d thinkspaces.yourdomain.com
```

---

## 🐛 Troubleshooting

### Container won't start

Check logs:
```bash
docker compose logs
```

Common issues:
- **Port 8000 in use:** Change port in docker-compose.yml
- **Permission denied:** Ensure LXC has "Nesting" enabled
- **Database locked:** Stop any local instances running on host

### Can't access from network

1. Check container is running:
   ```bash
   docker compose ps
   ```

2. Check firewall:
   ```bash
   # On container/VM
   ufw status
   ufw allow 8000/tcp
   ```

3. Test from container:
   ```bash
   curl http://localhost:8000/health
   ```

### Ollama not connecting

1. Verify Ollama is accessible:
   ```bash
   curl http://<ollama-host>:11434/api/version
   ```

2. Check OLLAMA_BASE_URL in docker-compose.yml

3. Ensure Ollama host firewall allows port 11434

---

## 📊 Resource Requirements

### Minimum
- **CPU:** 1 core
- **RAM:** 1 GB
- **Disk:** 5 GB

### Recommended
- **CPU:** 2 cores
- **RAM:** 2 GB
- **Disk:** 10 GB

### With Heavy Usage (1000+ artifacts)
- **CPU:** 4 cores
- **RAM:** 4 GB
- **Disk:** 20 GB

---

## 🔒 Security Considerations

### Production Deployment Checklist

- [ ] Change default port or use reverse proxy
- [ ] Enable HTTPS (via Let's Encrypt)
- [ ] Use strong API keys
- [ ] Regularly backup database
- [ ] Keep Docker and host OS updated
- [ ] Consider authentication layer (nginx basic auth or OAuth proxy)
- [ ] Restrict network access (firewall rules)

### Add Basic Authentication (nginx)

```bash
# Install htpasswd
apt-get install -y apache2-utils

# Create password file
htpasswd -c /etc/nginx/.htpasswd yourusername

# Update nginx config
location / {
    auth_basic "Think Spaces";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://<container-ip>:8000;
    ...
}
```

---

## 📝 Docker Commands Cheat Sheet

```bash
# Start application
docker compose up -d

# Stop application
docker compose down

# View logs
docker compose logs -f

# Restart application
docker compose restart

# Rebuild after code changes
docker compose up -d --build

# Check status
docker compose ps

# Execute command in container
docker compose exec thinkspaces bash

# View resource usage
docker stats think-spaces
```

---

## 🎯 Next Steps

After deployment:
1. Create your first Think Space at `/ui/spaces`
2. Add an agent (use `ollama` provider with `llama3.2` model, or `echo` for testing)
3. Add some artifacts
4. Test the chat interface

For advanced features like embeddings and Bloom, see [ROADMAP.md](./ROADMAP.md).

---

## 💬 Support

- **Issues:** https://github.com/yourusername/think-spaces/issues
- **Docs:** See [README.md](../README.md) and other docs in `/docs`

---

© 2025 Think Spaces - Containerized cognitive environments
