import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ====== 데이터 로드 ======
df = pd.read_excel("group_anova_with_effect_0331_STR_v2.xlsx", sheet_name="org_edit")
df2 = pd.read_excel("group_anova_with_effect_0331_STR_v2.xlsx", sheet_name="demo")

# ====== 카테고리 매핑 ======
category_mapping = {
    1: "Demo+Clinical",
    2: "Spatio-temporal",
    3: "Kinematics",
    4: "Tele-signal",
    5: "Motor-identity",
    6: "Frequency",
    7: "TUG"
}
df["Category"] = df["Category"].map(category_mapping)


categories = df["Category"].unique().tolist()

# ===============================
# 필터링 조건
anova_threshold = 0.05
kruskal_threshold = 0.05
eta_cutoff = 0.139
top_n = 15
pair_keys = ["HC_RBD", "HC_MildPD", "HC_ModPD", "MildPD_RBD", "ModPD_RBD", "MildPD_ModPD"]
group_names = ["HC", "RBD", "MildPD", "ModPD"]
colors = ["#4E79A7", "#F28E2B", "#E15759", "#76B7B2"]
significance_colors = ["red", "blue", "green", "purple", "orange", "brown"]

filtered_df_all = df[
    (df["P-Value"] < anova_threshold) &
    (df["Kruskal P"] < kruskal_threshold) &
    (df["Eta-Squared"] >= eta_cutoff)
]

df_top = filtered_df_all.sort_values(["Category", "Eta-Squared"], ascending=[True, False]) \
    .groupby("Category").head(top_n)

# ===============================
# Streamlit 레이아웃
st.set_page_config(layout="wide")
st.title("📊 Feature Comparison by Category")

# Sidebar 메뉴
tabs = ["Overview", "Subject Characteristics"] + categories + [p.replace("_", " vs ") for p in pair_keys]
selected_tab = st.sidebar.radio("탭 선택", tabs)

# ===============================
# Overview 탭
# Overview 탭 수정
if selected_tab == "Overview":
    st.markdown("## 🧾 분석 기준 안내")
    st.info("""
    - 그래프는 평균 ± 표준편차(Mean ± SD)로 표시하였습니다.
    - 그룹 간 유의한 차이는 별표(*)로 표시되어 있습니다. 
    - 유의미한 그룹 구분 기준:
        - ANOVA p < 0.05
        - Kruskal-Wallis p < 0.05
        - Eta-Squared ≥ 0.139
    - 그래프 스케일이 안맞을 경우 더블클릭하면 자동으로 오토스케일이 맞춰집니다. 
    """, icon="ℹ️")

    st.markdown("## 📂 Category 설명")
    st.markdown("""
    #### **1. Spatio-temporal & Kinematics**
        A. Spatio-temporal 
            - 보행 분석에서 사용하고 있는 시공간계수 대표 파라미터
            - gait event에 따라 생성되는 시간, 길이, 구간 변수들의 평균값과 표준편차, 변동계수 등
            - 논문에서 사용되는 기본적 파라미터 외에 정밀 분석을 통해 추가 변수 계산
        B. Kinematics : 
            - 보행 분석에서 사용하고 있는 운동학 대표 파라미터
            - gait event에 따라 생성되는 구간 사이의 발목에서 일어나는 각도 변화 변동계수, 일치도 등 계산

    #### **2. Tele-signal**
        - 통신 신호 분석 방법을 지면반력(Stance)과 다리의 Swing구간 분석에 적용하여 대상자 움직임의 심혈관 특성 
        - 개별 신호처리 방법으로 생성된 지수들의 특성을 무게중심 변동 패턴으로 변환하여 근육펌프 효율을 계산 
        - 역진자 모델링으로 구성된 순간속도(Instantaneous)로 계산된 무게중심 변동특성으로 산출 

    #### **3. Motor identity**
        - 대상자 고유의 움직임 특성을 모델링하여 IMU 센서 신호간의 교차상관 관계 분석, 
            각 신호 간 교차상관성을 통해 대상자가 가지는 고유의 움직임 특성을 추출 
        - 머리-골반-발관절의 균형 및 상호작용(직교성 동기화)을 반영 : 
            전정척수 반사의 최종말단(발)에서 신체균형 유지 정보를 취득하여 머리 움직임의 상호작용으로 연결

    #### **4. Frequency**
        - 피드포워드와 피드백 제어시스템 가정에서 대상자 동작의 주파수를 분석하여 움직임의 
            주기성을 평가, 움직임 조화를 평가하는 생성변수 
        - 인간의 모션은 일정한 패턴이 있는 경우에는 낮은 주기성을 가지고 패턴이 복잡하면 높은 주기성을 가짐
        - 직립이족보행에서 피드포워드 제어와 피드백 제어중 Dominant한 제어를 가지는 특징에 따라 
            1st, 2nd Frequency와 주파수 특성치가 다르게 나타남

    #### **5. TUG**
        A. S (Distance from start to turning onset (m))
            - 3m의 타겟을 걸을때 일어난 직후 부터 회전까지의 거리
            - 환자들은 회전을 시작하는 거리가 김, 타겟 근처에서 회전을 시작, 건강인은 빠르게 회전을 시작
        B. ETR (Effective Turning Radius (m))
            - 회전 구간에서 발생하는 총 회전 반경, 환자들은 회전 반경이 큼
        C. EMA (Effective Movement Area (m^2))
            - 회전 구간에서 발생하는 총 회전 면적, 환자들은 회전 총 면적이 넓음
        D. FN (Froude Number)
            - 프루드 수, 이 프로토콜에서는 대상자의 회전 능력을 판별하는 무차원 계수
            - 값이 높을수록 빠른 속도의 보행, 힘찬 보행으로 판단, 환자들은 수치가 낮음
    """)

