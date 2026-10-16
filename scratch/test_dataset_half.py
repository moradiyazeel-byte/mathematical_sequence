import sys
import os
import glob
import csv
import time
import json
import math

sys.path.insert(0, os.path.abspath("backend"))
from app import create_app

def run_dataset_half_test():
    app = create_app()
    client = app.test_client()

    dataset_dir = os.path.abspath("dataset")
    csv_files = sorted(glob.glob(os.path.join(dataset_dir, "*.csv")))

    all_test_cases = []
    file_summary = {}

    for csv_file in csv_files:
        fname = os.path.basename(csv_file)
        rows = []
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)

        # Take half of the rows (50%)
        half_count = max(1, len(rows) // 2)
        selected_rows = rows[:half_count]

        file_summary[fname] = {
            "total_in_file": len(rows),
            "selected_count": half_count,
            "passed": 0,
            "failed": 0
        }

        for idx, row in enumerate(selected_rows, 1):
            terms = []
            for col in ["t_1", "t_2", "t_3", "t_4", "t_5"]:
                if col in row and row[col] != "":
                    try:
                        terms.append(float(row[col]))
                    except ValueError:
                        pass

            expected_next = None
            if "t_6" in row and row["t_6"] != "":
                try:
                    expected_next = float(row["t_6"])
                except ValueError:
                    pass

            expected_type = (row.get("pattern_type") or fname.replace(".csv", "")).strip().lower()

            all_test_cases.append({
                "file": fname,
                "row_num": idx,
                "sequence": terms,
                "expected_next": expected_next,
                "expected_type": expected_type
            })

    total_tests = len(all_test_cases)
    correct_predictions = 0
    total_time_ms = 0
    results_table = []

    for idx, case in enumerate(all_test_cases, 1):
        seq = case["sequence"]
        expected_next = case["expected_next"]
        expected_type = case["expected_type"]
        fname = case["file"]

        t0 = time.perf_counter()
        resp = client.post("/api/predict", json={"sequence": seq, "save_to_history": False})
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        total_time_ms += elapsed_ms

        data = resp.get_json() or {}
        payload = data.get("data", {})
        pred = payload.get("prediction", {})

        actual_next = pred.get("next_term")
        actual_type = (pred.get("pattern_type") or "unknown").lower()
        label = pred.get("sequence_type_label") or actual_type
        conf = pred.get("confidence", 0.0)

        is_pred_correct = False
        if actual_next is not None:
            if "decreasing" in fname:
                # Must be strictly less than last term
                is_pred_correct = (actual_next < seq[-1])
            elif "increasing" in fname:
                # Must be strictly greater than last term
                is_pred_correct = (actual_next > seq[-1])
            elif expected_next is not None:
                is_pred_correct = math.isclose(float(actual_next), float(expected_next), rel_tol=0.05, abs_tol=1.0)
            else:
                is_pred_correct = True

        if is_pred_correct:
            correct_predictions += 1
            file_summary[fname]["passed"] += 1
        else:
            file_summary[fname]["failed"] += 1

        seq_str = ", ".join(str(int(v) if v.is_integer() else round(v, 2)) for v in seq[:5])
        results_table.append({
            "id": idx,
            "file": fname,
            "sequence": f"[{seq_str}]",
            "expected_next": round(expected_next, 2) if expected_next is not None else "N/A",
            "predicted_next": round(actual_next, 2) if actual_next is not None else "N/A",
            "pattern_label": label,
            "confidence": f"{round(conf * 100, 1)}%",
            "latency": f"{elapsed_ms} ms",
            "status": "✅ PASS" if is_pred_correct else "❌ FAIL"
        })

    avg_latency = round(total_time_ms / total_tests, 2)
    pred_acc_pct = round((correct_predictions / total_tests) * 100, 1)

    print("\n" + "=" * 65)
    print(f"  DATASET BENCHMARK RESULTS (50% Sample from Every File)")
    print("=" * 65)
    print(f"  Total Files Processed : {len(csv_files)}")
    print(f"  Total Test Cases      : {total_tests}")
    print(f"  Prediction Accuracy   : {correct_predictions}/{total_tests} ({pred_acc_pct}%)")
    print(f"  Average Query Latency : {avg_latency} ms / query")
    print("=" * 65)

    print("\nFile-by-File Summary Table:")
    for fname, info in file_summary.items():
        pass_rate = round((info["passed"] / info["selected_count"]) * 100, 1) if info["selected_count"] > 0 else 0
        print(f"  • {fname:<22}: {info['passed']}/{info['selected_count']} passed ({pass_rate}%)")

    output_data = {
        "summary": {
            "total_files": len(csv_files),
            "total_cases": total_tests,
            "correct_predictions": correct_predictions,
            "pred_accuracy_pct": pred_acc_pct,
            "avg_latency_ms": avg_latency,
            "total_time_ms": round(total_time_ms, 2)
        },
        "file_summary": file_summary,
        "rows": results_table
    }

    with open("scratch/test_dataset_half_results.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

if __name__ == "__main__":
    run_dataset_half_test()
