import os
import json
import subprocess
from openai import OpenAI

# 🔥 Read the exact secret name
api_key = os.getenv("OPEN_AI_API_KEY")

if not api_key:
    raise ValueError("API Key not found in environment!")

client = OpenAI(api_key=api_key)

MAX_DIFF_LENGTH = 6000


def get_git_diff():
    result = subprocess.run(
        ["git", "diff", "HEAD~1"],
        capture_output=True,
        text=True
    )

    diff = result.stdout

    if len(diff) > MAX_DIFF_LENGTH:
        diff = diff[:MAX_DIFF_LENGTH] + "\n\n[TRUNCATED]"

    return diff


def load_json_file(file_path):
    if not os.path.exists(file_path):
        return {}

    with open(file_path, "r") as f:
        return json.load(f)


def analyze_security(diff, bandit_data, semgrep_data):

    system_prompt = """
You are a Senior Application Security Engineer performing AI-driven vulnerability triage.

Return ONLY valid JSON:

{
  "vulnerabilities": [
    {
      "type": "",
      "cwe": "",
      "severity": "",
      "is_false_positive": false,
      "confidence": "",
      "explanation": "",
      "secure_fix": ""
    }
  ]
}
"""

    user_prompt = f"""
Code Diff:
{diff}

Bandit Findings:
{json.dumps(bandit_data, indent=2)}

Semgrep Findings:
{json.dumps(semgrep_data, indent=2)}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    content = response.choices[0].message.content

    try:
        parsed = json.loads(content)
        return parsed
    except json.JSONDecodeError:
        return {
            "error": "Invalid JSON returned",
            "raw_output": content
        }


if __name__ == "__main__":

    diff = get_git_diff()

    if not diff.strip():
        print("No changes detected.")
        exit(0)

    bandit_data = load_json_file("bandit-report.json")
    semgrep_data = load_json_file("semgrep-report.json")

    result = analyze_security(diff, bandit_data, semgrep_data)

    print(json.dumps(result, indent=2))

    vulnerabilities = result.get("vulnerabilities", [])

    for v in vulnerabilities:
        severity = v.get("severity", "").lower()

        if severity in ["critical", "high"]:
            print("\n🚨 Blocking pipeline due to High/Critical vulnerability.")
            exit(1)
