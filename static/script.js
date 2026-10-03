document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('start-btn');
    const terminal = document.getElementById('terminal');
    const statusBadge = document.getElementById('status-badge');
    
    let eventSource = null;

    function appendLog(text, type = '') {
        const line = document.createElement('div');
        line.className = `log-line ${type}`;
        
        if(text.includes('Error') || text.includes('failed') || text.includes('Koi number nahi mila')) {
            line.className += ' error';
        } else if (text.includes('STEP') || text.includes('FINAL SUMMARY')) {
            line.className += ' highlight';
            text = '\n' + text;
        } else if (text.includes('LINK →') || text.includes('activation_url_found')) {
            line.className += ' success';
        }
        
        line.textContent = text;
        terminal.appendChild(line);
        terminal.scrollTop = terminal.scrollHeight;
    }

    startBtn.addEventListener('click', () => {
        if(eventSource) {
            return;
        }

        startBtn.disabled = true;
        startBtn.querySelector('.btn-text').textContent = 'SCANNING IN PROGRESS...';
        statusBadge.textContent = 'Scanning';
        statusBadge.className = 'status-badge running';
        
        terminal.innerHTML = '';
        appendLog('Initializing system...', 'system');
        appendLog('Establishing connection to background process...', 'system');

        eventSource = new EventSource('/run');

        eventSource.onmessage = (event) => {
            if (event.data === '[PROCESS_COMPLETED]') {
                finishScan();
            } else {
                appendLog(event.data);
            }
        };

        eventSource.onerror = (error) => {
            console.error('EventSource failed:', error);
            appendLog('Connection to process lost or process terminated.', 'error');
            finishScan();
        };
    });

    function finishScan() {
        if(eventSource) {
            eventSource.close();
            eventSource = null;
        }
        startBtn.disabled = false;
        startBtn.querySelector('.btn-text').textContent = 'INITIALIZE SCAN';
        statusBadge.textContent = 'Completed';
        statusBadge.className = 'status-badge';
        appendLog('\n--- Process Completed ---', 'system');
    }
});
