import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="용돈기입장", layout="centered")
st.title("💸 용돈기입장 앱")
st.write("수입과 지출을 간편하게 기록하고 확인하세요!")

DATA_FILE = "money_log.csv"

# CSV 파일 불러오기
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(DATA_FILE)
        if "비고" not in df.columns:
            df["비고"] = ""
        df["날짜"] = pd.to_datetime(df["날짜"])
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["날짜", "항목", "금액", "유형", "비고"])

# CSV 저장 함수
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# 데이터 불러오기
data = load_data()

# 입력 폼
st.subheader("📥 새로운 내역 입력")
with st.form(key="income_expense_form"):  # 중복 피하기 위해 고유한 key 사용
    col1, col2 = st.columns(2)
    with col1:
        date_input = st.date_input("날짜", date.today())
    with col2:
        type_input = st.radio("유형", ["수입", "지출"], horizontal=True)

    title_input = st.text_input("항목 (예: 편의점, 알바, 용돈)")
    amount_input = st.number_input("금액", min_value=0, step=100)
    note_input = st.text_input("비고 (선택)")

    submitted = st.form_submit_button("저장")

    if submitted:
        if title_input and amount_input > 0:
            new_data = pd.DataFrame({
                "날짜": [pd.to_datetime(date_input)],
                "항목": [title_input],
                "금액": [amount_input if type_input == "수입" else -amount_input],
                "유형": [type_input],
                "비고": [note_input]
            })
            data = pd.concat([data, new_data], ignore_index=True)
            save_data(data)
            st.success("✅ 기록이 저장되었습니다!")
            st.rerun()
        else:
            st.warning("⚠️ 항목과 금액을 모두 입력해주세요.")

# 기록 내역 표시
st.subheader("📜 기록 내역")
if data.empty:
    st.info("아직 기록이 없습니다. 위에서 항목을 추가해주세요!")
else:
    st.dataframe(
        data[["날짜", "항목", "금액", "유형", "비고"]].sort_values("날짜", ascending=False),
        use_container_width=True
    )

    # 월별 분석
    st.subheader("📊 월별 수입/지출 합계")
    data["월"] = data["날짜"].dt.to_period("M").astype(str)
    summary = data.groupby(["월", "유형"])["금액"].sum().unstack().fillna(0)
    st.bar_chart(summary)

    # 항목별 지출 분석
    st.subheader("📂 항목별 지출 내역")
    expense_data = data[data["유형"] == "지출"]
    if not expense_data.empty:
        item_summary = expense_data.groupby("항목")["금액"].sum().sort_values()
        st.bar_chart(-item_summary)  # 지출은 음수이므로 -로 표시
    else:
        st.info("지출 내역이 있어야 항목별 분석이 가능합니다.")
