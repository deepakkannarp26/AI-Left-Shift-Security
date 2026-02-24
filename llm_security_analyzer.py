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


def mock_ai_analysis(diff):

    vulnerabilities = []

    # Hardcoded credentials detection
    if 'password == "' in diff or 'username == "' in diff:
        vulnerabilities.append({
            "type": "Hardcoded Credential",
            "cwe": "CWE-798",
            "severity": "High",
            "confidence": 0.9,
            "explanation": "Hardcoded credentials detected.",
            "secure_fix": "Use environment variables."
        })

    # Command execution detection
    if "os.system(" in diff:
        vulnerabilities.append({
            "type": "Command Injection",
            "cwe": "CWE-78",
            "severity": "Critical",
            "confidence": 0.95,
            "explanation": "Unsafe system command execution.",
            "secure_fix": "Avoid os.system; validate inputs."
        })

    return {"vulnerabilities": vulnerabilities}


def calculate_risk(severity, confidence):

    weights = {
        "Low": 1,
        "Medium": 2,
        "High": 3,
        "Critical": 4
    }

    return weights.get(severity, 1) * confidence


if __name__ == "__main__":

    diff = get_git_diff()

    if not diff.strip():
        print("No changes detected.")
        exit(0)

    result = mock_ai_analysis(diff)

    print(json.dumps(result, indent=2))

    # Adaptive enforcement gate
    for v in result["vulnerabilities"]:
        risk = calculate_risk(v["severity"], v["confidence"])
        print(f"Risk Score: {risk}")

        if risk >= 3:
            print("🚨 Mock AI Security Gate BLOCKED deployment")
            exit(1)
