import json
import re

try:
    with open(r'c:\Users\MC\AppData\Local\Temp\audit_results.jsonl', encoding='utf-8-sig') as f:
        content = f.read().strip()
    content = re.sub(r'\}\s*\{', '},{', content)
    data = json.loads(f"[{content}]")
    
    with open(r'c:\Users\MC\AppData\Local\Temp\audit_clean_output.txt', 'w', encoding='utf-8') as out:
        warns = [d for d in data if d.get('verdict') == 'WARN']
        fails = [d for d in data if d.get('verdict') == 'FAIL']
        passes = len(data) - len(warns) - len(fails)
        
        out.write(f"Total Scanned: {len(data)}\n")
        out.write(f"Pass: {passes}, Warn: {len(warns)}, Fail: {len(fails)}\n\n")
        
        for f in fails:
            out.write(f"\n[FAIL] {f['skill_name']}\n")
            for finding in f.get('findings', []):
                out.write(f"  - [{finding.get('severity')}] {finding.get('risk')} in {finding.get('file')} ({finding.get('pattern')})\n")
        for w in warns:
            out.write(f"\n[WARN] {w['skill_name']}\n")
            for finding in w.get('findings', []):
                out.write(f"  - [{finding.get('severity')}] {finding.get('risk')} in {finding.get('file')} ({finding.get('pattern')})\n")
    print("DONE writing output.")
except Exception as e:
    print(f"Error: {e}")
