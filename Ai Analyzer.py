import json

def analyze_bandit_report():
    try:
        with open("bandit-report.json", "r") as f:
            data = json.load(f)

        issues = data.get("results", [])

        if not issues:
            print("No vulnerabilities found.")
            return

        for issue in issues:
            print("\n--- Vulnerability Detected ---")
            print("File:", issue.get("filename"))
            print("Issue:", issue.get("issue_text"))
            print("Severity:", issue.get("issue_severity"))
            print("Confidence:", issue.get("issue_confidence"))
            print("AI Analysis: This may allow attackers to exploit the system.")
            print("Suggested Fix: Review this code and apply secure coding practices.")

    except FileNotFoundError:
        print("Bandit report not found.")

if __name__ == "__main__":
    analyze_bandit_report()
