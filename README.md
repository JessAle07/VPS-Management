# VPS Account & Proxy Manager

A lightweight local web application built with **Streamlit** and **SQLite** to manage VPS environments, accounts, proxies, and payouts in a clean and structured way.

This tool replaces messy spreadsheets by providing a **clear hierarchy**, **safe workflows**, and **financial tracking** for multiple VPS account setups.

---

# 🚀 Features

## 🔹 VPS Management
- Create and manage multiple VPS profiles
- Rename or delete VPS safely
- Each VPS can contain multiple accounts

---

# 👤 Account Management

Each account stores structured information:

- Gmail
- Login IP
- PayPal profile
- Status:
  - Active
  - Inactive
  - Paused
  - Banned
- Linked proxies
- Payout history

Accounts can be:

- Banned (instead of deleted)
- Deleted safely
- Restored if needed

---

# 🌐 Proxy Management

Each account can have multiple proxies.

Features include:

- Add proxies in **bulk (one per line)**
- Delete proxies **individually**
- Collapsible proxy list for cleaner UI
- Proxy count indicator

Proxies are linked to accounts to avoid unnecessary duplication.

---

# 💰 Payout Tracking

Each account supports detailed payout logging:

Stored information:

- Date
- Time
- Amount
- Payment method

Supported payment methods:

- Amazon Gift Card
- PayPal

Each payout can have a status:

- ⏳ Pending
- ✅ Received
- 🚫 Banned (lost due to account ban)

---

# 📊 Global Payout Dashboard

The **Global Payouts** tab provides a complete financial overview.

### Metrics

- 💰 Total Pending
- ✅ Total Received
- 🚫 Total Lost (banned accounts)

### Management Features

- Confirm pending payouts
- Mark payouts as banned
- Undo status changes
- Delete payouts

All payouts are displayed in a structured table with account references.

---

# 📅 Monthly Earnings Dashboard

The **Monthly Overview** tab automatically groups payouts by month.

Only confirmed payouts are counted.

For each month the dashboard shows:

- 💰 Total Earned
- 🚫 Total Lost
- 💵 Net Profit
- 👤 Accounts Paid
- 🚫 Accounts Banned

This makes it easy to track **monthly performance and profitability**.

---

# 🚫 Banned Accounts Workflow

Accounts can be marked as **BANNED** instead of deleted.

Banned accounts:

- Are hidden from the active account list
- Retain important information such as proxies and login IPs
- Can be reviewed in a dedicated **Banned Accounts section**
- Can be restored if necessary

---

# 🔒 Local & Private

The application runs **entirely locally**.

- Uses **SQLite**
- No cloud services
- No external APIs
- No tracking or data sharing

All data is stored in:

```
data.db
```

on your machine.

---

# 🧠 Data Structure (Concept)

```
VPS
 └── Account
      ├── AccountInfo
      │     ├ Gmail
      │     ├ Login IP
      │     ├ Status
      │     └ PayPal
      │
      ├── Proxies
      │     └ Multiple entries
      │
      └── Payouts
            ├ Amount
            ├ Date/Time
            ├ Payment Method
            └ Status (Pending / Received / Banned)
```

This structure prevents duplicated data and keeps the interface clean.

---

# 🛠 Tech Stack

- Python 3
- Streamlit
- SQLAlchemy
- SQLite

---

# ▶️ How to Run

Install dependencies:

```bash
pip install streamlit sqlalchemy
```

Run the application:

```bash
streamlit run app.py
```

Open in your browser:

```
http://localhost:8501
```

---

# 📁 Repository Structure

```
.
├── app.py        # Main application
├── README.md     # Documentation
└── data.db       # Local database (auto generated)
```

---

# ⚠️ Important Notes

- `data.db` is created automatically on first run.
- **Do NOT upload `data.db` to GitHub**, as it contains your local data.
- This application is designed for **personal or internal management use**.

---

# 📌 Possible Future Improvements

- Charts for earnings visualization
- Earnings per VPS
- Earnings per account
- Export payouts to CSV / Excel
- Import accounts or proxies from CSV
- Authentication system
- Standalone packaged version

---

# 📜 License

This project is provided **as-is for personal use**.

Feel free to modify or extend it for your own workflows.

---

# 📦 Changelog

## v2.0

Major update including financial tracking features.

### New Features

- Payout tracking system
- Global payouts dashboard
- Pending / Received / Banned payout statuses
- Monthly earnings overview
- Net profit calculations
- Proxy list collapse UI
- Improved account management workflow

### Improvements

- Cleaner UI structure
- Better payout status management
- Safer deletion workflows
