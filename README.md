# 🛡️ AI-Left-Shift-Security

**AI-Left-Shift-Security** is an intelligent, automated DevSecOps pipeline designed to identify, analyze, and remediate security vulnerabilities early in the software development lifecycle (SDLC). By combining traditional Static Application Security Testing (SAST) tools with advanced Generative AI analysis, this project ensures robust and real-time security reviews for every commit and pull request.

## ✨ Key Features

- **Automated Security Scanning**: Automatically triggers on pushes and pull requests via GitHub Actions.
- **Multi-layered Analysis**: Uses **Bandit** (for Python-specific security issues) and **Semgrep** (for comprehensive polyglot static analysis).
- **AI-Powered Triaging & Remediation**: Leverages Google Gemini to analyze code diffs, filter false positives, map vulnerabilities to specific CWEs, and generate context-aware remediation codes directly in GitHub PR comments.
- **Interactive Security Dashboard**: A modern, glassmorphic UI web dashboard to visualize security metrics, risks, and AI suggestions dynamically.
- **Deployment Enforcement**: Employs an adaptive risk-scoring algorithm (based on Severity and Confidence) to block high-risk deployments automatically.

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- A Google Gemini API Key
- GitHub Repository (for CI/CD workflow testing)

### Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/AI-Left-Shift-Security.git
   cd AI-Left-Shift-Security
   ```

2. **Install dependencies:**
   ```bash
   pip install bandit semgrep google-generativeai
   ```

3. **Set your API Key:**
   Export your Gemini API Key as an environment variable:
   ```bash
   # Windows (PowerShell)
   $env:GEMINI_API_KEY="your-api-key-here"
   
   # Linux/macOS
   export GEMINI_API_KEY="your-api-key-here"
   ```

4. **Launch the Dashboard:**
   To spin up the local server and open the interactive security dashboard, run:
   ```bash
   python dashboard/start_dashboard.py
   ```

## 🧠 How the AI Analyzer Works

The primary script `llm_security_analyzer.py` is invoked inside the CI/CD pipeline. 
1. It reads the code changes (`git diff`).
2. The code changes are sent to the Gemini LLM with a highly specific DevSecOps prompt.
3. The LLM returns a structured JSON containing vulnerabilities (`type`, `CWE`, `severity`, `confidence`, and `secure_fix`).
4. If the computed risk threshold (severity * confidence) exceeds the limit, the pipeline fails, blocking the insecure code from reaching production.

## 📋 Project Structure

- `src/` - The main application code (to be scanned).
- `dashboard/` - Frontend assets (`index.html`, `styles.css`, `script.js`) and the server launcher.
- `.github/workflows/security.yml` - The GitHub Actions automation script.
- `llm_security_analyzer.py` - AI integration for deep scanning diffs.
- `Ai Analyzer.py` - Secondary local rule-based aggregator.
- `temp_diff.txt` / `*-report.json` - Intermediary artifacts generated during scans.

## 🤝 Contribution

Contributions are welcome! Please feel free to open an issue or submit a Pull Request if you'd like to add new SAST tools or improve the Dashboard UI.