# ===============================
# Subject Characteristics 탭
elif selected_tab == "Subject Characteristics":
    st.subheader("📋 Subject Characteristics")
    st.dataframe(df2, use_container_width=True)




elif selected_tab in categories:
    st.header(f"📁 Category: {selected_tab}")
    cat_df = df_top[df_top["Category"] == selected_tab]

    for _, row in cat_df.iterrows():
        feature = row["변수명"]
        means = [row[f"{g}_mean"] for g in group_names]
        stds = [row[f"{g}_std"] for g in group_names]

        significance = { 
            "HC_RBD": row["HC_RBD"], "HC_MildPD": row["HC_MildPD"], "HC_ModPD": row["HC_ModPD"],
            "MildPD_RBD": row["MildPD_RBD"], "ModPD_RBD": row["ModPD_RBD"], "MildPD_ModPD": row["MildPD_ModPD"]
        }
        significant_pairs = [key for key, value in significance.items() if value == 1]

        fig = go.Figure()
        for i, group in enumerate(group_names):
            fig.add_trace(go.Bar(
                x=[group],
                y=[means[i]],
                name=group,
                marker_color=colors[i],
                error_y=dict(type='data', array=[stds[i]], visible=True)
            ))

        y_min = min([m - s for m, s in zip(means, stds)])
        y_max = max([m + s for m, s in zip(means, stds)])

        if y_max > 0 and y_min >= 0:
            base_y = y_max + abs(y_max - y_min) * 0.05
            y_offset = abs(y_max - y_min) * 0.03
        elif y_max <= 0 and y_min < 0:
            base_y = y_min - abs(y_max - y_min) * 0.05
            y_offset = abs(y_max - y_min) * 0.03
        else:
            base_y = y_max + abs(y_max - y_min) * 0.05
            y_offset = abs(y_max - y_min) * 0.03

        for i, pair in enumerate(significant_pairs):
            g1, g2 = pair.split("_")
            idx1, idx2 = group_names.index(g1), group_names.index(g2)
            y_line = base_y + i * y_offset if y_max > 0 else base_y - i * y_offset

            fig.add_trace(go.Scatter(
                x=[g1, g2],
                y=[y_line, y_line],
                mode='lines+text',
                text=['*'],
                textposition='top center',
                line=dict(color=significance_colors[i % len(significance_colors)], width=2),
                showlegend=True,
                name=pair
            ))

        fig.update_layout(
            title=f"{feature} (Mean ± SD)",
            xaxis_title="Group",
            yaxis_title="Mean Value",
            barmode='group',
            template='plotly_white',
            yaxis=dict(range=[
                y_min - len(significant_pairs) * y_offset,
                base_y + len(significant_pairs) * y_offset
            ])
        )

        st.plotly_chart(fig, use_container_width=True)

        stat_table = pd.DataFrame({
            "Comparison": list(significance.keys()),
            "Significant": ["Yes" if significance[p] == 1 else "No" for p in significance],
            "ANOVA P": [f"{row['P-Value']:.4f}"] * len(significance),
            "Kruskal P": [f"{row['Kruskal P']:.4f}"] * len(significance),
            "Eta-Squared": [f"{row['Eta-Squared']:.4f}"] * len(significance),
        })
        st.dataframe(stat_table, use_container_width=True)





# ===============================
# Group Comparison 탭
else:
    selected_pair = selected_tab.replace(" vs ", "_")
    st.header(f"🔍 Group Comparison: {selected_tab}")
    filtered_df_pairs = df_top[df_top["Category"] != "Demo+Clinical"]
    pair_df = filtered_df_pairs[filtered_df_pairs[selected_pair] == 1]
    top10_df = pair_df.sort_values("Eta-Squared", ascending=False).groupby("Category").head(20)

    for _, row in top10_df.iterrows():
        feature = row["변수명"]
        g1, g2 = selected_pair.split("_")
        means = [row[f"{g}_mean"] for g in [g1, g2]]
        stds = [row[f"{g}_std"] for g in [g1, g2]]

        fig = go.Figure()
        for i, g in enumerate([g1, g2]):
            fig.add_trace(go.Bar(
                x=[g],
                y=[means[i]],
                name=g,
                marker_color=colors[group_names.index(g)],
                error_y=dict(type='data', array=[stds[i]], visible=True)
            ))

        fig.update_layout(
            title=f"{feature} (Mean ± SD)",
            barmode="group",
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
