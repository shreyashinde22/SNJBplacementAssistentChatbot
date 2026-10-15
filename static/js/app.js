/**
 * SNJB Placement Cell Assistant — Frontend JavaScript Application
 * Manages chat interactions, markdown formatting, API communication, and UI state.
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const chatContainer = document.getElementById('chatContainer');
    const messagesLog = document.getElementById('messagesLog');
    const welcomeCard = document.getElementById('welcomeCard');
    const typingIndicator = document.getElementById('typingIndicator');
    const chatForm = document.getElementById('chatForm');
    const userMessageInput = document.getElementById('userMessage');
    const sendBtn = document.getElementById('sendBtn');
    const charCount = document.getElementById('charCount');
    const newChatBtn = document.getElementById('newChatBtn');
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const themeIcon = document.getElementById('themeIcon');
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const modelBadge = document.getElementById('modelBadge');
    
    // Status Card Elements
    const statusDot = document.getElementById('statusDot');
    const statusTitle = document.getElementById('statusTitle');
    const statusDetail = document.getElementById('statusDetail');
    const testApiBtn = document.getElementById('testApiBtn');
    const openUploadModalBtn = document.getElementById('openUploadModalBtn');

    // Modals
    const apiTestModal = document.getElementById('apiTestModal');
    const runApiTestBtn = document.getElementById('runApiTestBtn');
    const testResultBox = document.getElementById('testResultBox');
    const closeApiModalBtn = document.getElementById('closeApiModalBtn');
    const closeApiModalBtn2 = document.getElementById('closeApiModalBtn2');

    const uploadModal = document.getElementById('uploadModal');
    const uploadForm = document.getElementById('uploadForm');
    const docFileInput = document.getElementById('docFileInput');
    const uploadStatusBox = document.getElementById('uploadStatusBox');
    const closeUploadModalBtn = document.getElementById('closeUploadModalBtn');

    // Application State
    let chatHistory = [];
    let isProcessing = false;

    // --- 1. System Initialization & Health Check ---
    fetchHealthStatus();

    function fetchHealthStatus() {
        fetch('/api/health')
            .then(res => res.json())
            .then(data => {
                if (data.gemini_configured) {
                    statusDot.classList.add('online');
                    statusTitle.textContent = 'Gemini AI Active';
                    statusDetail.textContent = `Model: ${data.gemini_model} | FAQs: ${data.faq_count}`;
                    modelBadge.textContent = data.gemini_model;
                } else {
                    statusDot.classList.remove('online');
                    statusTitle.textContent = 'Offline KB Mode';
                    statusDetail.textContent = `GEMINI_API_KEY missing in .env | FAQs: ${data.faq_count}`;
                    modelBadge.textContent = 'Offline Knowledge Base';
                }
            })
            .catch(err => {
                console.error('Health check failed:', err);
                statusTitle.textContent = 'Server Connected';
                statusDetail.textContent = 'Check server console.';
            });
    }

    // --- 2. Input Handling & Textarea Auto-Resize ---
    userMessageInput.addEventListener('input', () => {
        const len = userMessageInput.value.length;
        charCount.textContent = `${len}/2000`;

        // Auto-expand rows
        userMessageInput.style.height = 'auto';
        userMessageInput.style.height = Math.min(userMessageInput.scrollHeight, 120) + 'px';
    });

    userMessageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });

    // --- 3. Chat Form Submission ---
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = userMessageInput.value.trim();
        if (!text || isProcessing) return;

        sendMessage(text);
    });

    function sendMessage(text) {
        isProcessing = true;
        userMessageInput.value = '';
        userMessageInput.style.height = 'auto';
        charCount.textContent = '0/2000';

        // Hide Welcome Card on first message
        if (welcomeCard.style.display !== 'none') {
            welcomeCard.style.display = 'none';
        }

        // Render User Message
        appendMessage('user', text);

        // Add to history
        chatHistory.push({ sender: 'user', text: text });

        // Show Typing Indicator
        showTyping(true);

        // Send to backend
        fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: text,
                history: chatHistory
            })
        })
        .then(res => res.json())
        .then(data => {
            showTyping(false);
            isProcessing = false;

            if (data.success) {
                appendMessage('assistant', data.reply, data.sources, data.is_verified, data.disclaimer);
                chatHistory.push({ sender: 'assistant', text: data.reply });
            } else {
                appendMessage('assistant', `⚠️ **Error:** ${data.error || 'Failed to generate answer.'}`);
            }
        })
        .catch(err => {
            showTyping(false);
            isProcessing = false;
            console.error('Chat error:', err);
            appendMessage('assistant', '⚠️ **Connection Error:** Could not reach the placement server. Please verify your connection.');
        });
    }

    // --- 4. Render Message Bubbles with Markdown ---
    function appendMessage(sender, rawText, sources = [], isVerified = true, disclaimer = '') {
        const row = document.createElement('div');
        row.className = `message-row ${sender}`;

        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.innerHTML = sender === 'user' ? '👤' : '🤖';

        const content = document.createElement('div');
        content.className = 'message-content';

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.innerHTML = parseMarkdown(rawText);

        content.appendChild(bubble);

        // Metadata footer for assistant messages
        if (sender === 'assistant') {
            const meta = document.createElement('div');
            meta.className = 'message-meta';

            if (isVerified) {
                meta.innerHTML += `<span class="verified-badge">✓ Verified SNJB Info</span>`;
            }

            if (sources && sources.length > 0) {
                sources.forEach(src => {
                    meta.innerHTML += `<span class="source-tag">📄 ${src}</span>`;
                });
            }

            if (disclaimer) {
                meta.innerHTML += `<span style="font-size:0.7rem; color:var(--text-muted);">• ${disclaimer}</span>`;
            }

            content.appendChild(meta);
        }

        row.appendChild(avatar);
        row.appendChild(content);
        messagesLog.appendChild(row);

        // Scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function showTyping(show) {
        typingIndicator.style.display = show ? 'flex' : 'none';
        if (show) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }

    // Simple Markdown Parser
    function parseMarkdown(text) {
        if (!text) return '';

        let html = text
            // Code block
            .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
            // Inline code
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            // Headings
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            // Bold
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Italic
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            // Bullet list items
            .replace(/^\- (.*$)/gim, '<li>$1</li>')
            .replace(/^\* (.*$)/gim, '<li>$1</li>');

        // Wrap consecutive <li> in <ul>
        html = html.replace(/(<li>[\s\S]*?<\/li>)/g, '<ul>$1</ul>');
        // Fix duplicate <ul> tags
        html = html.replace(/<\/ul>\s*<ul>/g, '');

        // Paragraph breaks
        const paragraphs = html.split(/\n\n+/);
        return paragraphs.map(p => {
            if (p.startsWith('<h') || p.startsWith('<ul>') || p.startsWith('<pre')) {
                return p;
            }
            return `<p>${p.replace(/\n/g, '<br>')}</p>`;
        }).join('');
    }

    // --- 5. Interactive Cards & Chips ---
    document.querySelectorAll('.suggestion-card, .faq-chip').forEach(el => {
        el.addEventListener('click', () => {
            const query = el.getAttribute('data-query');
            if (query) {
                sendMessage(query);
                if (window.innerWidth <= 768) {
                    sidebar.classList.remove('open');
                }
            }
        });
    });

    // --- 6. New Chat Reset ---
    newChatBtn.addEventListener('click', () => {
        chatHistory = [];
        messagesLog.innerHTML = '';
        welcomeCard.style.display = 'block';
        userMessageInput.value = '';
    });

    // --- 7. Theme Toggle (Light/Dark) ---
    const savedTheme = localStorage.getItem('snjb_theme') || 'light';
    setTheme(savedTheme);

    themeToggleBtn.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    });

    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('snjb_theme', theme);
        themeIcon.textContent = theme === 'dark' ? '☀️' : '🌙';
    }

    // --- 8. Mobile Sidebar Toggle ---
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });

    // --- 9. Gemini API Test Modal ---
    testApiBtn.addEventListener('click', () => {
        apiTestModal.classList.add('active');
    });

    [closeApiModalBtn, closeApiModalBtn2].forEach(btn => {
        btn.addEventListener('click', () => {
            apiTestModal.classList.remove('active');
        });
    });

    runApiTestBtn.addEventListener('click', () => {
        testResultBox.innerHTML = '<i>Contacting Google Gemini API...</i>';
        fetch('/api/test-gemini', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    testResultBox.innerHTML = `<span style="color:var(--accent-green)">✅ <strong>Success!</strong> ${data.message}</span>`;
                } else {
                    testResultBox.innerHTML = `<span style="color:var(--accent-red)">❌ <strong>Test Failed:</strong> ${data.message}</span>`;
                }
                fetchHealthStatus();
            })
            .catch(err => {
                testResultBox.innerHTML = `<span style="color:var(--accent-red)">❌ <strong>Network Error:</strong> ${err.message}</span>`;
            });
    });

    // --- 10. Document Upload Modal ---
    openUploadModalBtn.addEventListener('click', () => {
        uploadModal.classList.add('active');
    });

    closeUploadModalBtn.addEventListener('click', () => {
        uploadModal.classList.remove('active');
    });

    uploadForm.addEventListener('submit', (e) => {
        e.preventDefault();
        if (!docFileInput.files || docFileInput.files.length === 0) return;

        const formData = new FormData();
        formData.append('file', docFileInput.files[0]);

        uploadStatusBox.innerHTML = '<i>Uploading & indexing document...</i>';

        fetch('/api/upload-doc', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                uploadStatusBox.innerHTML = `<span style="color:var(--accent-green)">✅ ${data.message}</span>`;
                docFileInput.value = '';
                fetchHealthStatus();
            } else {
                uploadStatusBox.innerHTML = `<span style="color:var(--accent-red)">❌ Error: ${data.error}</span>`;
            }
        })
        .catch(err => {
            uploadStatusBox.innerHTML = `<span style="color:var(--accent-red)">❌ Upload failed: ${err.message}</span>`;
        });
    });
});
