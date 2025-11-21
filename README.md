# DevOps To-Do List Project

A simple, university-level project demonstrating core DevOps principles: **Containerization**, **CI/CD**, and **Automated Testing**.

## 🚀 Project Overview

This project is a simple "To-Do List" web application built with Python (Flask). The main goal is not the app itself, but the *DevOps infrastructure* around it.

**Tools Used:**
- **Code**: Python, Flask, HTML/CSS (Bootstrap)
- **Database**: SQLite (Simple file-based DB)
- **Containerization**: Docker
- **CI/CD**: GitHub Actions
- **Testing**: Pytest
- **Dashboard**: GitHub API Integration

## ✨ New Features
- **Premium UI**: Modern interface with priority badges and due dates.
- **CI/CD Dashboard**: Real-time visualization of your GitHub Actions pipeline status.
- **Task Editing**: Fix typos or update priorities easily.
- **Filtering**: View tasks by Status (Active/Completed) or Priority.
- **Robustness**: Flash messages for feedback and "Clear Completed" to keep things tidy.

---

## 🛠️ How to Run

### Option 1: Run Locally (Python)

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run the App**:
    ```bash
    python app.py
    ```
3.  **Access**: Open `http://localhost:5001` in your browser.

### Option 2: Run with Docker (Recommended)

1.  **Build the Image**:
    ```bash
    docker build -t todo-app .
    ```
2.  **Run the Container**:
    ```bash
    docker run -p 5001:5001 todo-app
    ```
3.  **Access**: Open `http://localhost:5001` in your browser.

---

## 📚 Viva Questions & Answers

**Q: What is DevOps?**
A: DevOps is a set of practices that combines software development (Dev) and IT operations (Ops). It aims to shorten the systems development life cycle and provide continuous delivery with high software quality.

**Q: Why did we use Docker?**
A: Docker allows us to "containerize" the application. This means we package the code, libraries, and dependencies into a single unit (image). It ensures the app runs exactly the same on my laptop, your laptop, and the server ("It works on my machine" problem solved).

**Q: What is CI/CD?**
A: 
- **CI (Continuous Integration)**: Automatically running tests and checks whenever code is changed. In this project, GitHub Actions runs our tests every time we push code.
- **CD (Continuous Delivery/Deployment)**: Automatically deploying the application. (We demonstrated the "Build" part of this).

**Q: How does the Pipeline work?**
A: We defined a workflow in `.github/workflows/ci.yml`. It has two jobs:
1.  **Test**: Installs Python and runs `pytest` to check for bugs.
2.  **Build**: If tests pass, it builds the Docker image to ensure it's ready for deployment.

---

## 🧪 Testing

We use `pytest` for automated testing.
Run tests manually with:
```bash
pytest
```
