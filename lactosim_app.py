import math
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="LactoSim", page_icon="🥛", layout="wide")

MW_LACTOSE = 342.30
MW_GLUCOSE = 180.16
MW_GALACTOSE = 180.16

st.markdown("""
<style>
.main .block-container{padding-top:2rem;max-width:1150px}.hero{padding:28px 32px;border-radius:28px;background:linear-gradient(135deg,#eef6ff,#fff7e8);border:1px solid #dbeafe;margin-bottom:18px}.hero h1{margin:0;font-size:2.5rem;color:#1f2a44}.hero p{color:#516070;font-size:1.05rem}.card{padding:18px;border-radius:22px;border:1px solid #e5e7eb;background:white;box-shadow:0 8px 24px rgba(15,23,42,.06);min-height:115px}.card-title{font-size:.95rem;color:#64748b;margin-bottom:8px}.card-value{font-size:1.65rem;font-weight:800;color:#1f2a44}.note{padding:14px 18px;border-radius:18px;background:#f8fafc;border:1px solid #e2e8f0;color:#334155}.diagram{padding:24px;border-radius:24px;background:#f8fbff;border:1px solid #dbeafe;margin-bottom:16px}.flow{display:flex;gap:14px;align-items:center;justify-content:space-between;flex-wrap:wrap}.box{padding:18px 20px;border-radius:18px;background:white;border:2px solid #bfdbfe;text-align:center;min-width:145px}.arrow{font-size:2rem;color:#334155}.molecule{display:flex;align-items:center;justify-content:center;gap:12px;flex-wrap:wrap;font-size:1.05rem}.pill{padding:18px 22px;border-radius:20px;background:white;border:2px solid #bfdbfe;font-weight:700;color:#1f2a44}.enzyme{border-color:#f2c46d;background:#fff7e8}.product1{border-color:#86efac;background:#f0fdf4}.product2{border-color:#f9a8d4;background:#fdf2f8}.tempbar{height:160px;position:relative;margin:20px 4px;background:linear-gradient(90deg,#dbeafe,#dcfce7,#fef3c7,#fee2e2);border-radius:18px;border:1px solid #e2e8f0}.curve{position:absolute;left:8%;right:8%;top:20%;height:70%;border-top:8px solid #4e89d8;border-radius:50% 50% 0 0}.opt{position:absolute;left:48%;top:10%;bottom:12%;border-left:4px dashed #e4a84f}.opt-label{position:absolute;left:40%;top:3%;font-weight:800;color:#1f2a44}.small{color:#64748b;font-size:.9rem}
</style>
""", unsafe_allow_html=True)

def temperature_factor(temp_c, optimal_temp_c, sigma):
    return math.exp(-((temp_c - optimal_temp_c) ** 2) / (2 * sigma ** 2))

def simulate(initial_lactose_g, total_time_min, enzyme_factor, temperature_c, k_ref, optimal_temp_c, sigma, points=151):
    tf = temperature_factor(temperature_c, optimal_temp_c, sigma)
    k_eff = k_ref * enzyme_factor * tf
    times = np.linspace(0, total_time_min, points)
    lactose_remaining = initial_lactose_g * np.exp(-k_eff * times)
    lactose_decomposed = initial_lactose_g - lactose_remaining
    decomposed_mol = lactose_decomposed / MW_LACTOSE
    glucose = decomposed_mol * MW_GLUCOSE
    galactose = decomposed_mol * MW_GALACTOSE
    hydrolysis = lactose_decomposed / initial_lactose_g * 100
    return pd.DataFrame({
        "시간(min)": times,
        "유당 잔존량(g)": lactose_remaining,
        "분해된 유당량(g)": lactose_decomposed,
        "포도당 생성량(g)": glucose,
        "갈락토스 생성량(g)": galactose,
        "유당분해율(%)": hydrolysis,
        "온도 보정 계수": tf,
        "최종 반응속도상수 k_eff": k_eff,
    })

