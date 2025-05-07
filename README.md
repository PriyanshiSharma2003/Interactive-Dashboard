# 📊Panasonic Samridhi Interactive Dashboard
<div align="justify">
An interactive data analytics dashboard built with Python and Streamlit, designed to visualize and analyze key metrics for the Panasonic Samridhi program. The dashboard consolidates registration, transaction, and redemption data, providing stakeholders with actionable insights through an intuitive interface.
---
  
</div>

<div align="justify">

# 🚀 Features
- **Comprehensive Overview:** Summarizes key metrics from all three modules—Registration, Transaction, and Redemption—in a single view.
- **Interactive Filtering:** Filter data by date, zone, state, city, and member tier to customize insights.
- **Dynamic Visualizations:** Real-time charts and graphs for monthly trends, member distribution, and more.
- **KPI Tracking:** Monitor essential KPIs such as total registrations, KYC completion rates, transaction counts, and redemption statistics.
- **User-Friendly Interface:** Built with Streamlit for a seamless and responsive user experience.
</div>

---

## 📊 Dashboard Previews

### 🔹 Overview Tab  
![Overview Dashboard](https://github.com/user-attachments/assets/d44e7af1-3a2f-44b7-b838-e10d99963c2d)

### 🔹 Registration Tab  
![Registration Dashboard](https://github.com/user-attachments/assets/98728336-ff41-4473-9fdc-ab6effd70521)

### 🔹 Transaction Tab  
![Transaction Dashboard](https://github.com/user-attachments/assets/cf782717-27d7-4797-8ac0-dd95dfe93247)

### 🔹 Redemption Tab  
![Redemption Dashboard](https://github.com/user-attachments/assets/a2b01962-2379-4741-a9c7-d0868d895cd5)

---

## 🔐 Authentication Screens 

### 🔸 Login Page  
![Login Page](https://github.com/user-attachments/assets/9c9e4bf7-34d0-478b-b6e2-0548cc239135)

### 🔸 Forgot Password Page  
![Forgot Password](https://github.com/user-attachments/assets/d4f390d1-7068-4492-be93-8950973442a3)


---

## 🛠️ Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/PriyanshiSharma2003/Interactive-Dashboard.git
   cd Interactive-Dashboard

2. **Create a Virtual Environment (Optional but Recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

## 📈 Usage

1. **Run the Dashboard**
    ```bash
    streamlit run dashboard_with_logout.py

2. **Access the Dashboard**  
   Open your browser and navigate to:  
   [http://localhost:8501](http://127.0.0.1:5000/)

## 📌 Technologies Used

- **Python**: Core programming language.
- **Streamlit**: For creating the interactive dashboard interface.
- **Flask**: Used to handle backend routing and serve dynamic content.
- **Pandas**: For data manipulation and analysis.
- **Plotly**: For rich interactive visualizations.
- **HTML/CSS**: For custom layout and design enhancements.

## 📂 Project Structure

```
Interactive-Dashboard/
├── codes/ # Main scripts or modules
├── templates/ # HTML templates (used by Flask)
├── dashboard_with_logout.py # Main application script with login/logout
├── downloadButton.png # Asset used in the UI
└── README.md # This documentation file
