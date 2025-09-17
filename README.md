# AWS EC2 Pricing Tool


A simple Python CLI tool to fetch 
  - EC2 instance types
  - vCPUs
  - memory
  - pricing** (hourly, monthly, yearly) for any AWS region.
---

## Output
<img width="1626" height="141" alt="image" src="https://github.com/user-attachments/assets/560d3487-79db-4e51-9cb7-525898a2a80d" />

## 🔹 Setup Instructions

### 1. Create `.env` File
Encrypt your AWS keys using base64 and save them in `.env`:

```bash
echo -n "YOUR_AWS_ACCESS_KEY" | base64
echo -n "YOUR_AWS_SECRET_KEY" | base64
```

### 2. Create `.env` File
```bash

cat <<EOT > .env
AWS_ACCESS_KEY_ENC=BASE64_ENCODED_ACCESS_KEY
AWS_SECRET_KEY_ENC=BASE64_ENCODED_SECRET_KEY
EOT
```
### 3. Install Dependencies
```
pip install python-dotenv
```

### 4. Clone the Repository
```
git clone https://github.com/Fir3eye/aws-ec2-pricing-tool.git
cd aws-ec2-pricing-tool
```

### 5. Run the App
```
python3 aws-price.py
```


