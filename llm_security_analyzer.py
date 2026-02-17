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

    # Simulate AI classification if Bandit found issues
    if bandit_data.get("results"):
        vulnerabilities.append({
            "type": "Hardcoded Credential",
            "cwe": "CWE-798",
            "severity": "High",
            "confidence": "High",
            "explanation": "Hardcoded credentials detected in source code.",
            "secure_fix": "Use environment variables and secure password hashing."
        })

    # Simulate logic flaw detection
    if "os.system" in diff:
        vulnerabilities.append({
            "type": "Command Injection Risk",
            "cwe": "CWE-78",
            "severity": "Critical",
            "confidence": "High",
            "explanation": "Use of os.system may allow command injection.",
            "secure_fix": "Use subprocess with argument lists and validate inputs."
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

    # 🔥 Block pipeline on High or Critical
    for v in result.get("vulnerabilities", []):
        if v.get("severity", "").lower() in ["high", "critical"]:
            print("🚨 Blocking pipeline due to High/Critical vulnerability.")
            exit(1)
