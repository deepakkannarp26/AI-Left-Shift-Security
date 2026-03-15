document.addEventListener('DOMContentLoaded', () => {
    // We will attempt to fetch from the local sample_data first for stability,
    // or from the root directory if the real scan json is present.
    const REPORT_URLS = [
        '../ai-report.json',      // Actual Gemini AI report
        '../mock-ai-report.json', // Legacy mock report
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
        const s = severity.toLowerCase();
        if (s === 'critical') return 'sev-critical';
        if (s === 'high') return 'sev-high';
        if (s === 'low') return 'sev-low';
        return 'sev-medium';
    }

    // Number counting animation utility
    function animateValue(obj, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            obj.innerHTML = Math.floor(progress * (end - start) + start);
            if (progress < 1) {
                window.requestAnimationFrame(step);
            } else {
                obj.innerHTML = end; // Ensure exact final value
            }
        };
        window.requestAnimationFrame(step);
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
            document.querySelector('.stat-safe .kpi-value').textContent = '1,402'; // Static for demo
            return;
        }

        const vulns = data.vulnerabilities;
        animateValue(vulnBadgeCount, 0, vulns.length, 1000);
        // Animate dummy scanned files for effect
        animateValue(document.querySelector('.stat-safe .kpi-value'), 0, 1402, 1500);

        // Render Cards
        vulns.forEach((v, index) => {
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
                <button class="vuln-toggle">View AI Remediation</button>
                <div class="vuln-body">
                    <p>${v.explanation || 'No explanation provided by AI.'}</p>
                    <div class="vuln-fix">
                        <strong>AI Recommended Fix:</strong><br/>
                        ${v.secure_fix || 'Review code manually.'}
                    </div>
                </div>
            `;

            // Add toggle event listener
            const toggleBtn = card.querySelector('.vuln-toggle');
            toggleBtn.addEventListener('click', () => {
                const isExpanded = card.classList.contains('expanded');
                // Close all other cards
                document.querySelectorAll('.vuln-card').forEach(c => c.classList.remove('expanded'));
                document.querySelectorAll('.vuln-toggle').forEach(btn => btn.textContent = 'View AI Remediation');

                if (!isExpanded) {
                    card.classList.add('expanded');
                    toggleBtn.textContent = 'Hide Remediation';
                }
            });

            // Stagger animation delay
            const delay = index * 0.15;
            card.style.animation = `fadeUp 0.5s ease-out ${delay}s forwards`;

            vulnList.appendChild(card);
        });

        vulnList.style.display = 'flex';
        renderSeverityBreakdown(vulns);
    }

    function renderSeverityBreakdown(vulns) {
        const breakdownSection = document.getElementById('severity-breakdown');
        breakdownSection.style.display = 'block';

        const counts = { critical: 0, high: 0, medium: 0, low: 0 };
        vulns.forEach(v => {
            const sev = (v.severity || 'medium').toLowerCase();
            if (counts[sev] !== undefined) counts[sev]++;
            else counts.medium++;
        });

        const total = vulns.length;
        document.getElementById('breakdown-total').textContent = total;

        // Update counts
        document.getElementById('count-critical').textContent = counts.critical;
        document.getElementById('count-high').textContent = counts.high;
        document.getElementById('count-medium').textContent = counts.medium;
        document.getElementById('count-low').textContent = counts.low;

        // Update bars (with a tiny delay for animation)
        setTimeout(() => {
            document.getElementById('bar-critical').style.width = `${(counts.critical / total) * 100}%`;
            document.getElementById('bar-high').style.width = `${(counts.high / total) * 100}%`;
            document.getElementById('bar-medium').style.width = `${(counts.medium / total) * 100}%`;
            document.getElementById('bar-low').style.width = `${(counts.low / total) * 100}%`;
        }, 100);
    }

    // Simulate network delay for effect
    setTimeout(() => {
        fetchReport()
            .then(data => renderVulnerabilities(data))
            .catch(error => {
                console.error("Dashboard Error:", error);
                document.getElementById('loader').innerHTML = `
                <div style="color: #ff003c; font-size: 2.5rem; margin-bottom: 1rem; filter: drop-shadow(0 0 10px rgba(255,0,60,0.5));">⚠️</div>
                    <p style="color: #ff003c; font-family: 'Outfit'; font-size: 1.2rem;">Telemetry Connection Lost</p>
                    <p style="font-size: 0.85rem; margin-top: 0.5rem; opacity: 0.7;">Ensure the local metrics server is online.</p>
            `;
            });
    }, 2000); // Slightly longer delay to show off new loader
});
