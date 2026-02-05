import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

# --------------------
# DATABASE
# --------------------
engine = create_engine("sqlite:///data.db", echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class VPS(Base):
    __tablename__ = "vps"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    vps_id = Column(Integer, ForeignKey("vps.id"))

class PayPal(Base):
    __tablename__ = "paypal"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)

class AccountInfo(Base):
    __tablename__ = "account_info"
    id = Column(Integer, primary_key=True)
    gmail = Column(String)
    ip_login = Column(String)
    status = Column(String, default="active")
    last_payment = Column(String)

    account_id = Column(Integer, ForeignKey("accounts.id"), unique=True)
    paypal_id = Column(Integer, ForeignKey("paypal.id"), nullable=True)

class Proxy(Base):
    __tablename__ = "proxies"
    id = Column(Integer, primary_key=True)
    proxy = Column(String)
    account_id = Column(Integer, ForeignKey("accounts.id"))

Base.metadata.create_all(engine)

# --------------------
# UI
# --------------------
st.set_page_config(page_title="VPS Manager", layout="wide")
st.title("VPS → Accounts → Proxies")

session = SessionLocal()

# --------------------
# VPS
# --------------------
st.subheader("VPS")
vps_name = st.text_input("Create VPS")
if st.button("Add VPS"):
    if vps_name.strip():
        session.add(VPS(name=vps_name.strip()))
        session.commit()
        st.rerun()

vps_list = session.query(VPS).all()
if not vps_list:
    st.stop()

vps = st.selectbox("Select VPS", vps_list, format_func=lambda v: v.name)

# --------------------
# ADD ACCOUNT
# --------------------
st.subheader("Accounts")
account_name = st.text_input("Create Account")
if st.button("Add Account"):
    if account_name.strip():
        acc = Account(name=account_name.strip(), vps_id=vps.id)
        session.add(acc)
        session.commit()
        session.add(AccountInfo(account_id=acc.id, status="active"))
        session.commit()
        st.rerun()

accounts = session.query(Account).filter_by(vps_id=vps.id).all()

# --------------------
# PAYPALS
# --------------------
st.subheader("PayPal Profiles")
paypal_email = st.text_input("Add PayPal")
if st.button("Add PayPal"):
    if paypal_email.strip():
        session.add(PayPal(email=paypal_email.strip()))
        session.commit()
        st.rerun()

paypals = session.query(PayPal).all()

# --------------------
# SPLIT ACTIVE / BANNED
# --------------------
active_accounts = []
banned_accounts = []

for acc in accounts:
    info = session.query(AccountInfo).filter_by(account_id=acc.id).first()
    if not info:
        info = AccountInfo(account_id=acc.id, status="active")
        session.add(info)
        session.commit()

    if info.status == "banned":
        banned_accounts.append(acc)
    else:
        active_accounts.append(acc)

# --------------------
# ACTIVE ACCOUNTS
# --------------------
for acc in active_accounts:
    info = session.query(AccountInfo).filter_by(account_id=acc.id).first()

    with st.expander(acc.name, expanded=False):

        st.warning("⚠️ Danger zone")

        col1, col2 = st.columns(2)

        confirm_ban = col1.checkbox(
            f"I understand, mark '{acc.name}' as BANNED",
            key=f"confirm_ban_{acc.id}"
        )

        if confirm_ban:
            if col1.button("🚫 MARK AS BANNED", key=f"ban_{acc.id}"):
                info.status = "banned"
                session.commit()
                st.rerun()

        confirm_delete = col2.checkbox(
            f"I understand, delete '{acc.name}'",
            key=f"confirm_del_{acc.id}"
        )

        if confirm_delete:
            if col2.button("🗑️ DELETE ACCOUNT", key=f"delete_{acc.id}", type="primary"):
                session.query(Proxy).filter_by(account_id=acc.id).delete()
                session.query(AccountInfo).filter_by(account_id=acc.id).delete()
                session.delete(acc)
                session.commit()
                st.rerun()

        st.markdown("### Account Info")

        info.gmail = st.text_input("Gmail", info.gmail or "", key=f"gmail_{acc.id}")
        info.ip_login = st.text_input("Login IP", info.ip_login or "", key=f"ip_{acc.id}")
        info.last_payment = st.text_input("Last Payment", info.last_payment or "", key=f"pay_{acc.id}")

        info.status = st.selectbox(
            "Estado en Earn",
            ["active", "inactive", "paused"],
            index=["active", "inactive", "paused"].index(info.status or "active"),
            key=f"status_{acc.id}"
        )

        paypal_choice = st.selectbox(
            "PayPal",
            ["None"] + [p.email for p in paypals],
            index=0 if not info.paypal_id else
            [p.id for p in paypals].index(info.paypal_id) + 1,
            key=f"paypal_{acc.id}"
        )

        info.paypal_id = None if paypal_choice == "None" else \
            session.query(PayPal).filter_by(email=paypal_choice).first().id

        session.commit()

        st.divider()
        st.markdown("### Proxies")

        proxies = session.query(Proxy).filter_by(account_id=acc.id).all()

        for p in proxies:
            c1, c2 = st.columns([6, 1])
            c1.write(p.proxy)
            if c2.button("❌", key=f"del_proxy_{p.id}"):
                session.delete(p)
                session.commit()
                st.rerun()

        new_proxies = st.text_area(
            "Add proxies (one per line)",
            key=f"new_proxy_{acc.id}",
            height=150
        )

        if st.button("Add Proxies", key=f"add_proxy_{acc.id}"):
            for line in new_proxies.splitlines():
                if line.strip():
                    session.add(Proxy(proxy=line.strip(), account_id=acc.id))
            session.commit()
            st.rerun()

# --------------------
# BANNED ACCOUNTS
# --------------------
st.divider()
st.subheader("🚫 Banned Accounts (IP reference)")

for acc in banned_accounts:
    with st.expander(f"🚫 {acc.name}", expanded=False):

        proxies = session.query(Proxy).filter_by(account_id=acc.id).all()

        if proxies:
            for p in proxies:
                st.write(p.proxy)
        else:
            st.info("No proxies stored")

        st.divider()

        confirm_delete = st.checkbox(
            f"Permanently delete '{acc.name}'",
            key=f"confirm_del_banned_{acc.id}"
        )

        if confirm_delete:
            if st.button("🗑️ DELETE PERMANENTLY", key=f"delete_banned_{acc.id}"):
                session.query(Proxy).filter_by(account_id=acc.id).delete()
                session.query(AccountInfo).filter_by(account_id=acc.id).delete()
                session.delete(acc)
                session.commit()
                st.rerun()

session.close()









