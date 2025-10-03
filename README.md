# 🎯 StrikeZone App

A **Streamlit-based tool** for exploring option strategies.  
Users can build combinations of option legs (long/short calls and puts), set premiums, strikes, and instantly see payoff diagrams.

---

## ✨ Features

- 🛠️ **Interactive sidebar** to configure option legs  
- 📈 **Net payoff curve** plus individual leg profiles (colored)  
- 🧭 **Visual aids**:
  - Zero P/L baseline  
  - Underlying price line  
  - Strike price markers  
  - Adjustable price range (±%)  
- 🌐 **Multi-language support**: English, Russian, Ukrainian  
- 🧩 **Clean extensible structure**:  
  - `build_sidebar`  
  - `compute_curve`  
  - `draw_chart`  

---

## 🎯 Purpose
This project is intended as a **lightweight educational and prototyping tool** for options trading strategies.

---

## 🚀 Getting Started

```bash
# Clone repo

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the app
streamlit run app/main.py
