# GitHub Token Generation & Setup Guide

## Step 1: Generate a Personal Access Token

1. Go to **GitHub Settings**: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Fill in the details:
   - **Token name**: `virtual-pamudu-token` (or any descriptive name)
   - **Expiration**: `90 days` (or longer as needed)
   - **Scopes**: Select these permissions:
     - ✅ `repo` (Full control of private repositories)
     - ✅ `read:user` (Read user profile data)
     - ✅ `user:email` (Access user email addresses)

4. Click **"Generate token"**
5. **Copy the token immediately** (you won't see it again!)

## Step 2: Set Environment Variable

### On Windows (Command Prompt):
```cmd
set GITHUB_TOKEN=your_token_here
```

### On Windows (PowerShell):
```powershell
$env:GITHUB_TOKEN="your_token_here"
```

### On Windows (Permanent - Edit System Variables):
1. Press `Win + R` → type `systempropertiesadvanced.exe`
2. Click **"Environment Variables"**
3. Click **"New..."** under "User variables"
4. Variable name: `GITHUB_TOKEN`
5. Variable value: `your_token_here` (paste your token)
6. Click **"OK"** and restart your terminal

### On macOS/Linux:
```bash
export GITHUB_TOKEN="your_token_here"
```

To make it permanent, add to `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export GITHUB_TOKEN="your_token_here"' >> ~/.bashrc
source ~/.bashrc
```

## Step 3: Verify Setup

Run this command to confirm your token is set:

### Windows:
```cmd
echo %GITHUB_TOKEN%
```

### macOS/Linux:
```bash
echo $GITHUB_TOKEN
```

Should output: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx`

## Step 4: Test Authentication

Run the test script:
```bash
python test_github.py
```

Expected output:
