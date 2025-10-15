# 🧪 Materials Science Hub

> **An intelligent community platform for materials science enthusiasts, researchers, and engineers — powered by Django, REST API, and Machine Learning.**

---

## 🌐 Live Domain
**[https://materialsscience.net](https://materialsscience.net)**

---

## 🚀 Overview

The **Materials Science Hub** is an open-source initiative that bridges materials science with data-driven intelligence.  
It provides a collaborative web ecosystem for researchers, engineers, and students to explore materials data, discuss theories, and experiment with AI-powered insights.

The project is built with **Python (Django & Django REST Framework)** for the backend and **HTML, CSS, and JavaScript** for the frontend — no Bootstrap, fully custom UI, and uses **Font Awesome icons**.

---

## 🧩 Key Features

### 🔹 Materials Database
Search and explore thousands of materials with detailed physical, chemical, optical, electrical, thermal properties and so on.

### 🔹 MatSciChat
ML-powered chat interface specialized in materials science.  
Predicts degradation, suggests alloys, and provides theoretical insights — built using a custom-trained ML mdoel.

### 🔹 Forum
Community-driven discussion hub for sharing knowledge, results, and innovations with post-like-comment-reply support.

### 🔹 Resources
A categorized library of **books, journals, and simulation software** used in materials science learning and research.

### 🔹 API Documentation
REST API access to the materials database and MatSciChat endpoints for research and automation use.

### 🔹 Press & Blog
Official announcements, technology updates, and featured research from materials engineers around the world.

### 🔹 Career & Pricing
Browse collaboration opportunities and MatSciChat subscription tiers for extended usage.

---

## ⚙️ Tech Stack

| Layer | Technologies |
|-------|---------------|
| **Frontend** | HTML, CSS, JavaScript, Font Awesome |
| **Backend** | Python, Django, Django REST Framework |
| **Database** | PostgreSQL |
| **Authentication** | Django Default Authentication |
| **AI Integration** | Custom Materials Science Ml model |
| **Deployment** | Nginx, Gunicorn, PgBouncer, VPS Cluster |
| **Version Control** | Git & GitHub |

---

## 🧰 Installation

### Prerequisites
- Python 3.10+
- PostgreSQL
- pip & virtualenv

### Setup

```bash
git clone https://github.com/uch105/mse.git
cd mse
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Installation

**1. Clone the repository**  

   ```bash
   git clone https://github.com/uch105/mse.git
   cd mse
   ```
**2.  Environment Variables & Database Configuration**

Edit your `.env` file:
```bash
DEBUG="True"
SECRET_KEY="your-secret-key"
ALLOWED_HOSTS="127.0.0.1,localhost, your-server-ip"
DB_HOST="localhost-OR-IPADDRESS"
DB_NAME="name_of_database"
DB_USER="name_of_database_user"
DB_PASSWORD="database_password"
EMAIL_HOST_USER="youremail@gmail.com"
EMAIL_HOST_PASSWORD="app_password_from_gmail"
```
**3. Run Migrations**
```bash
python3 manage.py makemigrations
# IN CASE 'core' is ignored,
# RUN 'python3 manage.py makemigrations core'
python3 manage.py migrate
# IN CASE 'core' is ignored,
# RUN 'python3 manage.py migrate core'
```
**4. Run Sever**
```bash
python3 manage.py runserver
```

---

## 🧑‍💻 Contribution

We welcome contributions from ***materials scientists***, ***engineers***, and ***developers***.
- Fork the repo
- Create a new branch
```bash
git checkout -b feature-name
```
- Commit your changes
```bash
git commit -m "Added new feature"
```
- Push to your fork and open a pull request

---

## 🧠 Future Roadmap

- Integrate custom-trained MatSciGPT model
- Add advanced materials search with environmental filters
- Launch contributor leaderboard
- Integrate citation & reference system for academic sharing

---

## 📢 Press Release
Read the official beta launch announcement:  
👉    **[MatSci Hub Press](https://materialsscience.net/press/)**

---

## 📧 Contact
- Official Email: [matscihubofficial@gmail.com](mailto:matscihubofficial@gmail.com)
- Core Team Members: [MatSci Hub Team](https://materialsscience.net/about/)
- Technical Lead: [Tanvir Saklan](mailto:saklantanvir@gmail.com)

---

## 🧾 License

This project is licensed under the *Apache License 2.0*. You may use, modify, and distribute the code, including for commercial purposes, as long as you comply with the terms of the license.  
  
See the [LICENSE](./LICENSE) file fore details.  
  
If you distribute the code, you must provide a copy of the license and include a NOTICE file with any required attributions.

---

### ⭐ If you like this project, give it a star on GitHub!

---
