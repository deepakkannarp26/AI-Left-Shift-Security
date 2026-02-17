name: Left Shift Security Scan

on:
  push:
    branches: ["main"]

jobs:
  security:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Setup Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.10"

    - name: Install Dependencies
      run: |
        pip install bandit semgrep openai

    - name: Run Bandit Scan
      run: |
        bandit -r src/ -f json -o bandit-report.json || true

    - name: Run Semgrep Scan
      run: |
        semgrep --config=auto src/ --json > semgrep-report.json || true

    - name: Run LLM Security Analyzer
      env:
        OPENAI_API_KEY: ${{ secrets.OPEN_AI_API_KEY }}
      run: |
        python llm_security_analyzer.py
