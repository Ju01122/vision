import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date

st.set_page_config(page_title="용돈기입장", layout="centered")

st.title("💸 용돈기입장 앱")
st.write("수입과 지출을 간편하게 기록하고 확인하세요!")

# CSV 저장 파일명
DATA_FILE = "money_log.csv"

# CSV 파일 불러오기
@st.cache_data
def load_data():
    try:
        return pd.read_csv(DATA_FILE, parse_dates=["날짜"])
    except FileNotFoundError:
        return pd.DataFrame(columns=["날짜", "항목", "금액", "유형"])

# CSV 파일 저장하기
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

data = load_data()

# 입력 폼
st.subheader("📥 새로운 내역 입력")
with st.form("entry_form"):
    col1, col2 = st.columns(2)
    with col1:
        date_input = st.date_input("날짜", date.today())
    with col2:
        type_input = st.radio("유형", ["수입", "지출"], horizontal=True)
    
    title_input = st.text_input("항목 (예: 편의점, 알바, 용돈)")
    amount_input = st.number_input("금액", min_value=0, step=100)
    submitted = st.form_submit_button("저장")

    if submitted and title_input and amount_input:
        new_data = pd.DataFrame({
            "날짜": [date_input],
            "항목": [title_input],
            "금액": [amount_input if type_input == "수입" else -amount_input],
            "유형": [type_input]
        })
        data = pd.concat([data, new_data], ignore_index=True)
        save_data(data)
        st.success("기록이 저장되었습니다!")
        st.rerun()

# 내역 표시
st.subheader("📜 기록 내역")
if data.empty:
    st.info("아직 기록이 없어요. 위에서 첫 항목을 입력해보세요!")
else:
    st.dataframe(data.sort_values("날짜", ascending=False), use_container_width=True)

    # 시각화
    st.subheader("📊 월별 분석 차트")
    data["월"] = data["날짜"].dt.to_period("M").astype(str)

    monthly_summary = data.groupby(["월", "유형"])["금액"].sum().unstack().fillna(0)
    st.bar_chart(monthly_summary)

    # 항목별 지출 비중 (파이차트)
    st.subheader("🥧 항목별 지출 비중")
    expense_data = data[data["유형"] == "지출"]
    if not expense_data.empty:
        category_summary = expense_data.groupby("항목")["금액"].sum()
        fig, ax = plt.subplots()
        ax.pie(-category_summary, labels=category_summary.index, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)
    else:
        st.info("지출 기록이 있어야 파이차트를 볼 수 있어요.")

