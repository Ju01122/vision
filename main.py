import streamlit as st
import pandas as pd
from datetime import date, datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# =========================
# 🔐 Google Sheets 연결
# =========================
@st.cache_resource
def connect_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("용돈기입장").sheet1  # ← 시트 이름 변경 가능
    return sheet

sheet = connect_gsheet()

# =========================
# 🧮 구글시트에서 데이터 불러오기
# =========================
@st.cache_data(ttl=0)
def load_data():
    rows = sheet.get_all_values()
    if not rows or rows[0] != ["날짜", "항목", "금액", "유형", "비고"]:
        sheet.update("A1:E1", [["날짜", "항목", "금액", "유형", "비고"]])
        return pd.DataFrame(columns=["날짜", "항목", "금액", "유형", "비고"])
    df = pd.DataFrame(rows[1:], columns=rows[0])
    df["금액"] = pd.to_numeric(df["금액"], errors="coerce").fillna(0)
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")
    return df

def append_row_to_sheet(row):
    sheet.append_row(row)

# =========================
# 📋 앱 UI 시작
# =========================
st.set_page_config(page_title="용돈기입장", layout="centered")
st.title("💸 용돈기입장 (Google Sheets 저장)")
st.write("수입과 지출을 간편하게 기록하고 확인하세요!")

data = load_data()

# =========================
# 📥 입력 폼
# =========================
st.subheader("📥 새로운 내역 입력")
with st.form(key="entry_form"):
    col1, col2 = st.columns(2)
    with col1:
        date_input = st.date_input("날짜", date.today())
    with col2:
        type_input = st.radio("유형", ["수입", "지출"], horizontal=True)

    title_input = st.text_input("항목 (예: 알바, 편의점)")
    amount_input = st.number_input("금액", min_value=0, step=100)
    note_input = st.text_input("비고 (선택)")

    submitted = st.form_submit_button("저장하기")

    if submitted:
        if title_input and amount_input > 0:
            row = [
                str(date_input),
                title_input,
                amount_input if type_input == "수입" else -amount_input,
                type_input,
                note_input
            ]
            append_row_to_sheet(row)
            st.success("✅ 기록이 저장되었습니다!")
            st.rerun()
        else:
            st.warning("⚠️ 항목과 금액을 모두 입력해주세요.")

# =========================
# 📜 기록 보기
# =========================
st.subheader("📜 기록 내역")
if data.empty:
    st.info("기록이 없습니다. 위에서 추가해주세요.")
else:
    st.dataframe(
        data.sort_values("날짜", ascending=False),
        use_container_width=True
    )

# =========================
# 📊 분석
# =========================
if not data.empty:
    st.subheader("📊 월별 수입/지출 합계")
    data["월"] = data["날짜"].dt.to_period("M").astype(str)
    summary = data.groupby(["월", "유형"])["금액"].sum().unstack().fillna(0)
    st.bar_chart(summary)

    st.subheader("📂 항목별 지출 분석")
    expenses = data[data["유형"] == "지출"]
    if not expenses.empty:
        expense_summary = expenses.groupby("항목")["금액"].sum().sort_values()
        st.bar_chart(-expense_summary)  # 지출은 음수로 표시
    else:
        st.info("지출 내역이 있어야 분석이 가능합니다.")
