
document.addEventListener('DOMContentLoaded', () => {
    // ... (Get element references: initialView, resultView, etc.) ...
    const claimForm = document.getElementById('claim-form');
    const claimInput = document.getElementById('claim-input');
    const suggestions = document.getElementById('suggestions');
    const newSearchButton = document.getElementById('new-search-button');
    const initialView = document.getElementById('initial-view');
    const resultView = document.getElementById('result-view');
    const copyPostButton = document.getElementById('copy-post-button');

    // --- Event Listeners ---
    claimForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const claim = claimInput.value.trim();
        if (claim) startFactCheck(claim);
    });

    suggestions.addEventListener('click', (e) => {
        if (e.target.classList.contains('suggestion-chip')) {
            const claim = e.target.textContent;
            claimInput.value = claim;
            startFactCheck(claim);
        }
    });

    newSearchButton.addEventListener('click', resetUI);
    copyPostButton.addEventListener('click', copyPostToClipboard);

    // --- Core Functions ---
    async function startFactCheck(claim) {
        initialView.classList.add('hidden');
        resultView.classList.remove('hidden');
        document.getElementById('claim-display').textContent = `"${claim}"`;
        resetResultView();

        try {
            const response = await fetch('/api/analyze-claim', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ claim }),
            });
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n\n');
                buffer = lines.pop();

                for (const line of lines) {
                    if (line.startsWith('data:')) {
                        const jsonString = line.substring(5).trim();
                        if (jsonString) handleStreamEvent(JSON.parse(jsonString));
                    }
                }
            }
        } catch (error) {
            console.error('Error starting fact-check:', error);
            addProgressStep('error', { stepId: 'error', title: 'Connection Error' });
        }
    }

    function handleStreamEvent(event) {
        const postTextEl = document.getElementById('post-text');
        switch (event.event) {
            case 'progress':
                addProgressStep('in-progress', { stepId: event.stepId, title: event.data });
                break;
            case 'progress_update':
                updateProgressStep(event.stepId, event.data);
                break;
            case 'token':
                postTextEl.textContent += event.data;
                break;
            case 'final_result':
                displayFinalResult(event.data);
                break;
            case 'end':
                markAllStepsComplete();
                postTextEl.classList.add('streaming-ended'); // Stop cursor blinking
                break;
            case 'error':
                addProgressStep('error', { stepId: 'error', title: 'An Error Occurred', details: event.data });
                break;
        }
    }

    // --- UI Manipulation Functions ---

    function addProgressStep(status, data) {
        const stepsContainer = document.getElementById('progress-steps');
        markPreviousStepComplete();

        const step = document.createElement('div');
        step.className = 'progress-step';
        step.dataset.stepId = data.stepId; // Use data attribute to identify the step

        const iconMap = {
            'analyzing': 'fa-regular fa-comment-dots', 'searching': 'fa-solid fa-magnifying-glass',
            'analyzing_evidence': 'fa-solid fa-balance-scale', 'writing_post': 'fa-solid fa-pen-to-square',
            'error': 'fa-solid fa-exclamation-triangle'
        };
        const iconClass = iconMap[data.stepId] || 'fa-solid fa-question';

        step.innerHTML = `
            <div class="progress-icon ${status}">
                <i class="fas ${status === 'in-progress' ? 'fa-spinner' : iconClass}"></i>
            </div>
            <div class="progress-text">
                <h3>${data.title}</h3>
                <p>${data.details || ''}</p>
            </div>
        `;
        stepsContainer.appendChild(step);
    }
    
    function updateProgressStep(stepId, newTitle) {
        const step = document.querySelector(`.progress-step[data-step-id="${stepId}"]`);
        if (step) {
            step.querySelector('h3').textContent = newTitle;
        }
    }
    
    function markPreviousStepComplete() {
        const steps = document.querySelectorAll('.progress-step');
        if (steps.length > 0) {
            const lastStep = steps[steps.length - 1];
            const lastIcon = lastStep.querySelector('.progress-icon');
            if (lastIcon.classList.contains('in-progress')) {
                lastIcon.classList.remove('in-progress');
                lastIcon.classList.add('completed');
                lastIcon.innerHTML = '<i class="fas fa-check"></i>';
            }
        }
    }
    
    function markAllStepsComplete() {
        markPreviousStepComplete(); // Mark the very last step
    }

    
    function displayFinalResult(data) {
        const verdictContainer = document.getElementById('verdict-container');
        const verdict = data.verdict;
        
        let citationsHTML = '<h4>Sources:</h4><ul>';
        verdict.citations.forEach(url => {
            citationsHTML += `<li><a href="${url}" target="_blank" rel="noopener noreferrer">${new URL(url).hostname}</a></li>`;
        });
        citationsHTML += '</ul>';

        verdictContainer.innerHTML = `
            <h3>Verdict</h3>
            <div class="verdict-header">
                <span class="verdict-badge ${verdict.verdict}">${verdict.verdict}</span>
                <span class="confidence-score">Confidence: ${(verdict.confidence_score * 100).toFixed(0)}%</span>
            </div>
            <p id="verdict-rationale">${verdict.rationale}</p>
            <div id="verdict-citations">${citationsHTML}</div>
        `;

        document.getElementById('post-text').textContent = data.post;
        document.getElementById('final-output-container').classList.remove('hidden');
    }

    function resetResultView() {
        document.getElementById('progress-steps').innerHTML = '';
        document.getElementById('final-output-container').classList.add('hidden');
        document.getElementById('post-text').classList.remove('streaming-ended');
    }

    function resetUI() {
        resultView.classList.add('hidden');
        initialView.classList.remove('hidden');
        claimInput.value = '';
        resetResultView();
    }
    
    function copyPostToClipboard() {
        const postText = document.getElementById('post-text').textContent;
        navigator.clipboard.writeText(postText).then(() => {
            const button = document.getElementById('copy-post-button');
            const originalContent = button.innerHTML;
            button.innerHTML = '<i class="fas fa-check"></i> <span>Copied!</span>';
            setTimeout(() => {
                button.innerHTML = originalContent;
            }, 2000);
        });
    }
});