import os
import json
import subprocess


def get_git_diff():
    result = subprocess.run(
        ["git", "diff", "HEAD~1"],
        capture_output=True,
        text=True
    )
    return result.stdout


def load_json_file(file_path):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r") as f:
        return json.load(f)


def mock_ai_analysis(diff, bandit_data, semgrep_data):

    vulnerabilities = []

    # 🔴 Detect Hardcoded Credentials (ONLY string literal comparison)
    if 'password == "' in diff or 'username == "' in diff:
        vulnerabilities.append({
            "type": "Hardcoded Credential",
            "cwe": "CWE-798",
            "severity": "High",
            "confidence": "High",
            "explanation": "Hardcoded credentials detected in authentication logic.",
            "secure_fix": "Use environment variables (os.getenv) or secure database-backed authentication."
        })

    # 🔴 Detect Command Injection Risk
    if "os.system(" in diff:
        vulnerabilities.append({
            "type": "Command Injection",
            "cwe": "CWE-78",
            "severity": "Critical",
            "confidence": "High",
            "explanation": "Use of os.system may allow command injection if user input is not sanitized.",
            "secure_fix": "Use subprocess with argument lists and validate all external inputs."
        })

    return {"vulnerabilities": vulnerabilities}


if __name__ == "__main__":

    diff = get_git_diff()

    if not diff.strip():
        print("No changes detected.")
        exit(0)

    bandit_data = load_json_file("bandit-report.json")
    semgrep_data = load_json_file("semgrep-report.json")

    result = mock_ai_analysis(diff, bandit_data, semgrep_data)

    print(json.dumps(result, indent=2))

    # 🚨 Block pipeline only for High or Critical
    for v in result.get("vulnerabilities", []):
        if v.get("severity", "").lower() in ["high", "critical"]:
            print("🚨 Blocking pipeline due to High/Critical vulnerability.")
            exit(1)
