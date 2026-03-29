import streamlit as st
import math
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="우리 집 관리비 예측기", layout="wide")

# --- 1. 계산 로직 함수들 ---

# 전기 요금 계산기 (고압/저압 선택 가능)
def calc_elec(usage, elec_type):
    if usage <= 0: return 0
    
    # 타입별 단가 설정
    if elec_type == "주택용 고압(아파트)":
        base = 730
        unit = 105.0
    else: # 주택용 저압(빌라/주택)
        base = 910
        unit = 120.0
        
    climate = 9.0       # 기후환경
    fuel = 5.0          # 연료비조정
    common = 1890       # 질문자님 댁 공동전기료
    support = 1350      # 발전소지원금
    
    # 세전 합계
    subtotal = base + (usage * (unit + climate + fuel))
    # 부가세(10%) 및 전력기금(3.7%)
    vat = round(subtotal * 0.1)
    fund = math.floor((subtotal * 0.037) / 10) * 10
    
    return int(subtotal + vat + fund + common - support)

# 수도 요금 계산기 (톤당 990원)
def calc_water(usage):
    if usage <= 0: return 490 # 기본 공동수도료만 반환
    return int((usage * 990) + 490)

# 가스 요금 계산기 (LPG/LNG 선택 가능)
def calc_gas(usage, gas_type, lpg_price=0):
    if usage <= 0: return 0
    
    if gas_type == "LPG":
        base_fee = 2000
        supply_price = (usage * lpg_price) + base_fee
    else: # LNG(도시가스)
        heating_value = 42.5  # 평균 열량 계수
        mj_price = 22.1       # MJ당 단가
        base_fee = 1000
        meter_fee = 200
        supply_price = (usage * heating_value * mj_price) + base_fee + meter_fee
        
    vat = supply_price * 0.1
    return int(supply_price + vat)

# --- 2. 웹 화면 구성 (사이드바 설정) ---

st.title("🏠 우리 집 관리비 실시간 예측 대시보드")

st.sidebar.header("⚙️ 기본 설정")
today = st.sidebar.number_input("오늘이 이번 달의 며칠째인가요? (1~31)", min_value=0, max_value=31, value=0)
total_days = st.sidebar.number_input("이번 달 총 일수", min_value=28, max_value=31, value=30)

st.sidebar.subheader("🔌 전기 설정")
elec_choice = st.sidebar.radio("전기 계약 종류", ["주택용 고압(아파트)", "주택용 저압(빌라/주택)"])

st.sidebar.subheader("🔥 가스 설정")
gas_choice = st.sidebar.radio("가스 종류", ["LPG", "LNG(도시가스)"])
lpg_unit_price = 0
if gas_choice == "LPG":
    lpg_unit_price = st.sidebar.number_input("LPG 단가 (1m³당)", value=0)

st.sidebar.subheader("🏢 기타 설정")
fixed_fee = st.sidebar.number_input("기타 고정 공용관리비 (청소 등)", value=0)

# --- 3. 메인 화면: 사용량 입력부 ---

st.info("💡 오늘 확인한 계량기 사용량을 입력하세요. (현재 지침 - 전월 지침)")
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("⚡ 전기 (kWh)")
    e_now = st.number_input("현재까지 전기 사용량", value=0.0)
    
with col2:
    st.subheader("💧 수도 (톤)")
    w_now = st.number_input("현재까지 수도 사용량", value=0.0)

with col3:
    st.subheader(f"🔥 가스 ({gas_choice}/m³)")
    g_now = st.number_input(f"현재까지 {gas_choice} 사용량", value=0.0)

# --- 4. 요금 계산 및 예측 ---

# 예측 사용량 계산 (날짜가 0보다 클 때만)
if today > 0:
    e_pred_usage = (e_now / today) * total_days
    w_pred_usage = (w_now / today) * total_days
    g_pred_usage = (g_now / today) * total_days
else:
    e_pred_usage = w_pred_usage = g_pred_usage = 0

# 개별 요금 계산
c_elec = calc_elec(e_now, elec_choice)
p_elec = calc_elec(e_pred_usage, elec_choice)

c_water = calc_water(w_now)
p_water = calc_water(w_pred_usage)

c_gas = calc_gas(g_now, gas_choice, lpg_unit_price)
p_gas = calc_gas(g_pred_usage, gas_choice, lpg_unit_price)

# 전체 합계
curr_total = c_elec + c_water + c_gas + fixed_fee
pred_total = p_elec + p_water + p_gas + fixed_fee

st.divider()

# --- 5. 결과 대시보드 (왼쪽: 현재, 오른쪽: 예상) ---

res_col1, res_col2 = st.columns(2)

with res_col1:
    st.header("💵 현재까지 발생 요금")
    st.metric(label="현재 합계", value=f"{curr_total:,.0f} 원")
    st.write(f"⚡ 전기({elec_choice}): {c_elec:,}원")
    st.write(f"💧 수도: {c_water:,}원")
    st.write(f"🔥 가스({gas_choice}): {c_gas:,}원")
    st.caption(f"오늘({today}일)까지 실제 사용량 기준 요금입니다.")

with res_col2:
    st.header("🔮 월말 최종 예상 요금")
    st.metric(label="예상 합계", value=f"{pred_total:,.0f} 원", 
              delta=f"{pred_total - curr_total:,.0f} 원 추가 예정", delta_color="inverse")
    st.write(f"⚡ 전기 예상: {p_elec:,}원")
    st.write(f"💧 수도 예상: {p_water:,}원")
    st.write(f"🔥 가스 예상: {p_gas:,}원")
    st.caption(f"현재 추세로 {total_days}일을 채울 경우의 예측치입니다.")

# --- 6. 그래프 시각화 (현재가 왼쪽, 예상이 오른쪽 고정) ---

st.subheader("📊 요금 비교 그래프")

chart_df = pd.DataFrame({
    "구분": ["1. 현재까지 발생 요금", "2. 월말 예상 요금"],
    "금액(원)": [curr_total, pred_total]
})

st.bar_chart(data=chart_df, x="구분", y="금액(원)", color="#3498db")

st.success("설정값을 변경하면 실시간으로 분석 결과가 업데이트됩니다.")
