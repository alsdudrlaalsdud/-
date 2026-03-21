import streamlit as st
import math

# 페이지 설정
st.set_page_config(page_title="우리 집 관리비 예측기", layout="wide")

# --- 계산 로직 함수들 ---

# 전기 요금 계산기 (저압/고압 선택 가능)
def calc_elec(usage, type="고압"):
    if type == "저압":
        base = 910
        unit = 120.0
    else: # 고압
        base = 730
        unit = 105.0
        
    climate = 9.0
    fuel = 5.0
    common = 1890    # 질문자님 댁 공동전기료
    support = 1350   # 발전소지원금
    
    # 세전 금액
    subtotal = base + (usage * unit) + (usage * climate) + (usage * fuel)
    
    # 세금 및 기금 (부가세 10%, 전력기금 3.7%)
    vat = round(subtotal * 0.1)
    fund = math.floor((subtotal * 0.037) / 10) * 10
    
    return int(subtotal + vat + fund + common - support)

# 수도 요금 계산기
def calc_water(usage):
    return int((usage * 990) + 490)

# LPG 가스 계산기
def calc_lpg(usage, price):
    base_fee = 2000
    supply_price = (usage * price) + base_fee
    vat = supply_price * 0.1
    return int(supply_price + vat)

# LNG(도시가스) 가스 계산기
def calc_lng(usage):
    heating_value = 42.5
    mj_price = 22.1
    base_fee = 1000
    meter_fee = 200
    mj_usage = usage * heating_value
    supply_price = (mj_usage * mj_price) + base_fee + meter_fee
    vat = supply_price * 0.1
    return int(supply_price + vat)

# --- 웹 화면 구성 ---
st.title("🏠 우리 집 관리비 실시간 예측 대시보드")

# 사이드바: 설정값
st.sidebar.header("⚙️ 기본 설정")
today = st.sidebar.slider("오늘이 이번 달의 며칠째인가요?", 1, 31, 15)

st.sidebar.subheader("🔌 전기 설정")
elec_type = st.sidebar.radio("전기 계약 종류", ["주택용 고압(아파트)", "주택용 저압(빌라/주택)"])

st.sidebar.subheader("🔥 가스 설정")
gas_type = st.sidebar.radio("가스 종류", ["LPG", "LNG(도시가스)"])
if gas_type == "LPG":
    lpg_price = st.sidebar.number_input("LPG 단가 (1m³당)", value=4200)

st.sidebar.subheader("🏢 기타 설정")
fixed_fee = st.sidebar.number_input("고정 공용관리비 (청소 등)", value=50000)

# 메인 화면: 입력부
st.info(f"오늘({today}일)까지 사용한 계량기 지침을 입력하세요.")
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("⚡ 전기 (kWh)")
    e_now = st.number_input("현재 사용량 입력", key="elec", value=41.0)
    e_pred = (e_now / today) * 30
    
with col2:
    st.subheader("💧 수도 (톤)")
    w_now = st.number_input("현재 사용량 입력", key="water", value=2.0)
    w_pred = (w_now / today) * 30

with col3:
    st.subheader(f"🔥 가스 ({gas_type})")
    g_now = st.number_input(f"현재 가스 사용량 입력", key="gas", value=5.0)
    g_pred = (g_now / today) * 30

# 요금 계산
e_type_val = "저압" if "저압" in elec_type else "고압"
c_elec = calc_elec(e_now, e_type_val)
p_elec = calc_elec(e_pred, e_type_val)

c_water = calc_water(w_now)
p_water = calc_water(w_pred)

if gas_type == "LPG":
    c_gas = calc_lpg(g_now, lpg_price)
    p_gas = calc_lpg(g_pred, lpg_price)
else:
    c_gas = calc_lng(g_now)
    p_gas = calc_lng(g_pred)

# 최종 합계
curr_total = c_elec + c_water + c_gas + fixed_fee
pred_total = p_elec + p_water + p_gas + fixed_fee

st.divider()

# 결과 표시
res1, res2 = st.columns(2)
with res1:
    st.metric(label="현재까지 발생 요금", value=f"{curr_total:,.0f} 원")
    st.write(f"⚡ 전기({e_type_val}): {c_elec:,}원")
    st.write(f"💧 수도: {c_water:,}원")
    st.write(f"🔥 가스: {c_gas:,}원")

with res2:
    st.metric(label="월말 최종 예상 요금", value=f"{pred_total:,.0f} 원", delta=f"{pred_total - curr_total:,.0f} 원 추가 예정")
    st.caption(f"남은 일수 동안 현재와 동일한 패턴으로 사용할 경우의 예측치입니다.")

# 시각화
st.bar_chart({"현재 합계": curr_total, "월말 예상": pred_total})
