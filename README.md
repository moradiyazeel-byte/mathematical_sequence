# Universal Mathematical Sequence Prediction System

SeqPredict is a state-of-the-art hybrid sequence prediction system designed to identify, analyze, and extrapolate numerical sequences of any degree or pattern. By combining a mathematically rigorous **Deterministic Rule Engine** (incorporating finite differences) with an advanced **Random Forest Classifier** (via Scikit-Learn), the system delivers high-accuracy predictions, confidence reports, and detailed calculation breakdowns.

---

## Features

- **Three-Layer Hybrid Prediction Architecture**:
  - **Layer 1: Rule Engine**: Resolves standard closed-form mathematical sequences instantly with $100\%$ confidence.
  - **Layer 2: ML Classifier**: Predicts sequence categories using 53 engineered statistical and relational features.
  - **Layer 3: Hybrid Resolver**: Coordinates path execution based on confidence thresholds and applies agreement bonuses or disagreement penalties.
- **Arbitrary Polynomial Extrapolator**: Implements the *Method of Finite Differences* to detect and solve polynomial sequences of any degree $k \le n-2$ without hardcoding.
- **RESTful Flask API**: Exposes endpoints for real-time predictions, search history, user authentication, and system health checks.
- **Premium Glassmorphic Frontend UI**: Features a modern dark-themed web interface for sequence input, prediction visualizer, and detailed model execution traces.
- **User Authentication & Authorization**: Secures history and profile pages using JSON Web Tokens (JWT) and BCrypt password hashing.
- **System Telemetry & Auditing**: Persists application execution traces, database caching, and custom system logging records.

---

## Technology Stack

### Backend
- **Core Framework**: Flask
- **Machine Learning**: Scikit-Learn, NumPy, Pandas, Joblib
- **Database**: SQLite3 (WAL mode enabled)
- **Security & Auth**: PyJWT, BCrypt, Flask-CORS

### Frontend
- **Interface**: HTML5, Vanilla JavaScript, CSS3 (Glassmorphism & animations)
- **Typography & Icons**: FontAwesome, Outfit & Inter (Google Fonts)

---

## Folder Structure

```
mathematical_sequence/
├── README.md                  # Project documentation
├── backend/                   # Backend Flask application
│   ├── app.py                 # Application factory & entry point
│   ├── config.py              # Configuration manager (Dev, Prod, Test)
│   ├── requirements.txt       # Python dependencies
│   ├── database/
│   │   └── database.py        # Database migration & CRUD queries
│   ├── models/
│   │   ├── user_model.py      # User profile data class
│   │   ├── prediction_model.py # Prediction record data class
│   │   └── sequence_model.pkl # Pre-trained Random Forest model bundle
│   ├── routes/
│   │   ├── auth_routes.py     # Authentication blueprint routes
│   │   ├── user_routes.py     # Profile management blueprint routes
│   │   ├── predict_routes.py  # Sequence prediction blueprint routes
│   │   ├── history_routes.py  # History management blueprint routes
│   │   ├── admin_routes.py    # Admin configurations blueprint routes
│   │   └── health_routes.py   # Health status checks blueprint routes
│   ├── services/
│   │   ├── rule_engine.py     # Rule-based sequence family detectors
│   │   ├── ml_predictor.py    # Random Forest inference manager
│   │   ├── model_loader.py    # Serialization asset helper
│   │   └── predictor.py       # Hybrid decision resolver
│   └── utils/
│       ├── auth.py            # Authentication decorators & helpers
│       ├── preprocessing.py   # Raw input parser & range validator
│       └── feature_engineering.py # 53-dimensional feature extractor
├── dataset/                   # Synthetic dataset directory (16 CSV files)
├── frontend/                  # Static frontend application
│   ├── index.html             # Landing page
│   ├── predict.html           # Prediction dashboard
│   ├── history.html           # Prediction history archive
│   ├── login.html             # User auth panel
│   ├── about.html             # Project details
│   ├── css/
│   │   └── style.css          # Main styling stylesheet
│   └── js/
│       ├── auth_helper.js     # Navbar and JWT session guard
│       ├── predict.js         # Predictions & trace visualizer
│       └── history.js         # History search & pagination
└── training/                  # ML model training pipeline
    ├── generate_dataset.py    # Synthetic dataset CSV generator
    ├── train_model.py         # RF model training pipeline script
    ├── evaluate_model.py      # Classifier evaluation script
    ├── test_model.py          # Interactive command-line sequence tester
    └── save_model.py          # Joblib serialization utility
```

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/mathematical_sequence.git
   cd mathematical_sequence
   ```

2. **Set up Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Unix/macOS:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

---

## How to Run

### 1. Synthetic Data & Model Training
Generate the synthetic datasets and train the Random Forest Classifier:
```bash
# Generate 100 rows per category (16 categories, total 1600 rows)
python training/generate_dataset.py --samples 100

# Run training (trains model, outputs backend/models/sequence_model.pkl)
python training/train_model.py

# Evaluate model metrics
python training/evaluate_model.py
```

### 2. Start Backend Server
Run the Flask API application server:
```bash
cd backend
python app.py
```
The backend API will start on `http://127.0.0.1:5000`.

### 3. Start Frontend Dashboard
Serve the static files using Python's built-in HTTP server:
```bash
# From project root
cd frontend
python -m http.server 8000
```
Open `http://127.0.0.1:8000` in your web browser.

---

## API Documentation

### POST `/api/predict`
Executes hybrid prediction for a given numerical sequence.
- **Request Body**:
  ```json
  {
    "sequence": [3, 7, 11, 15, 19],
    "save_to_history": true
  }
  ```
- **Response Payload**:
  ```json
  {
    "success": true,
    "data": {
      "id": 42,
      "input_sequence": [3.0, 7.0, 11.0, 15.0, 19.0],
      "sequence_length": 5,
      "prediction": {
        "next_term": 23,
        "pattern_type": "arithmetic",
        "sequence_type_label": "Arithmetic Sequence",
        "method_used": "rule",
        "confidence": 1.0,
        "confidence_label": "Very High"
      },
      "explanation": {
        "formula": "t(n) = a + (n−1)d",
        "calculation": "Common difference d = 19.0 − 15.0 = 4.0. Next term = 19.0 + 4.0 = 23.",
        "summary": "The sequence [3.0, 7.0, 11.0, 15.0, 19.0] was deterministically identified as an Arithmetic Sequence by the rule engine."
      }
    }
  }
  ```

---

## Supported Sequence Types

The system supports **16 distinct mathematical sequence categories**:
1. **Arithmetic**: Common difference constant $t_{n} - t_{n-1} = d$.
2. **Geometric**: Common ratio constant $t_{n} / t_{n-1} = r$.
3. **Prime**: Consecutive prime numbers starting from a random prime.
4. **Even**: Even arithmetic sequences.
5. **Odd**: Odd arithmetic sequences.
6. **Square**: Squares of consecutive indexes $n^2$.
7. **Cube**: Cubes of consecutive indexes $n^3$.
8. **Triangular**: $n(n+1)/2$ representing triangular numbers.
9. **Factorial**: Factorial values $n!$.
10. **Powers of 2**: Exponential powers of base 2 ($2^n$).
11. **Powers of 3**: Exponential powers of base 3 ($3^n$).
12. **Polynomial**: Custom degree-$k$ polynomial sequences ($c_k n^k + \dots + c_0$) detected using finite differences.
13. **Alternating**: Sequences alternating consistently in sign or magnitude.
14. **Increasing**: Strictly increasing sequences with uniform step distributions.
15. **Decreasing**: Strictly decreasing sequences with uniform step distributions.
16. **Custom**: Mixed composite patterns and Fibonacci-like sequences (e.g. Lucas numbers).

---

## Future Scope

- **Symbolic Regression Integration**: Introduce genetic algorithms (e.g. PySR) to output exact mathematical formula representations of custom sequence classes.
- **Deep Learning Extenders**: Train Recurrent Neural Networks (LSTM/GRU) or Transformer-based sequence architectures for complex, non-stationary sequence predictions.
- **Mathematical Function Plotter**: Add interactive charts (e.g. Chart.js) to the frontend to visualize the sequence trend and extrapolation curves.

---

## Screenshots Section

> [!NOTE]
> System snapshots and design mockups are stored under the [screenshots/](file:///c:/Users/DELL/OneDrive/Desktop/quillix/mathematical_sequence/screenshots) folder.

---

## License

Distributed under the MIT License. See `LICENSE` for details.
