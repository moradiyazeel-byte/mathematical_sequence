import sys
import os

try:
    import numpy as np
    import scipy
    import sklearn
    import joblib
    print("NumPy version:", np.__version__)
    print("SciPy version:", scipy.__version__)
    print("Scikit-Learn version:", sklearn.__version__)
except Exception as e:
    print("Import error:", e)
    sys.exit(1)

# Test model unpickling
model_path = os.path.join("backend", "models", "sequence_model.pkl")
if os.path.exists(model_path):
    try:
        model = joblib.load(model_path)
        print("SUCCESS: sequence_model.pkl loaded successfully!")
        print("Model bundle keys/type:", type(model))
    except Exception as e:
        print("Model load error:", e)
        sys.exit(2)
else:
    print("Model file not found at:", model_path)
