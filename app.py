import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, time

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

# 🔥 Payout actualizado
class Payout(Base):
    __tablename__ = "payouts"
    id = Column(Integer, primary_key=True)
    amount = Column(String)
    method = Column(String)
    datetime = Column(String)
    received = Column(Integer, default=0)  # 🔥 NUEVO
    account_id = Column(Integer, ForeignKey("accounts.id"))

Base.metadata.create_all(engine)

# 🔥 Si la columna no existe (DB vieja), la agrega sin borrar nada
with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE payouts ADD COLUMN received INTEGER DEFAULT 0"))
    except:
        pass

st.set_page_config(page_title="VPS Manager", layout="wide")
st.title("VPS → Accounts → Proxies")

session = SessionLocal()

# 🔥 TABS NUEVAS
tab1, tab2, tab3 = st.tabs(["Main Manager", "📊 Global Payouts", "📅 Monthly Stats"])

# ============================================================
# ======================== TAB 1 =============================
# ============================================================
with tab1:

    st.subheader("VPS")

    new_vps = st.text_input("Create VPS")
    if st.button("Add VPS"):
        if new_vps.strip():
            if not session.query(VPS).filter_by(name=new_vps.strip()).first():
                session.add(VPS(name=new_vps.strip()))
                session.commit()
                st.rerun()
            else:
                st.error("VPS already exists")

    vps_list = session.query(VPS).order_by(VPS.id).all()
    if not vps_list:
        st.stop()

    vps_names = [v.name for v in vps_list]

    if "selected_vps" not in st.session_state:
        st.session_state.selected_vps = vps_names[0]

    if st.session_state.selected_vps not in vps_names:
        st.session_state.selected_vps = vps_names[0]

    selected_name = st.selectbox(
        "Select VPS",
        vps_names,
        index=vps_names.index(st.session_state.selected_vps)
    )

    st.session_state.selected_vps = selected_name
    vps = session.query(VPS).filter_by(name=selected_name).first()

    rename_vps = st.text_input("Rename VPS", value=vps.name)
    if st.button("Update VPS Name"):
        if rename_vps.strip() and rename_vps != vps.name:
            if not session.query(VPS).filter_by(name=rename_vps.strip()).first():
                vps.name = rename_vps.strip()
                session.commit()
                st.session_state.selected_vps = rename_vps.strip()
                st.rerun()
            else:
                st.error("Name already exists")

    st.warning("⚠️ Delete VPS")
    if st.checkbox(f"I understand, delete VPS '{vps.name}'"):
        if st.button("🗑️ DELETE VPS", type="primary"):
            accounts_to_delete = session.query(Account).filter_by(vps_id=vps.id).all()
            for acc in accounts_to_delete:
                session.query(Proxy).filter_by(account_id=acc.id).delete()
                session.query(AccountInfo).filter_by(account_id=acc.id).delete()
                session.query(Payout).filter_by(account_id=acc.id).delete()
                session.delete(acc)
            session.delete(vps)
            session.commit()
            st.session_state.selected_vps = None
            st.rerun()

    # =========================
    # ACCOUNTS
    # =========================
    st.subheader("Accounts")

    new_account = st.text_input("Create Account")
    if st.button("Add Account"):
        if new_account.strip():
            acc = Account(name=new_account.strip(), vps_id=vps.id)
            session.add(acc)
            session.commit()
            session.add(AccountInfo(account_id=acc.id))
            session.commit()
            st.rerun()

    accounts = session.query(Account).filter_by(vps_id=vps.id).all()
    paypals = session.query(PayPal).all()

    active_accounts = []
    banned_accounts = []

    for acc in accounts:
        info = session.query(AccountInfo).filter_by(account_id=acc.id).first()
        if info and info.status == "banned":
            banned_accounts.append(acc)
        else:
            active_accounts.append(acc)

    # =========================
    # ACTIVE ACCOUNTS
    # =========================
    for acc in active_accounts:
        info = session.query(AccountInfo).filter_by(account_id=acc.id).first()

        with st.expander(acc.name):

            col1, col2 = st.columns(2)

            if col1.button("🚫 Ban", key=f"ban_{acc.id}"):
                info.status = "banned"
                session.commit()
                st.rerun()

            if col2.button("🗑️ Delete", key=f"del_acc_{acc.id}"):
                session.query(Proxy).filter_by(account_id=acc.id).delete()
                session.query(Payout).filter_by(account_id=acc.id).delete()
                session.delete(info)
                session.delete(acc)
                session.commit()
                st.rerun()

            info.gmail = st.text_input("Gmail", info.gmail or "", key=f"gmail_{acc.id}")
            info.ip_login = st.text_input("Login IP", info.ip_login or "", key=f"ip_{acc.id}")

            st.markdown("### 💰 Register Payout")

            dcol, tcol = st.columns(2)
            date_val = dcol.date_input("Date", key=f"d_{acc.id}")
            time_val = tcol.time_input("Time", value=time(12,0), key=f"t_{acc.id}")

            col_amount, col_method = st.columns(2)
            amount_input = col_amount.text_input("Amount ($)", key=f"amount_{acc.id}")
            method_input = col_method.selectbox(
                "Payment Method",
                ["Amazon Gift Card", "PayPal"],
                key=f"method_{acc.id}"
            )

            if st.button("Save Payout", key=f"save_payout_{acc.id}"):
                if date_val and time_val and amount_input:
                    combined = datetime.combine(date_val, time_val)
                    session.add(
                        Payout(
                            amount=amount_input,
                            method=method_input,
                            datetime=combined.strftime("%d-%m-%Y %H:%M"),
                            account_id=acc.id,
                            received=0
                        )
                    )
                    session.commit()
                    st.success("Payout saved.")
                    st.rerun()

            payouts = session.query(Payout).filter_by(account_id=acc.id).order_by(Payout.id.desc()).all()
            for p in payouts:
                status_icon = "✅" if p.received else "❌"
                st.write(f"{p.datetime} — ${p.amount} — {p.method} — {status_icon}")

            # 🔹 RESTAURAR STATUS
            info.status = st.selectbox(
                "Status",
                ["active", "inactive", "paused"],
                index=["active","inactive","paused"].index(info.status or "active"),
                key=f"status_{acc.id}"
            )

            # 🔹 RESTAURAR PAYPAL
            paypal_options = ["None"] + [p.email for p in paypals]

            current_index = 0
            if info.paypal_id:
                current_pp = session.query(PayPal).get(info.paypal_id)
                if current_pp and current_pp.email in paypal_options:
                    current_index = paypal_options.index(current_pp.email)

            selected_paypal = st.selectbox(
                "PayPal",
                paypal_options,
                index=current_index,
                key=f"paypal_{acc.id}"
            )

            if selected_paypal == "None":
                info.paypal_id = None
            else:
                info.paypal_id = session.query(PayPal).filter_by(email=selected_paypal).first().id

            session.commit()

            # =========================
            # 🌐 PROXIES COLAPSABLES
            # =========================
            proxies = session.query(Proxy).filter_by(account_id=acc.id).all()
            proxy_count = len(proxies)

            with st.expander(f"🌐 Proxies ({proxy_count})"):

                if proxy_count == 0:
                    st.info("No proxies assigned.")
                else:
                    for p in proxies:
                        col1, col2 = st.columns([6,1])
                        col1.write(p.proxy)
                        if col2.button("❌", key=f"proxy_{p.id}"):
                            session.delete(p)
                            session.commit()
                            st.rerun()

                new_proxies = st.text_area("Add proxies (one per line)", key=f"np_{acc.id}")

                if st.button("Add Proxies", key=f"addp_{acc.id}"):
                    for line in new_proxies.splitlines():
                        if line.strip():
                            session.add(Proxy(proxy=line.strip(), account_id=acc.id))
                    session.commit()
                    st.rerun()
    st.divider()
    st.subheader("PayPal Management")

    new_pp = st.text_input("New PayPal")
    if st.button("Add PayPal Account"):
        if new_pp.strip():
            if not session.query(PayPal).filter_by(email=new_pp.strip()).first():
                session.add(PayPal(email=new_pp.strip()))
                session.commit()
                st.rerun()
            else:
                st.error("Already exists")
    st.divider()
    st.subheader("🚫 Banned Accounts")

    for acc in banned_accounts:
        with st.expander(acc.name):

            info = session.query(AccountInfo).filter_by(account_id=acc.id).first()

            st.write(f"Gmail: {info.gmail or '-'}")
            st.write(f"Login IP: {info.ip_login or '-'}")

            proxies = session.query(Proxy).filter_by(account_id=acc.id).all()

            st.markdown("**Proxies:**")
            for p in proxies:
                st.write(p.proxy)

            if st.button("♻️ Unban", key=f"unban_{acc.id}"):
                info.status = "active"
                session.commit()
                st.rerun()