def card(title, value, unit=""):
    st.markdown(f'<div class="card"><div class="card-title">{title}</div><div class="card-value">{value}{unit}</div></div>', unsafe_allow_html=True)

left, right = st.columns([1.4, 1])
with left:
    st.markdown('<div class="hero"><h1>🥛 LactoSim</h1><p>락타아제 처리 조건에 따른 유당 잔존량, 생성당, 유당분해율을 예측하는 탐구용 웹앱</p></div>', unsafe_allow_html=True)
with right:
    st.markdown('''<div class="diagram"><div class="molecule"><span class="pill">유당</span><span class="arrow">→</span><span class="pill enzyme">락타아제</span><span class="arrow">→</span><span class="pill product1">포도당</span><span>+</span><span class="pill product2">갈락토스</span></div></div>''', unsafe_allow_html=True)

with st.sidebar:
    st.header("시뮬레이션 조건")
    initial_lactose_g = st.number_input("초기 유당량(g)", min_value=0.1, max_value=100.0, value=5.0, step=0.1)
    total_time_min = st.slider("처리 시간(min)", 0, 360, 120, 10)
    enzyme_factor = st.slider("효소량 배수", 0.1, 5.0, 1.0, 0.1)
    temperature_c = st.slider("처리 온도(℃)", 0, 80, 37, 1)
    st.divider()
    st.subheader("모델 설정")
    k_ref = st.slider("기준 반응속도상수 k_ref", 0.001, 0.100, 0.015, 0.001, format="%.3f")
    optimal_temp_c = st.slider("최적 온도 T_opt(℃)", 20, 70, 37, 1)
    sigma = st.slider("온도 민감도 σ", 5, 30, 12, 1)

df = simulate(initial_lactose_g, total_time_min, enzyme_factor, temperature_c, k_ref, optimal_temp_c, sigma)
final = df.iloc[-1]

st.subheader("최종 예측 결과")
c1,c2,c3,c4 = st.columns(4)
with c1: card("유당 잔존량", f"{final['유당 잔존량(g)']:.2f}", " g")
with c2: card("포도당 생성량", f"{final['포도당 생성량(g)']:.2f}", " g")
with c3: card("갈락토스 생성량", f"{final['갈락토스 생성량(g)']:.2f}", " g")
with c4: card("유당분해율", f"{final['유당분해율(%)']:.1f}", " %")

