---
title: drug-discovery-dashboard
colorFrom: green
colorTo: blue
sdk: docker
---

<div align="center">

<h1>⬡ MoleSight AI — Drug Discovery Dashboard</h1>
<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&duration=3000&pause=1000&color=00FF88&center=true&vCenter=true&width=700&lines=Molecular+Property+Analysis+%26+Visualization;Drug-Likeness+ML+Classifier+(Gradient+Boosting);ADMET+Multi-Output+Regression+Predictor" alt="Typing SVG"/>

<br/>

[![Python](https://img.shields.io/badge/Python-3.10+-3b82f6?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-4f46e5?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-3b82f6?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![RDKit](https://img.shields.io/badge/RDKit-Cheminformatics-00ff88?style=for-the-badge)](https://www.rdkit.org/)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Spaces-ffcc00?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/mnoorchenar/spaces)
[![Status](https://img.shields.io/badge/Status-Active-22c55e?style=for-the-badge)](#)

<br/>

**⬡ MoleSight AI** — An interactive drug discovery dashboard that computes physicochemical properties from SMILES, predicts drug-likeness and ADMET profiles using ML models, and ranks compound libraries via a virtual screening engine — all deployable on HuggingFace Spaces.

<br/>

---

</div>

## Table of Contents

- [Features](#-features)
- [Architecture](#️-architecture)
- [Getting Started](#-getting-started)
- [Docker Deployment](#-docker-deployment)
- [Dashboard Modules](#-dashboard-modules)
- [ML Models](#-ml-models)
- [Project Structure](#-project-structure)
- [Author](#-author)
- [Contributing](#-contributing)
- [Disclaimer](#disclaimer)
- [License](#-license)

---

## ✨ Features

<table>
  <tr>
    <td>⬡ <b>Molecular Property Engine</b></td>
    <td>Computes 12+ physicochemical descriptors (MW, LogP, HBD, HBA, TPSA, QED, Fsp³ …) from any SMILES string using RDKit, plus 2D structure SVG rendering</td>
  </tr>
  <tr>
    <td>📏 <b>Multi-Rule Filter Assessment</b></td>
    <td>Evaluates Lipinski's Rule of Five, Veber Rules, and Ghose Filter simultaneously with pass/fail breakdown per criterion</td>
  </tr>
  <tr>
    <td>🧠 <b>Drug-Likeness ML Classifier</b></td>
    <td>Gradient Boosting Classifier trained on 1,500 synthetic compounds; returns probability gauge, confidence level, feature importances, and 5-fold CV accuracy</td>
  </tr>
  <tr>
    <td>🧪 <b>ADMET Multi-Output Predictor</b></td>
    <td>Predicts Absorption, Distribution, Metabolism, Excretion, and Toxicity scores using a multi-output Gradient Boosting Regressor with traffic-light visual summary</td>
  </tr>
  <tr>
    <td>🔒 <b>Secure by Design</b></td>
    <td>No user data stored; all computations are stateless; configurable secret key via environment variables</td>
  </tr>
  <tr>
    <td>🐳 <b>Containerized Deployment</b></td>
    <td>Multi-stage Docker build optimised for HuggingFace Spaces (port 7860), Gunicorn WSGI server, non-root user execution</td>
  </tr>
</table>

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    MoleSight AI Dashboard                    │
│                                                              │
│  ┌─────────────┐   ┌─────────────┐   ┌──────────────────┐  │
│  │  Compound   │──▶│  RDKit +    │──▶│  Flask Blueprint  │  │
│  │  Library    │   │  ML Engine  │   │  API Backend      │  │
│  │  (20 drugs) │   │  (2 models) │   │  (3 blueprints)   │  │
│  └─────────────┘   └─────────────┘   └────────┬─────────┘  │
│                                                │             │
│                                    ┌───────────▼──────────┐  │
│                                    │  Jinja2 Templates    │  │
│                                    │  + Plotly.js Charts  │  │
│                                    └──────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Git

### Local Installation

```bash
# 1. Clone the repository
git clone https://github.com/mnoorchenar/drug-discovery-dashboard.git
cd drug-discovery-dashboard

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env with your settings

# 5. Run the application
python app.py
```

Open your browser at `http://localhost:7860` 🎉

---

## 🐳 Docker Deployment

```bash
# Build and run with Docker
docker build -t drug-discovery-dashboard .
docker run -p 7860:7860 drug-discovery-dashboard

# Or use docker compose
docker compose up --build
```

---

## 📊 Dashboard Modules

| Module | Description | Status |
|--------|-------------|--------|
| 📊 Analytics Dashboard | KPI overview, chemical space scatter, QED distribution, property heatmap | ✅ Live |
| 🔬 Molecule Analyzer | SMILES → 12 properties, 2D structure render, Lipinski/Veber/Ghose rules | ✅ Live |
| 🧠 Drug-Likeness ML | GBM classifier with probability gauge, radar chart, feature importances | ✅ Live |
| 🧪 ADMET Predictor | Multi-output regressor for 5 ADMET endpoints with traffic light summary | ✅ Live |
| 🎯 Virtual Screening | Composite MPO scoring of 20-compound library, ranked table & scatter | ✅ Live |
| 🔗 REST API | JSON endpoints for `/api/properties`, `/api/drug-likeness`, `/api/admet` | 🔄 Beta |

---

## 🧠 ML Models

```python
# Core Models Used in MoleSight AI
models = {
    "drug_likeness_classifier": "GradientBoostingClassifier — 200 estimators, depth=4, 5-fold CV",
    "admet_regressor":          "MultiOutputRegressor(GradientBoostingRegressor) — 5 ADMET endpoints",
    "training_data":            "1,500–2,000 synthetic compounds (drug-like + decoy distributions)",
    "input_features":           "MW, LogP, HBD, HBA, TPSA, RotBonds, QED, Fsp³",
    "molecular_engine":         "RDKit — SMILES parsing, descriptor computation, 2D SVG rendering",
}
```

---

## 📁 Project Structure

```
drug-discovery-dashboard/
│
├── 📂 app/
│   ├── 📂 routes/
│   │   ├── main.py            # Home dashboard + Molecule Analyzer routes
│   │   ├── prediction.py      # Drug-Likeness ML + ADMET routes + REST API
│   │   └── screening.py       # Virtual Screening + target filter routes
│   │
│   ├── 📂 models/
│   │   ├── drug_likeness.py   # GBM drug-likeness classifier (train + predict)
│   │   └── admet.py           # Multi-output ADMET regressor (train + predict)
│   │
│   ├── 📂 utils/
│   │   ├── molecular.py       # RDKit property computation, rule assessments, SVG
│   │   └── charts.py          # Plotly chart generators (radar, gauge, heatmap …)
│   │
│   ├── 📂 data/
│   │   └── compound_library.py  # 20 curated drug entries + summary stats
│   │
│   └── __init__.py            # Flask app factory + model initialisation
│
├── 📂 templates/
│   ├── base.html              # Biopunk dark theme layout + sidebar navigation
│   ├── index.html             # Analytics dashboard
│   ├── analyze.html           # Molecule Analyzer
│   ├── prediction.html        # Drug-Likeness ML page
│   ├── admet.html             # ADMET Predictor page
│   └── screening.html         # Virtual Screening page
│
├── 📂 static/
│   ├── 📂 css/style.css       # Supplemental responsive styles
│   └── 📂 js/main.js          # Client-side interactions + Plotly resize
│
├── 📄 app.py                  # Application entry point
├── 📄 Dockerfile              # Multi-stage Docker build (port 7860)
├── 📄 requirements.txt        # Python dependencies
└── 📄 .env.example            # Environment variable template
```

---

## 👨‍💻 Author

<div align="center">

<table>
<tr>
<td align="center" width="100%">

<img src="https://avatars.githubusercontent.com/mnoorchenar" width="120" style="border-radius:50%; border: 3px solid #00ff88;" alt="Mohammad Noorchenarboo"/>

<h3>Mohammad Noorchenarboo</h3>

<code>Data Scientist</code> &nbsp;|&nbsp; <code>AI Researcher</code> &nbsp;|&nbsp; <code>Biostatistician</code>

📍 &nbsp;Ontario, Canada &nbsp;&nbsp; 📧 &nbsp;[mohammadnoorchenarboo@gmail.com](mailto:mohammadnoorchenarboo@gmail.com)

──────────────────────────────────────

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/mnoorchenar)&nbsp;
[![Personal Site](https://img.shields.io/badge/Website-mnoorchenar.github.io-4f46e5?style=for-the-badge&logo=githubpages&logoColor=white)](https://mnoorchenar.github.io/)&nbsp;
[![HuggingFace](https://img.shields.io/badge/HuggingFace-ffcc00?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/mnoorchenar/spaces)&nbsp;
[![Google Scholar](https://img.shields.io/badge/Scholar-4285F4?style=for-the-badge&logo=googlescholar&logoColor=white)](https://scholar.google.ca/citations?user=nn_Toq0AAAAJ&hl=en)&nbsp;
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/mnoorchenar)

</td>
</tr>
</table>

</div>

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

---

## Disclaimer

<span style="color:red">This project is developed strictly for educational and research purposes and does not constitute professional medical, pharmaceutical, or clinical advice of any kind. All datasets used are either synthetically generated or represent publicly available literature values — no proprietary or patient data is stored or processed. Predictions are for demonstration only and must not be used to guide real drug development decisions. This software is provided "as is" without warranty of any kind; use at your own risk.</span>

---

## 📜 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:00ff88,100:00ccff&height=120&section=footer&text=Made%20with%20%E2%9D%A4%EF%B8%8F%20by%20Mohammad%20Noorchenarboo&fontColor=0a0e1a&fontSize=18&fontAlignY=80" width="100%"/>

[![GitHub Stars](https://img.shields.io/github/stars/mnoorchenar/drug-discovery-dashboard?style=social)](https://github.com/mnoorchenar/drug-discovery-dashboard)
[![GitHub Forks](https://img.shields.io/github/forks/mnoorchenar/drug-discovery-dashboard?style=social)](https://github.com/mnoorchenar/drug-discovery-dashboard/fork)

<sub>The name "MoleSight AI" is used purely for academic and portfolio purposes. Any similarity to existing products or trademarks is entirely coincidental. This project has no affiliation with any commercial pharmaceutical or biotech entity.</sub>

</div>
