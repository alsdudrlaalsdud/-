import streamlit as st
import math

# 페이지 설정
st.set_page_config(page_title="우리 집 관리비 예측기", layout="wide")

# --- 1. 계산 로직 함수들 ---

# 전기 요금 (주택용 고압 기준)
def calc_elec(usage):
    if usage <= 0: return 0
    base = 730          # 기본료
    unit = 105.0        # 전력량 단가
    climate = 9.0       # 기후환경
    fuel = 5.0          # 연료비조정
    common = 1890       # 공동전기료
    support = 1350      # 발전소지원금
    
    # 세전 합계
    subtotal = base + (usage * (unit + climate + fuel))
    # 부가세(10%) 및 전력기금(3.7%)
    vat = round(subtotal * 0.1)
    fund = math.floor((subtotal * 0.037) / 10) * 10
    
    return int(subtotal + vat + fund + common - support)

# 수도 요금 (톤당 990원)
def calc_water(usage):
    if usage <= 0: return 490 # 기본 공동수도료만 반환
    return int((usage * 990) + 490)

# 가스 요금 (LPG 개별난방)
def calc_lpg(usage, price):
    if usage <= 0: return 0
    base_fee = 2000     # LPG 기본료 추정치
    supply_price = (usage * price) + base_fee
    vat = supply_price * 0.1
    return int(supply_price + vat)

# --- 2. 웹 화면 구성 ---

st.title("🏠 우리 집 관리비 실시간 예측 대시보드")
st.markdown("모든 입력값을 기입하면 이번 달 최종 요금을 예측합니다.")

# 사이드바: 설정값 (초기값 모두 0)
st.sidebar.header("⚙️ 기본 설정")
today = st.sidebar.number_input("오늘이 이번 달의 며칠째인가요? (1~31)", min_value=0, max_value=31, value=0)
total_days = st.sidebar.number_input("이번 달 총 일수", min_value=28, max_value=31, value=30)
lpg_price = st.sidebar.number_input("LPG 단가 (1m³당)", value=0)
fixed_fee = st.sidebar.number_input("기타 고정 공용관리비 (청소 등)", value=0)

# 메인 화면: 계량기 사용량 입력부
st.info("💡 오늘 확인한 계량기 사용량을 입력하세요. (현재 지침 - 전월 지침)")
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("⚡ 전기 (kWh)")
    e_now = st.number_input("현재까지 사용량", key="elec", value=0.0)
    
with col2:
    st.subheader("💧 수도 (톤)")
    w_now = st.number_input("현재까지 사용량", key="water", value=0.0)

with col3:
    st.subheader("🔥 가스 (LPG/m³)")
    g_now = st.number_input("현재까지 사용량", key="gas", value=0.0)

# --- 3. 요금 계산 및 예측 ---

# 오늘 날짜가 0일 경우 에러 방지
if today > 0:
    e_pred_usage = (e_now / today) * total_days
    w_pred_usage = (w_now / today) * total_days
    g_pred_usage = (g_now / today) * total_days
else:
    e_pred_usage = w_pred_usage = g_pred_usage = 0

# 요금 계산
c_elec = calc_elec(e_now)
p_elec = calc_elec(e_pred_usage)

c_water = calc_water(w_now)
p_water = calc_water(w_pred_usage)

c_gas = calc_lpg(g_now, lpg_price)
p_gas = calc_lpg(g_pred_usage, lpg_price)

# 최종 합계
curr_total = c_elec + c_water + c_gas + fixed_fee
pred_total = p_elec + p_water + p_gas + fixed_fee

st.divider()

# --- 4. 결과 대시보드 (왼쪽: 현재 발생 요금, 오른쪽: 월말 예상 요금) ---

res1, res2 = st.columns(2)

with res1:
    st.header("💵 현재까지 발생 요금")
    st.metric(label="현재 합계", value=f"{curr_total:,.0f} 원")
    st.write(f"⚡ 전기 현재: {c_elec:,}원")
    st.write(f"💧 수도 현재: {c_water:,}원")
    st.write(f"🔥 가스 현재: {c_gas:,}원")
    st.caption(f"오늘({today}일)까지 실제 사용량 기준 요금입니다.")

with res2:
    st.header("🔮 월말 최종 예상 요금")
    # delta를 통해 현재보다 얼마나 더 나올지 표시
    st.metric(label="예상 합계", value=f"{pred_total:,.0f} 원", delta=f"{pred_total - curr_total:,.0f} 원 추가 예정", delta_color="inverse")
    st.write(f"⚡ 전기 예상: {p_elec:,}원")
    st.write(f"💧 수도 예상: {p_water:,}원")
    st.write(f"🔥 가스 예상: {p_gas:,}원")
    st.caption(f"현재 추세로 {total_days}일을 채울 경우의 예측치입니다.")

# --- 5. 그래프 시각화 (왼쪽: 현재, 오른쪽: 예상) ---

st.subheader("📊 요금 비교 그래프")
# 데이터 생성 (현재가 첫 번째로 오도록)
chart_data = {
    "구분": ["현재까지 발생 요금", "월말 예상 요금"],
    "금액(원)": [curr_total, pred_total]
}
st.bar_chart(data=chart_data, x="구분", y="금액(원)", color="#3498db")

st.success("데이터를 입력하면 실시간으로 분석 결과가 업데이트됩니다.")
