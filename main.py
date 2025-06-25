import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

# 구글 시트 연결 함수
@st.cache_resource
def connect_gsheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["google_sheets"], scope
    )
    client = gspread.authorize(creds)
    sheet = client.open("용돈기입장").sheet1  # 시트 이름을 꼭 본인 것과 맞춰주세요!
    return sheet

# 시트 불러오기
sheet = connect_gsheet()

# 시트 데이터 불러오기
def get_data():
    records = sheet.get_all_records()
    df = pd.DataFrame(records)
    return df

# 새로운 항목 추가
def add_entry(date, amount, category, note):
    new_row = [date, amount, category, note]
    sheet.append_row(new_row)

# 앱 UI
st.title("💰 용돈기입장 앱")

with st.form("entry_form"):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("날짜", value=datetime.today())
        amount = st.number_input("금액", min_value=0, step=100)
    with col2:
        category = st.radio("구분", ["수입", "지출"], horizontal=True)
        note = st.text_input("비고", placeholder="예: 알바비, 커피 등")

    submitted = st.form_submit_button("기록 추가")
    if submitted:
        add_entry(str(date), amount, category, note)
        st.success("✅ 기록이 저장되었습니다!")

# 저장된 기록 보기
st.subheader("📋 기록 내역")
data = get_data()

if not data.empty:
    st.dataframe(data)
else:
    st.info("기록이 아직 없습니다. 위에서 입력해 주세요.")
