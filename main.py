import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="용돈기입장", page_icon="💸", layout="centered")

# 세션 상태로 임시 데이터 저장
if "ledger" not in st.session_state:
    st.session_state.ledger = pd.DataFrame(columns=["날짜", "분류", "내용", "금액", "수입/지출"])

st.title("💸 용돈기입장")

# 탭으로 기능 분리
tab1, tab2, tab3 = st.tabs(["➕ 입력하기", "📋 전체 내역", "📊 통계 보기"])

with tab1:
    st.subheader("➕ 새 내역 입력")

    with st.form("entry_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("날짜", value=datetime.today())
            category = st.selectbox("분류", ["식비", "교통", "문화", "쇼핑", "기타"])
        with col2:
            amount = st.number_input("금액", min_value=0, step=100)
            type_ = st.radio("수입/지출", ["수입", "지출"], horizontal=True)
        
        description = st.text_input("내용", placeholder="예: 편의점 간식")

        submitted = st.form_submit_button("저장")
        if submitted:
            new_data = {
                "날짜": pd.to_datetime(date).strftime("%Y-%m-%d"),
                "분류": category,
                "내용": description,
                "금액": amount,
                "수입/지출": type_
            }
            st.session_state.ledger = pd.concat(
                [st.session_state.ledger, pd.DataFrame([new_data])],
                ignore_index=True
            )
            st.success("저장되었습니다!")

with tab2:
    st.subheader("📋 전체 내역 보기")
    if st.session_state.ledger.empty:
        st.info("아직 입력된 내역이 없습니다.")
    else:
        df = st.session_state.ledger.copy()
        st.dataframe(df.sort_values("날짜", ascending=False), use_container_width=True)

with tab3:
    st.subheader("📊 통계 보기")
    df = st.session_state.ledger
    if df.empty:
        st.info("데이터가 없어요. 먼저 입력해 주세요!")
    else:
        col1, col2 = st.columns(2)
        income = df[df["수입/지출"] == "수입"]["금액"].sum()
        expense = df[df["수입/지출"] == "지출"]["금액"].sum()
        balance = income - expense

        with col1:
            st.metric("총 수입", f"{income:,.0f} 원")
            st.metric("총 지출", f"{expense:,.0f} 원")
        with col2:
            st.metric("잔액", f"{balance:,.0f} 원", delta=f"{income - expense:,.0f} 원")

        st.divider()

        # 카테고리별 지출 합계
        exp_by_cat = (
            df[df["수입/지출"] == "지출"]
            .groupby("분류")["금액"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(exp_by_cat)

