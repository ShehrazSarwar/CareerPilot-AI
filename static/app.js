/* ═════════════════════════════════════════════════════════════════════════════
   CAREERPILOT AI FRONTEND CONTROLLER (app.js)
   ═════════════════════════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
    // ── DOM ELEMENTS ────────────────────────────────────────────────────────
    const themeToggleBtn = document.getElementById('theme-toggle');
    const roleSelect = document.getElementById('role-select');
    const customRoleGroup = document.getElementById('custom-role-group');
    const customRoleInput = document.getElementById('custom-role-input');
    const apiKeyInput = document.getElementById('api-key-input');
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const fileNameDisplay = document.getElementById('file-name-display');
    const analyzeBtn = document.getElementById('analyze-btn');
    
    const welcomePlaceholder = document.getElementById('welcome-placeholder');
    const loadingSpinner = document.getElementById('loading-spinner');
    const dashboardResults = document.getElementById('dashboard-results');
    
    // Dashboard Stats & Info
    const scoreFg = document.getElementById('score-fg');
    const scoreNum = document.getElementById('score-num');
    const scoreBadge = document.getElementById('score-badge');
    const resultRoleTitle = document.getElementById('result-role-title');
    const pillStrengths = document.getElementById('pill-strengths');
    const pillGaps = document.getElementById('pill-gaps');
    const pillProjects = document.getElementById('pill-projects');
    const downloadPdfBtn = document.getElementById('download-pdf-btn');
    
    // Tabs Navigation
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    // Tab 1: Overview
    const summaryText = document.getElementById('summary-text');
    const strengthsList = document.getElementById('strengths-list');
    const weaknessesList = document.getElementById('weaknesses-list');
    
    // Tab 2: Skill Gaps
    const gapsChips = document.getElementById('gaps-chips');
    const gapsList = document.getElementById('gaps-list');
    
    // Tab 3: Roadmap
    const roadmap30List = document.getElementById('roadmap-30-list');
    const roadmap60List = document.getElementById('roadmap-60-list');
    const roadmap90List = document.getElementById('roadmap-90-list');
    
    // Tab 4: Projects
    const projectsGrid = document.getElementById('projects-grid');
    
    // Tab 5: Certifications
    const certsGrid = document.getElementById('certs-grid');
    
    // Tab 6: Interview Prep
    const interviewList = document.getElementById('interview-list');
    
    // Tab 7: Job Matcher
    const jobDescTextarea = document.getElementById('job-desc-textarea');
    const calculateMatchBtn = document.getElementById('calculate-match-btn');
    const matcherResults = document.getElementById('matcher-results');
    const matcherLoading = document.getElementById('matcher-loading');
    const matchPercentBox = document.getElementById('match-percent-box');
    const matchStatusPill = document.getElementById('match-status-pill');
    const matchSummaryText = document.getElementById('match-summary-text');
    const matchKeywordsList = document.getElementById('match-keywords-list');
    const missingKeywordsList = document.getElementById('missing-keywords-list');
    const matchTipsList = document.getElementById('match-tips-list');

    // ── STATE VARIABLES ─────────────────────────────────────────────────────
    let selectedFile = null;
    let cachedSession = null; // Stores { cv_text, target_role, analysis }

    // ── THEME INITIALIZATION & SWITCHER ─────────────────────────────────────
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeUI(savedTheme);

    themeToggleBtn.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeUI(newTheme);
    });

    function updateThemeUI(theme) {
        if (theme === 'dark') {
            themeToggleBtn.innerHTML = '<i class="fa-solid fa-moon"></i> Dark Mode';
        } else {
            themeToggleBtn.innerHTML = '<i class="fa-solid fa-sun"></i> Light Mode';
        }
    }

    // ── PERSISTED API KEY RESTORATION ───────────────────────────────────────
    const savedApiKey = localStorage.getItem('gemini_api_key');
    if (savedApiKey) {
        apiKeyInput.value = savedApiKey;
    }

    // ── FORM INTERACTION (ROLE DROPDOWN) ────────────────────────────────────
    roleSelect.addEventListener('change', () => {
        if (roleSelect.value === 'Custom Role...') {
            customRoleGroup.style.display = 'block';
            customRoleInput.focus();
        } else {
            customRoleGroup.style.display = 'none';
        }
    });

    // ── DRAG & DROP RESUME UPLOAD ───────────────────────────────────────────
    dropzone.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        handleFileSelect(e.target.files[0]);
    });

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    function handleFileSelect(file) {
        if (!file) return;
        const validExtensions = ['.pdf', '.docx'];
        const fileExt = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
        
        if (!validExtensions.includes(fileExt)) {
            alert('Unsupported file format! Please upload a PDF or DOCX resume.');
            return;
        }
        
        selectedFile = file;
        fileNameDisplay.textContent = file.name;
        fileNameDisplay.style.color = 'var(--text-color)';
    }

    // ── TAB SWITCHING ───────────────────────────────────────────────────────
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');
            
            // Remove active class from buttons and panes
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));
            
            // Activate current
            btn.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
        });
    });

    // ── ANIMATE COUNTER UTILITY ─────────────────────────────────────────────
    function animateCounter(element, start, end, durationMs) {
        let startTime = null;
        
        function updateCounter(currentTime) {
            if (!startTime) startTime = currentTime;
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / durationMs, 1);
            
            // Easing out quadratic
            const easeProgress = progress * (2 - progress);
            const currentVal = Math.floor(start + easeProgress * (end - start));
            
            element.textContent = currentVal;
            
            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            } else {
                element.textContent = end;
            }
        }
        
        requestAnimationFrame(updateCounter);
    }

    // ── API TRIGGER: ANALYZE RESUME ─────────────────────────────────────────
    analyzeBtn.addEventListener('click', async () => {
        if (!selectedFile) {
            alert('Please select or drag-and-drop a resume first!');
            return;
        }

        const apiKey = apiKeyInput.value.trim();
        if (apiKey) {
            localStorage.setItem('gemini_api_key', apiKey);
        } else {
            localStorage.removeItem('gemini_api_key');
        }

        let targetRole = roleSelect.value;
        if (targetRole === 'Custom Role...') {
            targetRole = customRoleInput.value.trim();
            if (!targetRole) {
                alert('Please type in your custom target role!');
                customRoleInput.focus();
                return;
            }
        }

        // Prepare request
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('target_role', targetRole);
        if (apiKey) {
            formData.append('custom_api_key', apiKey);
        }

        // Update UI state to Loading
        welcomePlaceholder.style.display = 'none';
        dashboardResults.style.display = 'none';
        loadingSpinner.style.display = 'flex';
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Analyzing...';

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                let errMsg = 'Failed to complete resume analysis.';
                try {
                    const errData = await response.json();
                    if (errData && errData.detail) {
                        if (Array.isArray(errData.detail)) {
                            errMsg = errData.detail.map(d => {
                                const locStr = d.loc ? d.loc.join('.') : '';
                                return `${locStr ? locStr + ': ' : ''}${d.msg}`;
                            }).join('; ');
                        } else if (typeof errData.detail === 'string') {
                            errMsg = errData.detail;
                        }
                    }
                } catch (jsonErr) {}
                throw new Error(errMsg);
            }

            const data = await response.json();
            cachedSession = data; // Structure: { cv_text, target_role, analysis }
            
            // Render dashboard view
            renderDashboard(data.analysis, data.target_role);

            // Transition UI
            loadingSpinner.style.display = 'none';
            dashboardResults.style.display = 'block';
        } catch (error) {
            console.error(error);
            alert(`Error: ${error.message}`);
            loadingSpinner.style.display = 'none';
            welcomePlaceholder.style.display = 'flex';
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '<i class="fa-solid fa-rocket"></i> Analyze My Career';
        }
    });

    // ── DASHBOARD RENDERING ENGINE ──────────────────────────────────────────
    function renderDashboard(analysis, role) {
        // 1. Title & Pill Counts
        resultRoleTitle.textContent = role;
        
        const numStrengths = analysis.strengths ? analysis.strengths.length : 0;
        const numGaps = analysis.skill_gaps ? analysis.skill_gaps.length : 0;
        const numProjects = analysis.project_ideas ? analysis.project_ideas.length : 0;
        
        pillStrengths.textContent = `${numStrengths} Strengths`;
        pillGaps.textContent = `${numGaps} Skill Gaps`;
        pillProjects.textContent = `${numProjects} Projects`;

        // 2. Animate Score & Score Ring
        const score = analysis.career_score || 0;
        
        // svg circle circumference is 390
        const circumference = 390;
        const offset = circumference - (score / 100) * circumference;
        scoreFg.style.strokeDashoffset = offset;
        
        // Update Ring Stroke Color dynamically based on score
        let scoreColorVar = '--primary-color';
        let scoreBadgeClass = 'badge-yellow';
        let scoreBadgeText = 'Developing Competency';
        
        if (score >= 80) {
            scoreColorVar = '--green-text';
            scoreBadgeClass = 'badge-green';
            scoreBadgeText = 'Job Ready (FAANG)';
        } else if (score < 60) {
            scoreColorVar = '--red-text';
            scoreBadgeClass = 'badge-red';
            scoreBadgeText = 'Needs Up-skilling';
        }
        
        scoreFg.style.stroke = `var(${scoreColorVar})`;
        scoreBadge.className = `score-badge ${scoreBadgeClass}`;
        scoreBadge.textContent = scoreBadgeText;
        
        animateCounter(scoreNum, 0, score, 1500);

        // 3. Tab 1: Overview Summary & SW Lists
        summaryText.textContent = analysis.summary || 'Summary unavailable.';
        
        strengthsList.innerHTML = '';
        if (analysis.strengths && analysis.strengths.length > 0) {
            analysis.strengths.forEach(s => {
                const item = document.createElement('div');
                item.className = 'sw-item sw-item-strength';
                item.innerHTML = `<i class="fa-solid fa-check-circle" style="color: var(--green-text)"></i> <span>${s}</span>`;
                strengthsList.appendChild(item);
            });
        } else {
            strengthsList.innerHTML = '<p class="text-subdued">No specific strengths detected.</p>';
        }

        weaknessesList.innerHTML = '';
        if (analysis.weaknesses && analysis.weaknesses.length > 0) {
            analysis.weaknesses.forEach(w => {
                const item = document.createElement('div');
                item.className = 'sw-item sw-item-weakness';
                item.innerHTML = `<i class="fa-solid fa-triangle-exclamation" style="color: var(--red-text)"></i> <span>${w}</span>`;
                weaknessesList.appendChild(item);
            });
        } else {
            weaknessesList.innerHTML = '<p class="text-subdued">No major weaknesses detected.</p>';
        }

        // 4. Tab 2: Skill Gaps
        gapsChips.innerHTML = '';
        gapsList.innerHTML = '';
        if (analysis.skill_gaps && analysis.skill_gaps.length > 0) {
            analysis.skill_gaps.forEach(gap => {
                // Chip
                const chip = document.createElement('span');
                chip.className = 'chip-item';
                chip.innerHTML = `<i class="fa-solid fa-xmark" style="color: var(--red-text)"></i> ${gap}`;
                gapsChips.appendChild(chip);
                
                // Detailed breakdown list
                const row = document.createElement('div');
                row.className = 'gap-row';
                row.textContent = `Missing requirement: ${gap}. Learn this framework/technique to align with the core requirements of this role.`;
                gapsList.appendChild(row);
            });
        } else {
            gapsChips.innerHTML = '<p class="text-subdued">No major gaps identified!</p>';
            gapsList.innerHTML = '<p class="text-subdued">Your profile fully covers standard competencies for this role.</p>';
        }

        // 5. Tab 3: Timeline Roadmap
        roadmap30List.innerHTML = '';
        roadmap60List.innerHTML = '';
        roadmap90List.innerHTML = '';
        
        const rm = analysis.roadmap_30_60_90 || {};
        const steps30 = rm['30_day'] || [];
        const steps60 = rm['60_day'] || [];
        const steps90 = rm['90_day'] || [];
        
        if (steps30.length > 0) {
            steps30.forEach(step => {
                const item = document.createElement('div');
                item.className = 'roadmap-step';
                item.textContent = step;
                roadmap30List.appendChild(item);
            });
        } else {
            roadmap30List.innerHTML = '<p class="text-subdued">No steps scheduled.</p>';
        }

        if (steps60.length > 0) {
            steps60.forEach(step => {
                const item = document.createElement('div');
                item.className = 'roadmap-step';
                item.textContent = step;
                roadmap60List.appendChild(item);
            });
        } else {
            roadmap60List.innerHTML = '<p class="text-subdued">No steps scheduled.</p>';
        }

        if (steps90.length > 0) {
            steps90.forEach(step => {
                const item = document.createElement('div');
                item.className = 'roadmap-step';
                item.textContent = step;
                roadmap90List.appendChild(item);
            });
        } else {
            roadmap90List.innerHTML = '<p class="text-subdued">No steps scheduled.</p>';
        }

        // 6. Tab 4: Projects Grid
        projectsGrid.innerHTML = '';
        if (analysis.project_ideas && analysis.project_ideas.length > 0) {
            analysis.project_ideas.forEach(proj => {
                const card = document.createElement('div');
                card.className = 'project-card card';
                
                const techs = proj.technologies ? proj.technologies.join(', ') : 'General Stack';
                const difficulty = proj.difficulty || 'Intermediate';
                
                card.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.50rem;">
                        <h3 class="project-title">${proj.title}</h3>
                        <span class="project-difficulty">${difficulty}</span>
                    </div>
                    <p class="project-desc">${proj.description}</p>
                    <span class="project-tech"><i class="fa-solid fa-code"></i> Stack: ${techs}</span>
                `;
                projectsGrid.appendChild(card);
            });
        } else {
            projectsGrid.innerHTML = '<p class="text-subdued">No projects recommended.</p>';
        }

        // 7. Tab 5: Certifications Grid
        certsGrid.innerHTML = '';
        if (analysis.certifications && analysis.certifications.length > 0) {
            analysis.certifications.forEach(cert => {
                const card = document.createElement('div');
                card.className = 'cert-card card';
                
                card.innerHTML = `
                    <h3 class="cert-title">${cert.name}</h3>
                    <span class="cert-provider"><i class="fa-solid fa-award"></i> Provided by: ${cert.provider}</span>
                    <p class="cert-reason">${cert.reason}</p>
                `;
                certsGrid.appendChild(card);
            });
        } else {
            certsGrid.innerHTML = '<p class="text-subdued">No certifications recommended.</p>';
        }

        // 8. Tab 6: Interview Prep (Accordion List)
        interviewList.innerHTML = '';
        if (analysis.interview_prep && analysis.interview_prep.length > 0) {
            analysis.interview_prep.forEach((qa, idx) => {
                const item = document.createElement('div');
                item.className = 'accordion-item';
                
                item.innerHTML = `
                    <div class="accordion-header" data-index="${idx}">
                        <span>Q${idx + 1}: ${qa.question}</span>
                        <i class="fa-solid fa-chevron-down accordion-icon"></i>
                    </div>
                    <div class="accordion-body" id="acc-body-${idx}">
                        <div class="accordion-content">
                            <strong>Suggested Response strategy:</strong><br/>
                            ${qa.answer}
                        </div>
                    </div>
                `;
                
                // Bind toggle interaction directly
                const header = item.querySelector('.accordion-header');
                header.addEventListener('click', () => {
                    const isOpen = item.classList.contains('open');
                    
                    // Close all accordion items
                    document.querySelectorAll('.accordion-item').forEach(acc => {
                        acc.classList.remove('open');
                        acc.querySelector('.accordion-body').style.maxHeight = null;
                    });
                    
                    if (!isOpen) {
                        item.classList.add('open');
                        const body = item.querySelector('.accordion-body');
                        const content = item.querySelector('.accordion-content');
                        body.style.maxHeight = `${content.scrollHeight + 50}px`;
                    }
                });
                
                interviewList.appendChild(item);
            });
        } else {
            interviewList.innerHTML = '<p class="text-subdued">No interview preparation loops available.</p>';
        }

        // Reset Job Matcher Results Section
        matcherResults.style.display = 'none';
        jobDescTextarea.value = '';

        // Refresh/Reset Microsoft Calendar Sync state for the new analysis
        if (typeof msGraphToken !== 'undefined' && msGraphToken) {
            const events = buildCalendarEvents(analysis, role);
            renderCalendarPreview(events);
            if (calSyncBtn) {
                calSyncBtn.disabled = false;
                calSyncBtn.innerHTML = '<i class="fa-solid fa-calendar-plus"></i> Create Calendar Events';
                calSyncBtn.style.background = '';
            }
        } else {
            if (calPreview) {
                calPreview.style.display = 'none';
            }
            if (calSyncBtn) {
                calSyncBtn.disabled = false;
                calSyncBtn.innerHTML = '<i class="fa-solid fa-calendar-plus"></i> Create Calendar Events';
                calSyncBtn.style.background = '';
            }
        }
    }

    // ── API TRIGGER: JOB MATCH COMPATIBILITY ────────────────────────────────
    calculateMatchBtn.addEventListener('click', async () => {
        if (!cachedSession) {
            alert('Please run the main CV analysis before calculating match compatibility!');
            return;
        }

        const jobDesc = jobDescTextarea.value.trim();
        if (!jobDesc) {
            alert('Please paste the job description or requirements detail first!');
            jobDescTextarea.focus();
            return;
        }

        const apiKey = apiKeyInput.value.trim();

        // Update UI to Loading
        matcherResults.style.display = 'none';
        matcherLoading.style.display = 'flex';
        calculateMatchBtn.disabled = true;
        calculateMatchBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Analyzing Alignment...';

        try {
            const response = await fetch('/api/match', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    cv_text: cachedSession.cv_text,
                    job_description: jobDesc,
                    custom_api_key: apiKey || null
                })
            });

            if (!response.ok) {
                let errMsg = 'Failed to analyze job alignment.';
                try {
                    const errData = await response.json();
                    if (errData && errData.detail) {
                        if (Array.isArray(errData.detail)) {
                            errMsg = errData.detail.map(d => {
                                const locStr = d.loc ? d.loc.join('.') : '';
                                return `${locStr ? locStr + ': ' : ''}${d.msg}`;
                            }).join('; ');
                        } else if (typeof errData.detail === 'string') {
                            errMsg = errData.detail;
                        }
                    }
                } catch (jsonErr) {}
                throw new Error(errMsg);
            }

            const matchData = await response.json(); // Structure: { match_percentage, summary, matched_skills, missing_skills, resume_tailoring_tips }

            // Render Matcher UI
            matchPercentBox.textContent = `${matchData.match_percentage}%`;
            matchSummaryText.textContent = matchData.summary;
            
            // Compatibility status categorization
            let matchStatusText = 'Low Compatibility';
            let matchStatusColor = 'var(--red-text)';
            
            if (matchData.match_percentage >= 80) {
                matchStatusText = 'Excellent Match';
                matchStatusColor = 'var(--green-text)';
            } else if (matchData.match_percentage >= 55) {
                matchStatusText = 'Moderate Compatibility';
                matchStatusColor = '#eab308'; // yellow
            }
            
            matchStatusPill.textContent = matchStatusText;
            matchStatusPill.style.color = matchStatusColor;

            // Matched keywords chips
            matchKeywordsList.innerHTML = '';
            if (matchData.matched_skills && matchData.matched_skills.length > 0) {
                matchData.matched_skills.forEach(skill => {
                    const chip = document.createElement('span');
                    chip.className = 'chip-item';
                    chip.innerHTML = `<i class="fa-solid fa-check-circle" style="color: var(--green-text)"></i> ${skill}`;
                    matchKeywordsList.appendChild(chip);
                });
            } else {
                matchKeywordsList.innerHTML = '<p class="text-subdued">No direct keyword overlaps detected.</p>';
            }

            // Missing keywords chips
            missingKeywordsList.innerHTML = '';
            if (matchData.missing_skills && matchData.missing_skills.length > 0) {
                matchData.missing_skills.forEach(skill => {
                    const chip = document.createElement('span');
                    chip.className = 'chip-item';
                    chip.innerHTML = `<i class="fa-solid fa-times-circle" style="color: var(--red-text)"></i> ${skill}`;
                    missingKeywordsList.appendChild(chip);
                });
            } else {
                missingKeywordsList.innerHTML = '<p class="text-subdued">No critical keywords missing!</p>';
            }

            // Tailoring tips list
            matchTipsList.innerHTML = '';
            if (matchData.resume_tailoring_tips && matchData.resume_tailoring_tips.length > 0) {
                matchData.resume_tailoring_tips.forEach(tip => {
                    const row = document.createElement('div');
                    row.className = 'tip-row';
                    row.textContent = tip;
                    matchTipsList.appendChild(row);
                });
            } else {
                matchTipsList.innerHTML = '<p class="text-subdued">No tailoring tips needed.</p>';
            }

            // Transition UI
            matcherLoading.style.display = 'none';
            matcherResults.style.display = 'block';
        } catch (error) {
            console.error(error);
            alert(`Job Matching Error: ${error.message}`);
            matcherLoading.style.display = 'none';
        } finally {
            calculateMatchBtn.disabled = false;
            calculateMatchBtn.innerHTML = '<i class="fa-solid fa-circle-nodes"></i> Calculate Compatibility Score';
        }
    });

    // ── API TRIGGER: DOWNLOAD PDF REPORT ────────────────────────────────────
    downloadPdfBtn.addEventListener('click', async () => {
        if (!cachedSession) {
            alert('Please generate the career analysis before downloading the report!');
            return;
        }

        // Disable button while processing
        downloadPdfBtn.disabled = true;
        const origContent = downloadPdfBtn.innerHTML;
        downloadPdfBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generating PDF...';

        try {
            const response = await fetch('/api/generate-pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    analysis: cachedSession.analysis,
                    target_role: cachedSession.target_role
                })
            });

            if (!response.ok) {
                let errMsg = 'Failed to compile report PDF.';
                try {
                    const errData = await response.json();
                    if (errData && errData.detail) {
                        if (Array.isArray(errData.detail)) {
                            errMsg = errData.detail.map(d => {
                                const locStr = d.loc ? d.loc.join('.') : '';
                                return `${locStr ? locStr + ': ' : ''}${d.msg}`;
                            }).join('; ');
                        } else if (typeof errData.detail === 'string') {
                            errMsg = errData.detail;
                        }
                    }
                } catch (jsonErr) {}
                throw new Error(errMsg);
            }

            // Read as Blob
            const blob = await response.blob();
            
            // Extract filename from response header if available
            let filename = `CareerPilot_${cachedSession.target_role.replace(/\s+/g, '_')}.pdf`;
            const disposition = response.headers.get('Content-Disposition');
            if (disposition && disposition.indexOf('attachment') !== -1) {
                const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                const matches = filenameRegex.exec(disposition);
                if (matches != null && matches[1]) {
                    filename = matches[1].replace(/['"]/g, '');
                }
            }

            // Create client-side file link download trigger
            const blobUrl = URL.createObjectURL(blob);
            const downloadLink = document.createElement('a');
            downloadLink.href = blobUrl;
            downloadLink.download = filename;
            
            document.body.appendChild(downloadLink);
            downloadLink.click();
            
            // Cleanup after a short delay to allow Chrome's async download manager to ingest the stream
            setTimeout(() => {
                document.body.removeChild(downloadLink);
                URL.revokeObjectURL(blobUrl);
            }, 500);
        } catch (error) {
            console.error(error);
            alert(`PDF Generation Error: ${error.message}`);
        } finally {
            downloadPdfBtn.disabled = false;
            downloadPdfBtn.innerHTML = origContent;
        }
    });

    // ── MICROSOFT GRAPH CALENDAR SYNC (Work IQ) ─────────────────────────────

    const MSAL_CONFIG = {
        auth: {
            clientId: 'beaee821-3c46-4a01-915f-f9bd9e4dcdbb', // Replace with your Azure App Registration Client ID
            authority: 'https://login.microsoftonline.com/common',
            redirectUri: window.location.origin
        },
        cache: { cacheLocation: 'sessionStorage' }
    };
    const GRAPH_SCOPES = ['Calendars.ReadWrite', 'User.Read'];

    let msalInstance = null;
    let msGraphToken = null;
    let msUserName = null;

    const calConnectBtn = document.getElementById('cal-connect-btn');
    const calSyncBtn    = document.getElementById('cal-sync-btn');
    const calMsStatus   = document.getElementById('cal-ms-status');
    const calPreview    = document.getElementById('cal-preview');
    const calEventsList = document.getElementById('cal-events-list');

    // Build flat list of calendar events from all three roadmap phases
    function buildCalendarEvents(analysis, role) {
        const events = [];
        const rm = analysis.roadmap_30_60_90 || {};
        const today = new Date();
        today.setHours(9, 0, 0, 0);

        const phases = [
            { key: '30_day', label: 'Days 1\u201330 \u00b7 Foundation',        offsetWeeks: 0  },
            { key: '60_day', label: 'Days 31\u201360 \u00b7 Build & Apply',     offsetWeeks: 5  },
            { key: '90_day', label: 'Days 61\u201390 \u00b7 Portfolio & Apply', offsetWeeks: 10 }
        ];

        phases.forEach(({ key, label, offsetWeeks }) => {
            (rm[key] || []).forEach((step, idx) => {
                const start = new Date(today);
                start.setDate(today.getDate() + (offsetWeeks * 7) + (idx * 7));
                const end = new Date(start);
                end.setHours(10, 0, 0, 0);
                const shortTitle = step.length > 70 ? step.substring(0, 70) + '\u2026' : step;
                events.push({
                    subject: 'CareerPilot: ' + shortTitle,
                    body: 'CareerPilot AI \u2013 ' + role + ' Career Roadmap\n\nPhase: ' + label + '\n\nTask:\n' + step + '\n\nAuto-created by CareerPilot AI Work IQ Calendar Sync.',
                    startDate: start,
                    endDate: end,
                    phase: label,
                    fullText: step
                });
            });
        });
        return events;
    }

    // Render event rows in the preview panel
    function renderCalendarPreview(events) {
        calEventsList.innerHTML = '';
        const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
        events.forEach(ev => {
            const row = document.createElement('div');
            row.className = 'cal-event-row pending';
            row.dataset.eventSubject = ev.subject;
            row.innerHTML =
                '<div class="cal-event-date">' +
                    '<span class="cal-event-day">' + ev.startDate.getDate() + '</span>' +
                    '<span class="cal-event-month">' + months[ev.startDate.getMonth()] + '</span>' +
                '</div>' +
                '<div class="cal-event-body">' +
                    '<div class="cal-event-title">' + ev.fullText + '</div>' +
                    '<div class="cal-event-phase">' + ev.phase + '</div>' +
                '</div>' +
                '<div class="cal-event-status" style="color:var(--text-subdued)">' +
                    '<i class="fa-regular fa-clock"></i> Pending' +
                '</div>';
            calEventsList.appendChild(row);
        });
        calPreview.style.display = 'block';
    }

    // Mark a row green after successful Graph API creation
    function markEventSynced(subject) {
        calEventsList.querySelectorAll('.cal-event-row').forEach(row => {
            if (row.dataset.eventSubject === subject) {
                row.classList.remove('pending');
                row.classList.add('synced');
                row.querySelector('.cal-event-status').innerHTML =
                    '<i class="fa-solid fa-circle-check" style="color:#22c55e"></i> <span style="color:#22c55e">Synced</span>';
            }
        });
    }

    // POST one event to Microsoft Graph Calendar
    async function createGraphCalendarEvent(token, ev) {
        const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
        const res = await fetch('https://graph.microsoft.com/v1.0/me/events', {
            method: 'POST',
            headers: { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' },
            body: JSON.stringify({
                subject: ev.subject,
                body: { contentType: 'text', content: ev.body },
                start: { dateTime: ev.startDate.toISOString(), timeZone: tz },
                end:   { dateTime: ev.endDate.toISOString(),   timeZone: tz },
                categories: ['CareerPilot AI']
            })
        });
        if (!res.ok) {
            const e = await res.json();
            throw new Error(e.error ? e.error.message : 'Graph API error');
        }
        return res.json();
    }

    // CONNECT: launch Microsoft OAuth popup via MSAL
    calConnectBtn.addEventListener('click', async () => {
        if (MSAL_CONFIG.auth.clientId === 'YOUR_CLIENT_ID') {
            alert(
                '\u2699\ufe0f  One-time Azure Setup Required\n\n' +
                '1. Go to: portal.azure.com\n' +
                '2. Azure Active Directory \u2192 App registrations \u2192 New registration\n' +
                '3. Name: CareerPilot AI\n' +
                '4. Supported accounts: "Accounts in any organizational directory and personal Microsoft accounts"\n' +
                '5. Redirect URI type: Single-page application (SPA)\n' +
                '   URI: http://127.0.0.1:8000\n' +
                '6. Click Register \u2192 copy the Application (client) ID\n' +
                '7. Open static/app.js \u2192 find YOUR_CLIENT_ID \u2192 paste your ID\n\n' +
                'Then click Connect Microsoft Account again!'
            );
            return;
        }
        calConnectBtn.disabled = true;
        calConnectBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Connecting...';
        try {
            msalInstance = new msal.PublicClientApplication(MSAL_CONFIG);
            await msalInstance.initialize();
            const auth = await msalInstance.loginPopup({ scopes: GRAPH_SCOPES });
            msGraphToken = auth.accessToken;
            msUserName   = auth.account.name || auth.account.username;

            calMsStatus.innerHTML = '<span style="color:var(--green-text)"><i class="fa-solid fa-circle-check"></i> ' + msUserName + '</span>';
            calConnectBtn.style.display = 'none';
            calSyncBtn.style.display    = 'inline-flex';

            // If analysis already done, show event preview immediately
            if (cachedSession) {
                renderCalendarPreview(buildCalendarEvents(cachedSession.analysis, cachedSession.target_role));
            }
        } catch (err) {
            console.error(err);
            calMsStatus.innerHTML = '<span style="color:var(--red-text)"><i class="fa-solid fa-circle-xmark"></i> Login failed: ' + err.message + '</span>';
            calConnectBtn.disabled = false;
            calConnectBtn.innerHTML = '<i class="fa-brands fa-microsoft"></i> Connect Microsoft Account';
        }
    });

    // SYNC: create all roadmap tasks as calendar events
    calSyncBtn.addEventListener('click', async () => {
        if (!cachedSession) { alert('Run the CV analysis first!'); return; }
        if (!msGraphToken)  { alert('Connect your Microsoft account first!'); return; }

        const events = buildCalendarEvents(cachedSession.analysis, cachedSession.target_role);
        if (calPreview.style.display === 'none') renderCalendarPreview(events);

        calSyncBtn.disabled = true;
        calSyncBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Creating Events...';

        let ok = 0, fail = 0;
        for (const ev of events) {
            try {
                await createGraphCalendarEvent(msGraphToken, ev);
                markEventSynced(ev.subject);
                ok++;
                await new Promise(r => setTimeout(r, 300)); // avoid Graph rate limit
            } catch (err) {
                console.error('Event failed:', ev.subject, err);
                fail++;
            }
        }

        calSyncBtn.disabled = false;
        calSyncBtn.innerHTML = '<i class="fa-solid fa-calendar-check"></i> ' + ok + ' Events Created!';
        calSyncBtn.style.background = 'linear-gradient(135deg,#16a34a,#22c55e)';
        calMsStatus.innerHTML = '<span style="color:var(--green-text)"><i class="fa-solid fa-circle-check"></i> ' + msUserName + ' \u00b7 ' + ok + ' events added to Outlook</span>';
        if (fail > 0) alert('\u26a0\ufe0f ' + fail + ' event(s) failed. Check the browser console for details.');
    });

});
