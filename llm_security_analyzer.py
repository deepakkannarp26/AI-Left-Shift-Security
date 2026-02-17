import os
import json
import subprocess
from openai import OpenAI

# Read API key from environment
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("API key not found in environment!")

client = OpenAI(api_key=api_key)


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


def analyze_security(diff, bandit_data, semgrep_data):

    system_prompt = """
You are a Senior Application Security Engineer.

Analyze the code diff and SAST findings.
Return ONLY valid JSON in this format:

{
  "vulnerabilities": [
    {
      "type": "",
      "cwe": "",
      "severity": "",
      "explanation": ""
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
    return json.loads(content)


if __name__ == "__main__":

    diff = get_git_diff()

    if not diff.strip():
        print("No changes detected.")
        exit(0)

    bandit_data = load_json_file("bandit-report.json")
    semgrep_data = load_json_file("semgrep-report.json")

    result = analyze_security(diff, bandit_data, semgrep_data)

    print(json.dumps(result, indent=2))

    # 🔥 Severity blocking
    for v in result.get("vulnerabilities", []):
        if v.get("severity", "").lower() in ["high", "critical"]:
            print("🚨 Blocking pipeline due to High/Critical vulnerability.")
            exit(1)