st.markdown(f'<div class="note">현재 조건에서 온도 보정 계수는 <b>{final["온도 보정 계수"]:.3f}</b>, 최종 반응속도상수 k_eff는 <b>{final["최종 반응속도상수 k_eff"]:.4f}</b>입니다.</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["원리 그림", "그래프", "조건 비교", "데이터", "보고서 설명"])

with tab1:
    st.markdown('''<div class="diagram"><h3>락타아제에 의한 유당 분해 원리</h3><div class="molecule"><span class="pill">유당<br><span class="small">Lactose</span></span><span class="arrow">→</span><span class="pill enzyme">락타아제<br><span class="small">Lactase</span></span><span class="arrow">→</span><span class="pill product1">포도당<br><span class="small">Glucose</span></span><span>+</span><span class="pill product2">갈락토스<br><span class="small">Galactose</span></span></div></div>''', unsafe_allow_html=True)
    st.markdown('''<div class="diagram"><h3>시뮬레이션 계산 흐름</h3><div class="flow"><div class="box"><b>입력 조건</b><br><span class="small">유당·시간·온도·효소량</span></div><div class="arrow">→</div><div class="box"><b>반응속도 계산</b><br><span class="small">k_eff 보정</span></div><div class="arrow">→</div><div class="box"><b>물질량 예측</b><br><span class="small">잔존량·생성량</span></div><div class="arrow">→</div><div class="box"><b>그래프 출력</b><br><span class="small">분해율 변화</span></div></div></div>''', unsafe_allow_html=True)
    st.markdown('''<div class="diagram"><h3>온도와 효소 활성의 관계</h3><div class="tempbar"><div class="curve"></div><div class="opt"></div><div class="opt-label">최적 온도 근처</div></div><p class="small">온도가 최적 온도에 가까울수록 반응속도는 커지고, 너무 낮거나 높으면 감소한다고 단순화하였다.</p></div>''', unsafe_allow_html=True)

with tab2:
    st.subheader("시간에 따른 물질량 변화")
    st.line_chart(df.set_index("시간(min)")[["유당 잔존량(g)", "포도당 생성량(g)", "갈락토스 생성량(g)"]])
    st.subheader("시간에 따른 유당분해율 변화")
    st.line_chart(df.set_index("시간(min)")[["유당분해율(%)"]])

with tab3:
    st.subheader("조건 비교")
    mode = st.radio("비교 기준", ["온도 비교", "효소량 비교"], horizontal=True)
    if mode == "온도 비교":
        temps = st.multiselect("비교할 온도(℃)", [10,20,30,37,45,55,65], default=[20,37,55])
        comp = pd.DataFrame({"시간(min)": np.linspace(0, total_time_min, 151)})
        for temp in temps:
            comp[f"{temp}℃"] = simulate(initial_lactose_g,total_time_min,enzyme_factor,temp,k_ref,optimal_temp_c,sigma)["유당분해율(%)"]
        st.line_chart(comp.set_index("시간(min)"))
    else:
        enzs = st.multiselect("비교할 효소량 배수", [0.5,1.0,1.5,2.0,3.0,5.0], default=[0.5,1.0,2.0])
        comp = pd.DataFrame({"시간(min)": np.linspace(0, total_time_min, 151)})
        for enz in enzs:
            comp[f"{enz}배"] = simulate(initial_lactose_g,total_time_min,enz,temperature_c,k_ref,optimal_temp_c,sigma)["유당분해율(%)"]
        st.line_chart(comp.set_index("시간(min)"))

with tab4:
    st.subheader("계산 데이터")
    st.dataframe(df, use_container_width=True)
    st.download_button("CSV 다운로드", data=df.to_csv(index=False).encode("utf-8-sig"), file_name="lactosim_result.csv", mime="text/csv")

with tab5:
    st.subheader("보고서에 넣을 수 있는 설명")
    st.markdown('''
본 후속활동에서는 락타아제 처리 조건에 따른 유당분해율 변화를 예측하기 위해 웹앱 형태의 시뮬레이션 프로그램을 제작하였다. 프로그램은 초기 유당량, 처리 시간, 효소량, 온도 조건을 입력하면 유당 잔존량, 포도당 생성량, 갈락토스 생성량, 유당분해율을 자동으로 계산하고 그래프로 시각화하도록 설계하였다.

계산 모델은 유당 잔존량이 시간에 따라 지수적으로 감소한다고 가정하였다. 효소량은 반응속도상수에 비례적으로 반영하였고, 온도는 최적 온도에서 멀어질수록 효소 활성이 감소하는 방식으로 보정하였다. 이를 통해 락타아제의 효소 작용을 개념적으로 이해하는 수준을 넘어, 유당 저감 식품 제조 과정에서 처리 시간, 효소량, 온도 조건을 조절하는 공정 설계의 관점으로 확장하였다.

다만 본 모델은 pH 변화, 생성물 저해, 효소의 열변성, 우유 속 단백질과 지방의 영향 등을 반영하지 않은 단순화된 예측 모델이다. 따라서 실제 식품 공정에 적용하려면 실험값을 바탕으로 반응속도상수와 온도 보정식을 보정하는 과정이 필요하다.
''')
    st.latex(r"L(t) = L_0 e^{-k_{eff}t}")
    st.latex(r"k_{eff} = k_{ref} \times E_{factor} \times T_{factor}")
    st.latex(r"T_{factor} = e^{-\frac{(T - T_{opt})^2}{2\sigma^2}}")

st.caption("탐구용 단순 예측 모델입니다. 실제 제조 조건 결정에는 실험값 기반 보정이 필요합니다.")
