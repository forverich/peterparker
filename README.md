# 🏆 Nobel Prize Dashboard

Interactive Streamlit dashboard — convert từ R (ggplot2/treemapify) sang Python (Plotly).

## Charts có trong app
| Tab | Chart | R gốc |
|-----|-------|--------|
| Treemap (Asia) | Treemap quốc gia & lĩnh vực châu Á | `treemapify` |
| Donut (Continent) | Half-donut 6 châu lục | `ggforce::geom_arc_bar` |
| Bar (Peace) | Individual vs Org theo thập kỷ | `geom_bar` |
| Age Boxplot | Phân bổ tuổi theo category | `geom_boxplot` |
| Lollipop | Top 15 quốc gia | `geom_segment + geom_point` |
| Heatmap (Gender) | Gender × Category | `geom_tile` |
| World Map | Choropleth birth country | `map_data("world")` |

---

## Cài đặt & chạy local (VS Code)

### 1. Clone / tạo folder
```bash
cd your-project-folder
```

### 2. Tạo virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Cài dependencies
```bash
pip install -r requirements.txt
```

### 4. Chạy app
```bash
streamlit run app.py
```
→ Mở `http://localhost:8501` trong browser

### 5. Upload data
Sidebar → **Upload your CSV** → chọn `SDnobel__1_.csv`

Cột CSV cần có:
- `year` — năm trao giải
- `category` — Physics / Chemistry / Medicine / Literature / Peace / Economics
- `birth_country` — tên đầy đủ bằng tiếng Anh
- `sex` — Male / Female
- `age` — tuổi khi nhận giải
- `laureate_type` — Individual / Organization

---

## Deploy lên Streamlit Cloud

1. Push code lên GitHub (public hoặc private repo)
2. Vào [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Chọn repo, branch `main`, file `app.py`
4. Click **Deploy** — xong!

> Streamlit Cloud tự đọc `requirements.txt` và cài package.  
> Không cần thêm file nào khác.

---

## Cấu trúc project
```
nobel_dashboard/
├── app.py               ← main app
├── requirements.txt     ← dependencies
├── .streamlit/
│   └── config.toml      ← dark theme config
└── README.md
```
