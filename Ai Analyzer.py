import os
import json
import re

def load_json_file(file_path):
    if not os.path.exists(file_path):
        return {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return {}

def calculate_risk(severity, confidence):
    weights = {
        "Low": 1,
        "Medium": 2,
        "High": 3,
        "Critical": 4
    }
    return weights.get(severity, 1) * confidence

def map_bandit_severity(sev):
    mapping = {
        "LOW": "Low",
        "MEDIUM": "Medium",
        "HIGH": "High"
    }
    return mapping.get(sev.upper(), "Medium")

def map_semgrep_severity(sev):
    mapping = {
        "INFO": "Low",
        "WARNING": "Medium",
        "ERROR": "High"
    }
    return mapping.get(sev.upper(), "Medium")

def extract_cwe_from_list(cwe_list):
    if not cwe_list:
        return "Unknown"
    if isinstance(cwe_list, list):
        # usually looks like "CWE-79: Improper Neutralization..."
        match = re.search(r'(CWE-\d+)', str(cwe_list[0]))
        if match:
            return match.group(1)
        return str(cwe_list[0])
    return str(cwe_list)

def generate_secure_fix(cwe, issue_text):
    cwe_upper = str(cwe).upper()
    if "CWE-78" in cwe_upper or "B605" in issue_text or "B607" in issue_text:
        return "Avoid os.system or shell=True. Use subprocess modules with validated inputs and avoid shell execution."
    if "CWE-259" in cwe_upper or "CWE-798" in cwe_upper or "PASSWORD" in issue_text.upper():
        return "Use environment variables or a secure vault to store and retrieve credentials instead of hardcoding."
    if "CWE-94" in cwe_upper or "DEBUG=TRUE" in issue_text.upper():
        return "Ensure debug mode is disabled (debug=False) in production environments to prevent arbitrary code execution."
    if "CWE-89" in cwe_upper or "SQL" in issue_text.upper():
        return "Use parameterized queries or ORMs to prevent SQL injection."
    if "CWE-79" in cwe_upper or "XSS" in issue_text.upper():
        return "Sanitize and encode all user inputs before rendering them in the UI."
    
    return "Review the code architecture to enforce input validation, secure defaults, and principle of least privilege."

def process_reports():
    vulnerabilities = []

    # 1. Process Bandit Results
    bandit_data = load_json_file("bandit-report.json")
    for issue in bandit_data.get("results", []):
        # Synthetic intelligence mapping
        issue_text = issue.get('issue_text', 'Unknown issue')
        cwe_id = issue.get('issue_cwe', {}).get('id', 'Unknown')
        cwe_str = f"CWE-{cwe_id}" if cwe_id != 'Unknown' else "Unknown"
        severity = map_bandit_severity(issue.get('issue_severity', 'MEDIUM'))
        
        # Synthetic confidence score based on the tool's confidence
        conf_map = {"LOW": 0.4, "MEDIUM": 0.7, "HIGH": 0.95}
        confidence = conf_map.get(issue.get('issue_confidence', 'HIGH').upper(), 0.8)
        
        # Promote severity if it's a known dangerous CWE
        if "CWE-78" in cwe_str or "CWE-94" in cwe_str or "CWE-89" in cwe_str:
            severity = "Critical"
            
        secure_fix = generate_secure_fix(cwe_str, issue_text)
        
        vulnerabilities.append({
            "type": issue.get('test_name', 'Security Vulnerability').replace('_', ' ').title(),
            "cwe": cwe_str,
            "severity": severity,
            "confidence": confidence,
            "explanation": issue_text,
            "secure_fix": secure_fix,
            "file": issue.get('filename', ''),
            "line": issue.get('line_number', '')
        })

    # 2. Process Semgrep Results
    semgrep_data = load_json_file("semgrep-report.json")
    for issue in semgrep_data.get("results", []):
        extra = issue.get("extra", {})
        message = extra.get("message", "Unknown issue")
        severity_raw = extra.get("severity", "WARNING")
        severity = map_semgrep_severity(severity_raw)
        
        metadata = extra.get("metadata", {})
        cwe_list = metadata.get("cwe", [])
        cwe_str = extract_cwe_from_list(cwe_list)
        
        confidence = 0.85 # Synthetic confidence for semgrep
        
        if "CWE-78" in cwe_str or "CWE-94" in cwe_str or "CWE-89" in cwe_str:
            severity = "Critical"
            
        secure_fix = generate_secure_fix(cwe_str, message)
        
        vulnerabilities.append({
            "type": issue.get("check_id", "Semgrep Finding").split('.')[-1].replace('_', ' ').title(),
            "cwe": cwe_str,
            "severity": severity,
            "confidence": confidence,
            "explanation": message,
            "secure_fix": secure_fix,
            "file": issue.get("path", ""),
            "line": issue.get("start", {}).get("line", "")
        })

    return {"vulnerabilities": vulnerabilities}

def generate_markdown_summary(result):
    total_vulns = len(result["vulnerabilities"])
    md = f"## 🛡️ local AI Security Engine Analysis Report\n\n"
    
    if total_vulns == 0:
        md += "✅ **No high-risk vulnerabilities detected.**\n\n"
        md += "> The pipeline scanned the latest changes and found no issues.\n"
        return md
        
    md += f"⚠️ **Found {total_vulns} potential security issue(s)**\n\n"
    md += "| Type | Severity | CWE | Explanation | Fix | Location |\n"
    md += "|---|---|---|---|---|---|\n"
    
    for v in result["vulnerabilities"]:
        loc = f"`{v.get('file', '')}:{v.get('line', '')}`" if v.get('file') else "N/A"
        md += f"| **{v['type']}** | {v['severity']} | {v['cwe']} | {v['explanation']} | `{v['secure_fix']}` | {loc} |\n"
        
    md += "\n> Note: This report was generated by the Local Rule-Based Component acting as the AI Analyzer.\n"
    return md

def generate_pr_comment(result):
    total_vulns = len(result["vulnerabilities"])
    if total_vulns == 0:
        return ""
        
    md = f"## 🤖 Auto-Remediation Suggestions\n\n"
    md += f"I have analyzed your code and found **{total_vulns}** potential security issue(s). Here are the suggested fixes:\n\n"
    
    for i, v in enumerate(result["vulnerabilities"], 1):
        loc = f" in `{v.get('file', '')}` line {v.get('line', '')}" if v.get('file') else ""
        md += f"### {i}. **{v['type']}** ({v['severity']} Severity){loc}\n"
        md += f"- **Explanation**: {v['explanation']}\n"
        md += f"- **CWE**: {v['cwe']}\n"
        md += f"- **Suggested Fix**:\n"
        md += f"  > `{v['secure_fix']}`\n\n"
        
    return md

if __name__ == "__main__":
    result = process_reports()

    # Save for dashboard artifact
    with open("ai-report.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(json.dumps(result, indent=2))

    # Write to GitHub Step Summary
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        try:
            with open(summary_file, "a", encoding="utf-8") as f:
                f.write(generate_markdown_summary(result))
        except Exception as e:
            print(f"Could not write to step summary: {e}")

    # Generate PR Comment File
    pr_comment_content = generate_pr_comment(result)
    if pr_comment_content:
        with open("pr_comment.md", "w", encoding="utf-8") as f:
            f.write(pr_comment_content)

    # Adaptive enforcement gate
    blocked = False
    for v in result["vulnerabilities"]:
        risk = calculate_risk(v["severity"], v["confidence"])
        print(f"Evaluating Risk Score for {v['type']}: {risk:.2f}")

        if risk >= 3:
            blocked = True
            
    if blocked:
        print("\n[BLOCKED] Local Security Gate BLOCKED deployment due to high-risk issues")
        exit(1)
    else:
        print("\n[PASSED] Security Gates Passed")
        exit(0)