# ============================================================
# ======================== TAB 2 =============================
# ============================================================
with tab2:

    st.subheader("📊 Global Payout Overview")

    payouts = session.query(Payout).order_by(Payout.id.desc()).all()

    total_pending = 0
    total_received = 0
    total_banned = 0

    for p in payouts:
        try:
            value = float(p.amount)
        except:
            value = 0

        if p.received == 1:
            total_received += value
        elif p.received == 2:
            total_banned += value
        else:
            total_pending += value

    colA, colB, colC = st.columns(3)

    colA.metric("💰 Pending", f"${total_pending:.2f}")
    colB.metric("✅ Received", f"${total_received:.2f}")
    colC.metric("🚫 Lost (Banned)", f"${total_banned:.2f}")

    st.divider()

    # 🔥 ORDENAR payouts: Pending → Received → Banned
    payouts_sorted = sorted(
        payouts,
        key=lambda p: (
            0 if p.received == 0 else
            1 if p.received == 1 else
            2
        )
    )

    # 🔥 Encabezados tipo tabla
    h1, h2, h3, h4, h5, h6 = st.columns([2,2,1,2,1,2])

    h1.markdown("**Date**")
    h2.markdown("**Account**")
    h3.markdown("**$**")
    h4.markdown("**Method**")
    h5.markdown("**Status**")
    h6.markdown("**Actions**")

    st.markdown("---")

    for p in payouts_sorted:

        account = session.query(Account).get(p.account_id)

        c1, c2, c3, c4, c5, c6 = st.columns([2,2,1,2,1,2])

        c1.write(p.datetime)
        c2.write(account.name if account else "Unknown")
        c3.write(f"${p.amount}")
        c4.write(p.method)

        # =====================
        # STATUS LOGIC
        # =====================

        if p.received == 1:

            c5.markdown("✅ Received")

            if c6.button("↩ Undo", key=f"undo_payout_{p.id}"):
                p.received = 0
                session.commit()
                st.rerun()

        elif p.received == 2:

            c5.markdown("🚫 Banned")

            if c6.button("↩ Undo Ban", key=f"unban_payout_{p.id}"):
                p.received = 0
                session.commit()
                st.rerun()

        else:

            c5.markdown("⏳ Pending")

            col_confirm, col_ban = c6.columns(2)

            if col_confirm.button("Confirm", key=f"conf_payout_{p.id}"):
                p.received = 1
                session.commit()
                st.rerun()

            if col_ban.button("Ban", key=f"ban_payout_{p.id}"):
                p.received = 2
                session.commit()
                st.rerun()

        # Delete alineado debajo
        c_del = st.columns([2,2,1,2,1,2])[5]

        if c_del.button("🗑", key=f"del_global_{p.id}"):
            session.delete(p)
            session.commit()
            st.rerun()

        st.markdown("---")
