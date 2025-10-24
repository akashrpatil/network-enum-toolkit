# 🧠 Multi-Account AWS Command Executor

This repository contains a shell script - `multi_account_exec.sh` - that allows you to **execute any AWS CLI command across multiple AWS accounts** in sequence.

---

## ⚙️ Features
✅ Run a single AWS CLI command across multiple accounts  
✅ Supports account labels for easy identification  
✅ Output is clearly separated by account  
✅ Uses per-invocation environment credentials (no profile switching)  
✅ Safe: does not persist credentials locally  

---

## 🧑‍💻 Usage

### 1️⃣ Make the script executable
```bash
chmod +x multi_account_exec.sh
```

### 2️⃣ Edit credentials inside the script

Inside multi_account_exec.sh, update the section:
```
KEYS["acct1-ro"]="PUT ACCESS KEY"
SECRETS["acct1-ro"]="PUT SECRET KEY"
LABELS["acct1-ro"]="Account1 - ReadOnly"
```

You can define as many as you want:
```
KEYS["prod"]="AKIAxxxx"
SECRETS["prod"]="xxxxxxxx"
LABELS["prod"]="Production Account"
```

### 3️⃣ Run any AWS CLI command across all defined accounts

Examples:
```
./multi_account_exec.sh "aws sts get-caller-identity"
./multi_account_exec.sh "aws s3 ls"
./multi_account_exec.sh "aws ec2 describe-instances --region us-east-1"
```

Output:
```
============================================================
[Account1 - ReadOnly]
Running: aws sts get-caller-identity
------------------------------------------------------------
{
    "UserId": "AIDAEXAMPLE",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/test"
}

============================================================
[Account2 - AllAccessService]
Running: aws sts get-caller-identity
------------------------------------------------------------
...

```
### 🔒 Security Best Practices

Never commit real access keys to GitHub.
Replace them with placeholders (PUT ACCESS KEY, PUT SECRET KEY) before committing.
Optionally, move secrets to an .env file and source it (see below).
Always use IAM users/roles with least privilege.

### 🧰 Using a Local .env File (Optional)

You can keep your credentials out of the script by storing them locally.

Create .env (copy from env.sample):
```
KEYS["acct1-ro"]=$AWS_KEY1
SECRETS["acct1-ro"]=$AWS_SECRET1
LABELS["acct1-ro"]="Account1 - ReadOnly"
```

Then load it:
```
source .env
./multi_account_exec.sh "aws s3 ls"
```

### 🧱 Requirements
```
bash (Linux/macOS/WSL)
AWS CLI v2 installed and configured
Install AWS CLI:
sudo apt install awscli -y
# or
brew install awscli
```

### ⚠️ Disclaimer

- This tool is for authorized internal use only.
- Do not use on accounts you do not own or have permission to access.
- You are responsible for all actions executed via your AWS credentials.


👨‍💻 Author
```
Developed by Akash Rajendra Patil
Cyber Security Professional - Red Teaming | Cloud | Infrastructure | Application
```
