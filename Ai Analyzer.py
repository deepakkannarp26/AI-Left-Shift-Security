import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_bandit_with_ai():

    try:
        with open("bandit-report.json", "r") as f:
            bandit_data = json.load(f)

        issues = bandit_data.get("results", [])

        if not issues:
            print("## ✅ AI Security Review\nNo vulnerabilities found.")
            return

        prompt = f"""
You are a Senior Application Security Engineer.

Analyze the following Bandit SAST findings.
Identify:
- Real vulnerability?
- False positive?
- CWE reference
- Severity
- Secure fix

Return JSON only.

Bandit Findings:
{json.dumps(issues, indent=2)}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            messages=[
                {"role": "system", "content": "You are an expert security engineer."},
                {"role": "user", "content": prompt}
            ]
        )

        print(response.choices[0].message.content)

    except FileNotFoundError:
        print("Bandit report not found.")

if __name__ == "__main__":
    analyze_bandit_with_ai()