# ============================================================
# ======================== TAB 3 =============================
# ============================================================
with tab3:

    st.subheader("📅 Monthly Earnings Overview")

    payouts = session.query(Payout).all()

    monthly_data = {}

    for p in payouts:

        # ignorar pending
        if p.received == 0:
            continue

        try:
            value = float(p.amount)
        except:
            value = 0

        try:
            date_obj = datetime.strptime(p.datetime, "%d-%m-%Y %H:%M")
            month_key = date_obj.strftime("%Y-%m")
        except:
            continue

        if month_key not in monthly_data:
            monthly_data[month_key] = {
                "earned": 0,
                "lost": 0,
                "paid_accounts": 0,
                "banned_accounts": 0
            }

        if p.received == 1:
            monthly_data[month_key]["earned"] += value
            monthly_data[month_key]["paid_accounts"] += 1

        elif p.received == 2:
            monthly_data[month_key]["lost"] += value
            monthly_data[month_key]["banned_accounts"] += 1

    if not monthly_data:
        st.info("No payout data yet.")
    else:

        for month in sorted(monthly_data.keys(), reverse=True):

            earned = monthly_data[month]["earned"]
            lost = monthly_data[month]["lost"]
            paid_acc = monthly_data[month]["paid_accounts"]
            banned_acc = monthly_data[month]["banned_accounts"]

            net = earned - lost

            st.markdown(f"## 📅 {month}")

            col1, col2, col3 = st.columns(3)

            col1.metric("💰 Earned", f"${earned:.2f}")
            col2.metric("🚫 Lost", f"${lost:.2f}")
            col3.metric("💵 Net", f"${net:.2f}")

            col4, col5 = st.columns(2)

            col4.metric("👤 Accounts Paid", paid_acc)
            col5.metric("🚫 Accounts Banned", banned_acc)

            st.markdown("---")
            
session.close()
