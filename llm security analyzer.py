import os
import json
import subprocess
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_git_diff():
    result = subprocess.run(
        ["git", "diff", "origin/main...HEAD"],
        capture_output=True,
        text=True
    )
    return result.stdout

def analyze_security(diff):

    system_prompt = """
You are a Senior Application Security Engineer.

Follow OWASP Top 10 and CWE standards.
Avoid hallucinations.
If insufficient context, say so.

Return ONLY valid JSON:

{
  "vulnerabilities": [
    {
      "type": "",
      "cwe": "",
      "severity": "",
      "explanation": "",
      "secure_fix": ""
    }
  ]
}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Code Diff:\n{diff}"}
        ]
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    diff = get_git_diff()
    if not diff.strip():
        print("No changes detected.")
        exit(0)

    result = analyze_security(diff)
    print(result)
