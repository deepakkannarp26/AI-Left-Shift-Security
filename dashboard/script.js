document.addEventListener('DOMContentLoaded', () => {
    // We will attempt to fetch from the local sample_data first for stability,
    // or from the root directory if the real scan json is present.
    const REPORT_URLS = [
        '../mock-ai-report.json', // Real run location if served from root
        'sample_data/mock-ai-report.json' // Fallback sample data
    ];

    async function fetchReport() {
        for (const url of REPORT_URLS) {
            try {
                const response = await fetch(url);
                if (response.ok) {
                    return await response.json();
                }
            } catch (error) {
                console.warn(`Could not fetch from ${url}, trying next...`);
            }
        }
        throw new Error("Could not load AI Security Report data.");
    }

    function getSeverityClass(severity) {
        if (!severity) return 'sev-medium';
        return severity.toLowerCase() === 'high' || severity.toLowerCase() === 'critical' 
            ? 'sev-high' 
            : 'sev-medium';
    }

    function renderVulnerabilities(data) {
        const loader = document.getElementById('loader');
        const vulnList = document.getElementById('vuln-list');
        const noIssues = document.getElementById('no-issues');
        const vulnBadgeCount = document.getElementById('vuln-count');
        const kpiVulns = document.getElementById('kpi-vulns');

        // Hide loader
        loader.style.display = 'none';

        if (!data || !data.vulnerabilities || data.vulnerabilities.length === 0) {
            // Show Success State
            noIssues.style.display = 'block';
            kpiVulns.classList.remove('stat-danger');
            kpiVulns.classList.add('stat-safe');
            vulnBadgeCount.textContent = '0';
            return;
        }

        const vulns = data.vulnerabilities;
        vulnBadgeCount.textContent = vulns.length;

        // Render Cards
        vulns.forEach(v => {
            const sevClass = getSeverityClass(v.severity);
            const severityLevel = v.severity || 'Medium';
            const cardLevel = severityLevel.toLowerCase(); // for border left color

            const card = document.createElement('div');
            card.className = `vuln-card ${cardLevel}`;
            
            card.innerHTML = `
                <div class="vuln-header">
                    <div>
                        <h4 class="vuln-title">${v.type || 'Unknown Vulnerability'}</h4>
                        <span class="vuln-cwe">${v.cwe || 'CWE-Unknown'}</span>
                    </div>
                    <span class="vuln-severity ${sevClass}">${severityLevel} Risk</span>
                </div>
                <div class="vuln-body">
                    <p>${v.explanation || 'No explanation provided by AI.'}</p>
                    <div class="vuln-fix">
                        <strong>AI Recommended Fix:</strong><br/>
                        ${v.secure_fix || 'Review code manually.'}
                    </div>
                </div>
            `;
            vulnList.appendChild(card);
        });

        vulnList.style.display = 'flex';
    }

    // Simulate network delay for effect
    setTimeout(() => {
        fetchReport()
            .then(data => renderVulnerabilities(data))
            .catch(error => {
                console.error("Dashboard Error:", error);
                document.getElementById('loader').innerHTML = `
                    <div style="color: #ef4444; font-size: 2rem; margin-bottom: 1rem;">⚠️</div>
                    <p style="color: #ef4444;">Failed to load security telemetry.</p>
                    <p style="font-size: 0.8rem; margin-top: 0.5rem; opacity: 0.7;">Make sure you are running the dashboard via a local server.</p>
                `;
            });
    }, 1500);
});
