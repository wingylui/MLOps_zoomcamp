# Perth Housing Price Prediction – MLOps End-to-End Project

This repository contains an end-to-end MLOps project that predicts housing prices in Perth, Australia. It integrates data preprocessing, feature engineering, ML experimentation, automated orchestration, model deployment, monitoring, and infrastructure-as-code.



### 🏡 Problem Statement

The goal is to predict property prices in Perth using a mix of geographic, demographic, and real estate features. The model serves real-time predictions via an API and is continuously monitored and retrained as data drift or performance degradation is detected.

---

### 📦 Dataset & Feature Engineering

- **Source**: Housing dataset from [Kaggle](https://www.kaggle.com/datasets/heptix/perth-property-prices/data)
- **Custom Features**:
  - `distance_to_coastline`: Geospatially computed distance from each house to the nearest coastline.
  - `ICSEA_score`: Integrated contextual socio-educational score for schools in the surrounding area.
- Additional preprocessing steps include outlier removal, normalization, categorical encoding, and imputation.

---

### 🔬 Experiment Tracking & Model Management

- **MLflow**:
  - Experiment tracking: log metrics, parameters, artifacts
  - Hyperparameter tuning using random/grid search
  - Model registry used to manage the transition between staging and production models

---

### 🔁 Automated Retraining Workflow

- **Orchestration with Prefect**:
  - Automated pipeline triggers on a schedule or drift condition
  - Tasks include data fetching, feature engineering, training, evaluation, and model registration


---

### 🐳 Dockerized Inference Stack

- **Flask API**:
  - Provides an interface for users to submit features and receive housing price predictions
  - Uses the latest production model from MLflow registry

- **Monitoring**:
  - **Grafana** visualizes API metrics and model performance indicators
  - Drift detection logs are stored in a **PostgreSQL** warehouse
  - **Adminer** is used to manage the database through a web UI

---

### ☁️ Cloud Infrastructure

- Hosted on **AWS EC2**
- Provisioned with **Terraform**, including:
  - EC2 instance setup
  - IAM roles and security groups
  - S3 bucket for storing ML artifacts

---

### 🧪 Testing

- **Pytest** is used to test:
  - Feature preprocessing logic
  - Flask API input/output and prediction consistency

---

### 🔧 Future Improvements (Planned)

To further improve the robustness and automation of this project, the following enhancements are planned:

- ✅ **Integration Tests**: Add end-to-end tests that simulate the full prediction pipeline including API, database, and model.
- ✅ **Linting & Code Formatting**: Integrate tools like `flake8`, `black`, or `ruff` to maintain code quality and style.
- ✅ **Pre-commit Hooks**: Use `pre-commit` to run checks (e.g., linting, formatting, secrets detection) before each commit.
- ✅ **CI/CD Pipeline**: Implement GitHub Actions for:
  - Automated testing
  - Docker image builds
  - Terraform deployment to AWS
  - Notifying via Slack/email on deployment status

These additions will align the project more closely with production-grade MLOps standards and best practices.

---

### 🧠 Tech Stack Summary

| Layer                 | Tool/Tech                          |
|----------------------|------------------------------------|
| Data & Features       | Pandas, GeoPy, Custom Python       |
| Experimentation       | MLflow, Scikit-learn, Xgboost               |
| Orchestration         | Prefect                            |
| Model Serving         | Flask, Docker Compose              |
| Monitoring            | Grafana, PostgreSQL       |
| Cloud Infrastructure  | AWS EC2, Terraform                 |
| Testing               | Pytest                             |

---

### 📂 Directory Structure

```text
project/
├── data_processing/         # Feature engineering and transformation logic
├── dataset/                 # Raw and cleaned datasets
├── deploy-monitoring/       # Grafana, Adminer, and PostgreSQL setup
├── docker/
│   └── mlflow-prefect/      # MLflow and Prefect Docker configs
├── experiment/              # Model training, evaluation, and registry code
├── img/                     # Flowcharts and architecture diagrams
├── infra/                   # Terraform configurations for AWS infrastructure
├── test/                    # Unit and (future) integration tests
└── docker-compose.yml       # Launches the full stack locally or on EC2