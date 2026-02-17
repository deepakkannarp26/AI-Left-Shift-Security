import os
import json
import subprocess
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MAX_DIFF_LENGTH = 6000  # prevent token overflow


def get_git_diff():
    result = subprocess.run(
        ["git", "diff", "origin/main...HEAD"],
        capture_output=True,
        text=True
    )
    diff = result.stdout

    # Trim large diffs
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
Your responsibilities:
1. Determine whether each finding is a TRUE vulnerability or a FALSE POSITIVE.
2. Map the issue to correct CWE ID.
3. Assign severity: Low, Medium, High, Critical.
4. Provide a short technical explanation.
5. Suggest a secure code-level fix.

Rules:
- Be strict in classification.
- If evidence is weak, mark as false positive.
- Follow OWASP Top 10 and CWE standards.
- Do not hallucinate missing context.

Return ONLY valid JSON in this format:

{
  "vulnerabilities": [
    {
      "type": "",
      "cwe": "",
      "severity": "",
      "is_false_positive": false,
      "confidence": "Low/Medium/High",
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

    # Validate JSON
    try:
        parsed = json.loads(content)
        return json.dumps(parsed, indent=2)
    except json.JSONDecodeError:
        return json.dumps({
            "error": "Invalid JSON returned from LLM",
            "raw_output": content
        })


if __name__ == "__main__":
    diff = get_git_diff()

    if not diff.strip():
        print(json.dumps({"message": "No changes detected."}))
        exit(0)

    bandit_data = load_json_file("bandit-report.json")
    semgrep_data = load_json_file("semgrep-report.json")

    result = analyze_security(diff, bandit_data, semgrep_data)
    print(result)
