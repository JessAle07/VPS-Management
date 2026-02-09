# VPS Account & Proxy Manager

A lightweight local web application built with **Streamlit** and **SQLite** to manage VPS environments, accounts, and proxies in a clean and structured way.

This tool was designed to replace messy spreadsheets by providing a clear hierarchy and safe workflows for handling active and banned accounts.

---

## 🚀 Features

### 🔹 VPS Management
- Create and manage multiple VPS profiles
- Each VPS contains multiple accounts

### 🔹 Account Management
- Store account metadata:
  - Gmail
  - Login IP
  - PayPal profile
  - Earn status (active / inactive / paused / banned)
  - Last payment date
- Clean separation between **account info** and **proxies**
- Safe account deletion with confirmation

### 🔹 Proxy Management
- Add proxies in bulk (one per line)
- Each proxy is stored individually
- Delete proxies one by one
- Proxies are linked to accounts, not duplicated unnecessarily

### 🔹 Banned Accounts Workflow
- Mark accounts as **BANNED** instead of deleting them
- Banned accounts:
  - Are hidden from the active accounts list
  - Retain only relevant data (mainly proxies / IPs)
- Dedicated section to review banned accounts and their IPs
- Option to permanently delete banned accounts when no longer needed

### 🔹 Local & Private
- Runs entirely locally
- Uses SQLite (`data.db`) stored on your machine
- No external services, no cloud dependency

---

## 🧠 Data Structure (Concept)

VPS
└── Account
├── AccountInfo (gmail, login IP, status, PayPal, etc.)
└── Proxies (multiple, individually deletable)

yaml
Copiar código

This design avoids duplicated data and keeps the UI clean and readable.

---

## 🛠️ Tech Stack

- Python 3
- Streamlit
- SQLAlchemy
- SQLite

---

## ▶️ How to Run

1. Install dependencies:
   ```bash
   pip install streamlit sqlalchemy
Run the app:

bash
Copiar código
streamlit run app.py
Open the browser at:

arduino
Copiar código
http://localhost:8501
📁 Repository Structure
pgsql
Copiar código
.
├── app.py        # Main application
├── README.md     # Documentation
└── data.db       # Local database (DO NOT COMMIT)
⚠️ Notes
data.db is generated automatically on first run.

Do not commit data.db to GitHub, as it contains local data.

This app is intended for personal or internal use.

📌 Future Improvements (Optional Ideas)
Export data to Excel

Import accounts from CSV

Global proxy blacklist

Tags or notes for accounts

Authentication / password protection

Packaging as a standalone executable

📜 License
This project is provided as-is for personal use.
Feel free to fork and adapt it to your needs.

yaml
Copiar código

---

## Changelog
### v1.1
- Added calendar and time picker for last payment
- Improved banned account workflow
Note: Before updating, make sure to save your last payment dates so you dont lose them once the update is applied. To update you just need to download the new app,py, as the database will remain the same.


venv/


