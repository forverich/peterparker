import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Nobel Prize Dashboard",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Dark theme CSS ──────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0F0F1E; }
    .block-container { padding-top: 1.5rem; }
    .stMetric { background: #141828; border: 1px solid #1e2545; border-radius: 10px; padding: 0.8rem; }
    h1, h2, h3 { color: #F5C842 !important; }
    .stTabs [data-baseweb="tab"] { color: #6a6a9a; }
    .stTabs [aria-selected="true"] { color: #F5C842 !important; }
</style>
""", unsafe_allow_html=True)

# ── Color palettes ──────────────────────────────────────────
CAT_COLORS = {
    "Physics":    "#4A90D9",
    "Chemistry":  "#E8821A",
    "Medicine":   "#2ECC71",
    "Literature": "#9B59B6",
    "Peace":      "#E8527A",
    "Economics":  "#F1C40F",
}
COUNTRY_COLORS = {
    "Japan": "#4A90D9", "China": "#D94040", "India": "#E8821A",
    "Israel": "#1A5BBF", "South Korea": "#5B8FA8", "Pakistan": "#2E7D5E",
    "Iran": "#7B4FBF", "Turkey": "#C0784A", "Taiwan": "#E84393",
    "Bangladesh": "#3DAE6B", "Vietnam": "#D4A020", "Yemen": "#8B6A3E",
}
CONT_COLORS = {
    "Europe": "#3560C0", "North America": "#D44070", "Asia": "#E8821A",
    "South America": "#2ECC71", "Africa": "#F1C40F", "Oceania": "#9B59B6",
}

PLOT_BG   = "#0F0F1E"
PAPER_BG  = "#0F0F1E"
FONT_CLR  = "#F0EAD6"
GRID_CLR  = "#1E2545"

def base_layout(**kwargs):
    return dict(
        plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG,
        font=dict(color=FONT_CLR, family="Georgia"),
        xaxis=dict(gridcolor=GRID_CLR, zerolinecolor=GRID_CLR),
        yaxis=dict(gridcolor=GRID_CLR, zerolinecolor=GRID_CLR),
        margin=dict(l=60, r=30, t=50, b=50),
        **kwargs,
    )

# ── Data loading ────────────────────────────────────────────
@st.cache_data
def load_data(uploaded_file=None):
    """Load CSV; fall back to synthetic demo data."""
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        return df, False

    # Synthetic demo data matching SDnobel__1_.csv schema
    np.random.seed(42)
    n = 1000
    categories = ["Physics", "Chemistry", "Medicine", "Literature", "Peace", "Economics"]
    birth_countries = (
        ["United States of America"] * 350 +
        ["United Kingdom"] * 120 + ["Germany"] * 100 + ["France"] * 65 +
        ["Sweden"] * 30 + ["Russia"] * 28 + ["Switzerland"] * 25 +
        ["Japan"] * 25 + ["Netherlands"] * 20 + ["Canada"] * 20 +
        ["Italy"] * 18 + ["Austria"] * 18 + ["India"] * 10 +
        ["China"] * 8 + ["Israel"] * 15 + ["Denmark"] * 13 +
        ["Norway"] * 12 + ["Australia"] * 12 + ["Hungary"] * 10 +
        ["Poland"] * 9 + ["Belgium"] * 9 + ["South Africa"] * 6
    )

    COUNTRY_CONTINENT = {
        "United States of America": "North America", "Canada": "North America",
        "United Kingdom": "Europe", "Germany": "Europe", "France": "Europe",
        "Sweden": "Europe", "Russia": "Europe", "Switzerland": "Europe",
        "Netherlands": "Europe", "Italy": "Europe", "Austria": "Europe",
        "Denmark": "Europe", "Norway": "Europe", "Hungary": "Europe",
        "Poland": "Europe", "Belgium": "Europe",
        "Japan": "Asia", "China": "Asia", "India": "Asia", "Israel": "Asia",
        "Australia": "Oceania",
        "South Africa": "Africa",
    }

    countries_sample = np.random.choice(birth_countries, size=n)
    cats = np.random.choice(categories, size=n,
                            p=[0.22, 0.18, 0.22, 0.14, 0.14, 0.10])
    sexes = np.random.choice(["Male", "Female"], size=n, p=[0.94, 0.06])

    age_mu = {"Physics": 56, "Chemistry": 59, "Medicine": 57,
               "Literature": 65, "Peace": 62, "Economics": 67}
    ages = np.array([
        int(np.random.normal(age_mu[c], 10)) for c in cats
    ]).clip(25, 97)

    df = pd.DataFrame({
        "year":          np.random.randint(1901, 2024, n),
        "category":      cats,
        "birth_country": countries_sample,
        "sex":           sexes,
        "age":           ages,
        "laureate_type": np.random.choice(
            ["Individual", "Organization"], n, p=[0.95, 0.05]),
    })
    df["continent"] = df["birth_country"].map(COUNTRY_CONTINENT).fillna("Other")
    return df, True   # (dataframe, is_demo)


# ── Sidebar ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏆 Nobel Dashboard")
    st.markdown("---")

    uploaded = st.file_uploader(
        "Upload your CSV (SDnobel__1_.csv)",
        type=["csv"],
        help="Cột cần có: year, category, birth_country, sex, age, laureate_type",
    )

    df, is_demo = load_data(uploaded)

    if is_demo:
        st.info("📊 Demo data — upload CSV để dùng data thật", icon="ℹ️")

    st.markdown("### Filters")
    all_cats = sorted(df["category"].dropna().unique())
    sel_cats = st.multiselect("Category", all_cats, default=all_cats)

    year_min = int(df["year"].min())
    year_max = int(df["year"].max())
    yr_range = st.slider("Year range", year_min, year_max, (year_min, year_max))

    st.markdown("---")
    st.caption("Source: Nobel Prize Dataset · 1901–present")

# ── Filter ──────────────────────────────────────────────────
dff = df[
    df["category"].isin(sel_cats) &
    df["year"].between(yr_range[0], yr_range[1])
].copy()

# ── Header ──────────────────────────────────────────────────
st.markdown("# 🏆 NOBEL PRIZE DASHBOARD")
st.markdown(f"**Distribution by country, field, geography · {yr_range[0]}–{yr_range[1]}**")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Laureates",  len(dff))
col2.metric("Categories",       dff["category"].nunique())
col3.metric("Countries",        dff["birth_country"].nunique())
col4.metric("Avg Age",          f"{dff['age'].mean():.1f}" if "age" in dff else "—")

st.markdown("---")

# ── Tabs ────────────────────────────────────────────────────
tabs = st.tabs([
    "🗺 Treemap (Asia)",
    "🍩 Donut (Continent)",
    "📊 Bar (Peace)",
    "📦 Age Boxplot",
    "🍭 Lollipop",
    "🔥 Heatmap (Gender)",
    "🌍 World Map",
])

# ─────────────────────────────────────────────────────────────
# TAB 1 · TREEMAP (Asia)
# ─────────────────────────────────────────────────────────────
with tabs[0]:
    st.subheader("Nobel Prizes in Asia — by Country & Field")

    ASIAN_MAP = {
        "Japan": "Japan", "China": "China",
        "Tibet (People's Republic of China)": "China",
        "India": "India", "British India (India)": "India",
        "British India (Bangladesh)": "Bangladesh",
        "India (Pakistan)": "Pakistan", "Pakistan": "Pakistan",
        "Korea (South Korea)": "South Korea", "Taiwan": "Taiwan",
        "Vietnam": "Vietnam", "Iran": "Iran", "Persia (Iran)": "Iran",
        "Turkey": "Turkey", "Ottoman Empire (Turkey)": "Turkey",
        "Yemen": "Yemen",
        "British Mandate of Palestine (Israel)": "Israel",
        "British Protectorate of Palestine (Israel)": "Israel",
    }
    df_asia = dff.copy()
    df_asia["country"] = df_asia["birth_country"].map(ASIAN_MAP)
    df_asia = df_asia.dropna(subset=["country"])

    if df_asia.empty:
        st.warning("No Asian laureates in current filter.")
    else:
        df_tree = (
            df_asia.groupby(["country", "category"])
            .size().reset_index(name="n")
        )
        df_tree["color"] = df_tree["country"].map(COUNTRY_COLORS)

        fig_tree = px.treemap(
            df_tree, path=["country", "category"], values="n",
            color="country", color_discrete_map=COUNTRY_COLORS,
            title="Nobel Prizes in Asia by Country & Field",
        )
        fig_tree.update_layout(**base_layout(height=480))
        fig_tree.update_traces(
            textfont_color="white",
            marker_line_color="#0F0F1E",
            marker_line_width=2,
        )
        st.plotly_chart(fig_tree, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# TAB 2 · DONUT (Continent)
# ─────────────────────────────────────────────────────────────
with tabs[1]:
    st.subheader("Nobel Prize Breakdown by Continent & Field")

    continents = [c for c in CONT_COLORS if c in dff["continent"].values]
    n_conts = len(continents)
    if n_conts == 0:
        st.warning("No continent data available.")
    else:
        cols_per_row = 3
        rows = (n_conts + cols_per_row - 1) // cols_per_row
        specs = [[{"type": "domain"}] * cols_per_row for _ in range(rows)]
        subtitles = (continents + [""] * (rows * cols_per_row - n_conts))

        fig_donut = make_subplots(
            rows=rows, cols=cols_per_row,
            specs=specs, subplot_titles=subtitles,
        )
        for idx, cont in enumerate(continents):
            r, c = divmod(idx, cols_per_row)
            sub = dff[dff["continent"] == cont].groupby("category").size().reset_index(name="n")
            fig_donut.add_trace(
                go.Pie(
                    labels=sub["category"], values=sub["n"],
                    name=cont, hole=0.55,
                    marker_colors=[CAT_COLORS.get(cat, "#888") for cat in sub["category"]],
                    textinfo="none",
                    hovertemplate="<b>%{label}</b><br>%{value} prizes (%{percent})<extra></extra>",
                ),
                row=r + 1, col=c + 1,
            )
        fig_donut.update_layout(
            **base_layout(height=420, showlegend=True),
            legend=dict(
                orientation="h", y=-0.08,
                font=dict(color=FONT_CLR),
            ),
        )
        fig_donut.update_annotations(font_color=FONT_CLR)
        st.plotly_chart(fig_donut, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# TAB 3 · BAR CHART (Peace)
# ─────────────────────────────────────────────────────────────
with tabs[2]:
    st.subheader("Nobel Peace Prize — Individuals vs Organizations per Decade")

    df_peace = dff[dff["category"] == "Peace"].copy()
    if df_peace.empty:
        st.warning("No Peace prizes in current filter.")
    else:
        df_peace["laureate_type_clean"] = df_peace.apply(
            lambda r: "Organization"
            if (r.get("laureate_type") == "Organization" or
                pd.isna(r.get("sex")) or r.get("sex") == "")
            else "Individual",
            axis=1,
        )
        df_peace["decade"] = (df_peace["year"] // 10 * 10).astype(str) + "s"
        df_bar = (
            df_peace.groupby(["decade", "laureate_type_clean"])
            .size().reset_index(name="Count")
        )
        fig_bar = px.bar(
            df_bar, x="decade", y="Count", color="laureate_type_clean",
            barmode="group", text="Count",
            color_discrete_map={"Individual": "#00B4D8", "Organization": "#FF004D"},
            labels={"laureate_type_clean": "Type", "decade": "Decade"},
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(
            **base_layout(height=420),
            legend=dict(title=None, font=dict(color=FONT_CLR)),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# TAB 4 · BOX PLOT (Age distribution)
# ─────────────────────────────────────────────────────────────
with tabs[3]:
    st.subheader("Age Distribution by Nobel Prize Category")

    df_box = dff.dropna(subset=["age", "category"])
    if df_box.empty:
        st.warning("No age data in current filter.")
    else:
        order = (
            df_box.groupby("category")["age"]
            .median().sort_values().index.tolist()
        )
        fig_box = go.Figure()
        for cat in order:
            sub = df_box[df_box["category"] == cat]["age"]
            fig_box.add_trace(go.Box(
                x=sub, name=cat, orientation="h",
                marker_color=CAT_COLORS.get(cat, "#888"),
                boxmean="sd",
                hovertemplate=f"<b>{cat}</b><br>Age: %{{x}}<extra></extra>",
            ))
        fig_box.update_layout(
            **base_layout(height=430),
            showlegend=False,
            xaxis_title="Age",
        )
        st.plotly_chart(fig_box, use_container_width=True)

        medians = df_box.groupby("category")["age"].agg(["median","mean","min","max"]).round(1)
        medians.columns = ["Median", "Mean", "Min", "Max"]
        st.dataframe(medians, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# TAB 5 · LOLLIPOP CHART
# ─────────────────────────────────────────────────────────────
with tabs[4]:
    st.subheader("Top 15 Countries by Number of Nobel Laureates")

    top15 = (
        dff.groupby("birth_country").size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(15)
        .sort_values("count")
    )
    fig_loli = go.Figure()
    # stems
    for _, row in top15.iterrows():
        fig_loli.add_shape(
            type="line",
            x0=0, x1=row["count"],
            y0=row["birth_country"], y1=row["birth_country"],
            line=dict(color="#1e2545", width=2),
        )
    # dots with gradient color
    fig_loli.add_trace(go.Scatter(
        x=top15["count"], y=top15["birth_country"],
        mode="markers+text",
        marker=dict(
            size=14,
            color=top15["count"],
            colorscale=[[0, "#9ecae1"], [1, "#08306b"]],
            showscale=False,
        ),
        text=top15["count"],
        textposition="middle right",
        textfont=dict(color=FONT_CLR, size=11),
        hovertemplate="<b>%{y}</b><br>%{x} laureates<extra></extra>",
    ))
   fig_loli.update_layout(
    height=500,
    xaxis=dict(...),
    yaxis=dict(...)
)
)
        xaxis=dict(range=[0, top15["count"].max() * 1.25],
                   gridcolor=GRID_CLR),
    )
    st.plotly_chart(fig_loli, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# TAB 6 · HEATMAP (Gender × Category)
# ─────────────────────────────────────────────────────────────
with tabs[5]:
    st.subheader("Nobel Prizes by Category and Gender")

    df_heat = dff.copy()
    df_heat["sex_clean"] = df_heat.apply(
        lambda r: "Organization"
        if r.get("laureate_type") == "Organization"
        else (r.get("sex") if pd.notna(r.get("sex")) else "Unknown"),
        axis=1,
    )
    pivot = (
        df_heat.groupby(["sex_clean", "category"])
        .size().unstack(fill_value=0)
    )
    fig_heat = px.imshow(
        pivot,
        color_continuous_scale=["#0d1225", "#185FA5", "#4a8fd4", "#B5D4F4"],
        text_auto=True, aspect="auto",
        labels=dict(x="Category", y="", color="Count"),
    )
    fig_heat.update_layout(**base_layout(height=320))
    fig_heat.update_coloraxes(colorbar_tickfont_color=FONT_CLR)
    st.plotly_chart(fig_heat, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# TAB 7 · WORLD MAP
# ─────────────────────────────────────────────────────────────
with tabs[6]:
    st.subheader("Global Distribution of Nobel Laureates — Birth Country")

    COUNTRY_ISO = {
        "United States of America": "USA", "United Kingdom": "GBR",
        "Germany": "DEU", "France": "FRA", "Sweden": "SWE",
        "Russia": "RUS", "Switzerland": "CHE", "Japan": "JPN",
        "Netherlands": "NLD", "Canada": "CAN", "Italy": "ITA",
        "Austria": "AUT", "India": "IND", "China": "CHN",
        "Israel": "ISR", "Denmark": "DNK", "Norway": "NOR",
        "Australia": "AUS", "Hungary": "HUN", "Poland": "POL",
        "Belgium": "BEL", "South Africa": "ZAF", "Ireland": "IRL",
        "Finland": "FIN", "Portugal": "PRT", "Romania": "ROU",
        "Ukraine": "UKR", "Czech Republic": "CZE", "New Zealand": "NZL",
        "Brazil": "BRA", "Argentina": "ARG", "Colombia": "COL",
        "Chile": "CHL", "Kenya": "KEN", "Nigeria": "NGA",
        "Egypt": "EGY", "Ghana": "GHA", "Pakistan": "PAK",
        "Bangladesh": "BGD", "South Korea": "KOR", "Taiwan": "TWN",
        "Mexico": "MEX", "Turkey": "TUR", "Iran": "IRN",
        "Vietnam": "VNM",
    }
    df_map = dff.copy()
    df_map["iso"] = df_map["birth_country"].map(COUNTRY_ISO)
    country_counts = (
        df_map.dropna(subset=["iso"])
        .groupby(["birth_country", "iso"])
        .size().reset_index(name="Laureates")
    )
    fig_map = px.choropleth(
        country_counts,
        locations="iso",
        color="Laureates",
        hover_name="birth_country",
        color_continuous_scale=["#0d1225", "#185FA5", "#4a8fd4", "#F5C842"],
        projection="natural earth",
    )
    fig_map.update_layout(
        **base_layout(height=460),
        geo=dict(
            bgcolor=PLOT_BG,
            lakecolor=PLOT_BG,
            landcolor="#1A1F3A",
            showframe=False,
            showcoastlines=True,
            coastlinecolor="#1e2545",
        ),
        coloraxis_colorbar=dict(tickfont_color=FONT_CLR, title_font_color=FONT_CLR),
    )
    st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")
st.caption("Nobel Prize Dataset · Built with Streamlit + Plotly")
