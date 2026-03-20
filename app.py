import streamlit as st
import math

# 페이지 설정
st.set_page_config(page_title="우리 집 관리비 예측기", layout="wide")

# 계산 로직 함수들
def calc_elec(usage):
    base = 730
    unit = 105.0
    climate = 9.0
    fuel = 5.0
    common = 1890
    support = 1350
    
    subtotal = base + (usage * unit) + (usage * climate) + (usage * fuel)
    vat = round(subtotal * 0.1)
    fund = math.floor((subtotal * 0.037) / 10) * 10
    return int(subtotal + vat + fund + common - support)

def calc_water(usage):
    return int((usage * 990) + 490)

def calc_gas(usage, price):
    supply = (usage * price) + 2000
    return int(supply * 1.1)

# --- 웹 화면 구성 ---
st.title("📊 우리 집 관리비 실시간 예측 대시보드")
st.markdown("계량기 숫자를 입력하면 이번 달 최종 요금을 예측합니다.")

# 사이드바: 설정값
st.sidebar.header("⚙️ 기본 설정")
today = st.sidebar.slider("오늘이 며칠인가요?", 1, 31, 15)
total_days = 30
lpg_unit_price = st.sidebar.number_input("LPG 단가 (1m³당)", value=4200)
fixed_fee = st.sidebar.number_input("고정 공용관리비", value=50000)

# 메인 화면: 입력부
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("⚡ 전기 (kWh)")
    e_now = st.number_input("현재 사용량", key="elec", value=41.0)
    e_pred_usage = (e_now / today) * total_days
    
with col2:
    st.subheader("💧 수도 (톤)")
    w_now = st.number_input("현재 사용량", key="water", value=2.0)
    w_pred_usage = (w_now / today) * total_days

with col3:
    st.subheader("🔥 가스 (m³)")
    g_now = st.number_input("현재 사용량", key="gas", value=5.0)
    g_pred_usage = (g_now / today) * total_days

# 계산 결과
curr_total = calc_elec(e_now) + calc_water(w_now) + calc_gas(g_now, lpg_unit_price) + fixed_fee
pred_total = calc_elec(e_pred_usage) + calc_water(w_pred_usage) + calc_gas(g_pred_usage, lpg_unit_price) + fixed_fee

st.divider()

# 결과 대시보드
res1, res2 = st.columns(2)

with res1:
    st.metric(label="현재까지 합계", value=f"{curr_total:,.0f} 원")
    st.write(f"전기: {calc_elec(e_now):,}원")
    st.write(f"수도: {calc_water(w_now):,}원")
    st.write(f"가스: {calc_gas(g_now, lpg_unit_price):,}원")

with res2:
    st.metric(label="월말 최종 예상", value=f"{pred_total:,.0f} 원", delta=f"{pred_total - curr_total:,.0f} 원 추가 예정")
    st.caption(f"현재 추세로 남은 {total_days-today}일을 보낼 경우의 예측치입니다.")

# 그래프 (선택 사항)
st.bar_chart({"현재": curr_total, "예상": pred_total})