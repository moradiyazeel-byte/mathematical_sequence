import json
import math

def check():
    with open('scratch/test_200_results.json', 'r') as f:
        d = json.load(f)
    
    failures = []
    for r in d['rows']:
        exp = r['expected_next']
        pred = r['predicted_next']
        
        is_correct = False
        if exp is not None and pred is not None:
            try:
                is_correct = math.isclose(float(exp), float(pred), rel_tol=1e-4, abs_tol=1e-4)
            except Exception:
                pass
        
        if not is_correct:
            failures.append({
                'id': r['id'],
                'name': r['name'],
                'category': r['category'],
                'sequence': r['sequence'],
                'expected': exp,
                'predicted': pred,
                'pattern_type': r['pattern_type']
            })
            
    print(f"Total failures: {len(failures)}")
    for f in failures:
        print(f"ID {f['id']} | {f['name']} | Cat: {f['category']} | Pattern: {f['pattern_type']} | Expected: {f['expected']} | Predicted: {f['predicted']}")

if __name__ == '__main__':
    check()
