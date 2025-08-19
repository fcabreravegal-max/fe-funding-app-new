
# Fossil East Funding Optimizer 💸

Streamlit web app to optimize and visualize weekly intercompany funding for Fossil East.

## Features
- Upload weekly Excel workbook
- Extract cash positions and ICo AP to FE
- Display surplus cash and flow diagram
- Auto-allocate optimal (greedy) sources
- Constraint controls in sidebar

## Local Run

```bash
pip install -r requirements.txt
streamlit run fe_funding_app.py
```

## Docker Run

```bash
docker build -t fe-funding-app .
docker run -p 8501:8501 fe-funding-app
```

Then visit http://localhost:8501
