// ===== State Management =====
const state = {
    ws: null,
    mediaRecorder: null,
    audioChunks: [],
    isRecording: false,
    isConnected: false
};


const wakeSound = new Audio('./sounds/ding.mp3');
wakeSound.volume = 0.6; // adjust if needed


// ===== DOM Elements =====
const elements = {
    statusDot: document.getElementById('statusDot'),
    statusText: document.getElementById('statusText'),
    micButton: document.getElementById('micButton'),
    micStatus: document.getElementById('micStatus'),
    textInput: document.getElementById('textInput'),
    sendButton: document.getElementById('sendButton'),
    chatContainer: document.getElementById('chatContainer'),
    dataSection: document.getElementById('dataSection'),
    thinkingIndicator: document.getElementById('thinkingIndicator'),
    audioPlayer: document.getElementById('audioPlayer'),
    clearChat: document.getElementById('clearChat'),
    voiceVisualizer: document.getElementById('voiceVisualizer')
};

// ===== WebSocket Connection =====
function connectWebSocket() {
    state.ws = new WebSocket('ws://localhost:8765');

    state.ws.onopen = handleConnect;
    state.ws.onmessage = handleMessage;
    state.ws.onerror = handleError;
    state.ws.onclose = handleDisconnect;
}

function handleConnect() {
    console.log('✅ Connected to AI Voice Assistant');
    state.isConnected = true;
    updateStatus('connected', 'Connected');
    enableControls(true);
    showNotification('Connected to ARIA', 'success');
}

function handleMessage(event) {
    try {
        const data = JSON.parse(event.data);
        
        switch(data.type) {
            case 'transcription':
                handleTranscription(data.text);
                break;
            case 'response':
                handleResponse(data.data);
                break;
            case 'audio_response':
                playAudioResponse(data.audio);
                break;
            case 'reminder':
                handleReminder(data.data);
                break;
            case 'error':
                handleErrorMessage(data.message);
                break;
        }
    } catch (error) {
        console.error('Error parsing message:', error);
    }
}

function handleError(error) {
    console.error('❌ WebSocket error:', error);
    updateStatus('disconnected', 'Connection error');
    showNotification('Connection error occurred', 'error');
}

function handleDisconnect() {
    console.log('🔌 Disconnected from server');
    state.isConnected = false;
    updateStatus('disconnected', 'Disconnected');
    enableControls(false);
    
    // Attempt reconnection after 3 seconds
    setTimeout(() => {
        if (!state.isConnected) {
            showNotification('Reconnecting...', 'info');
            connectWebSocket();
        }
    }, 3000);
}

// ===== Status Management =====
function updateStatus(status, text) {
    elements.statusDot.className = `status-dot ${status}`;
    elements.statusText.textContent = text;
}

function enableControls(enabled) {
    elements.micButton.disabled = !enabled;
    elements.textInput.disabled = !enabled;
    elements.sendButton.disabled = !enabled;
}

// ===== Message Handlers =====
function handleTranscription(text) {
    addMessage(text, 'user');
    setThinking(true);
}

function handleResponse(response) {
    setThinking(false);
    addMessage(response.message, 'assistant', response.function_called);
    
    if (response.function_results) {
        response.function_results.forEach(result => {
            if (result.result.data) {
                displayData(result.function_name, result.result.data);
            }
        });
    }
}

function handleReminder(data) {
    addMessage(data.message, 'assistant');
    showNotification(data.reminder.text, 'info', '⏰ Reminder');
}

function handleErrorMessage(message) {
    setThinking(false);
    addMessage(`Error: ${message}`, 'assistant');
    showNotification(message, 'error');
}

// ===== Voice Recording =====
async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: {
                sampleRate: 16000,
                channelCount: 1,
                echoCancellation: true,
                noiseSuppression: true
            }
        });

        state.mediaRecorder = new MediaRecorder(stream);
        state.audioChunks = [];

        state.mediaRecorder.ondataavailable = (event) => {
            state.audioChunks.push(event.data);
        };

        state.mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(state.audioChunks, { type: 'audio/webm' });
            const reader = new FileReader();
            
            reader.readAsDataURL(audioBlob);
            reader.onloadend = () => {
                const base64Audio = reader.result.split(',')[1];
                sendAudio(base64Audio);
            };

            stream.getTracks().forEach(track => track.stop());
            stopRecordingUI();
        };

        state.mediaRecorder.start();
        state.isRecording = true;
        startRecordingUI();

        // Auto-stop after 5 seconds
        setTimeout(() => {
            if (state.isRecording && state.mediaRecorder.state === 'recording') {
                stopRecording();
            }
        }, 5000);

    } catch (error) {
        console.error('Microphone error:', error);
        showNotification('Could not access microphone', 'error');
    }
}

function stopRecording() {
    if (state.mediaRecorder && state.mediaRecorder.state === 'recording') {
        state.mediaRecorder.stop();
        state.isRecording = false;
    }
}

function startRecordingUI() {
    elements.micButton.classList.add('listening');
    elements.voiceVisualizer.classList.add('active');
    elements.micStatus.textContent = 'Listening... (5s max)';
    updateStatus('listening', 'Listening');
}

function stopRecordingUI() {
    elements.micButton.classList.remove('listening');
    elements.voiceVisualizer.classList.remove('active');
    elements.micStatus.textContent = 'Click to speak';
    updateStatus('connected', 'Connected');
}

// ===== Message Sending =====
function sendAudio(base64Audio) {
    if (state.ws && state.ws.readyState === WebSocket.OPEN) {
        state.ws.send(JSON.stringify({
            type: 'audio',
            audio: base64Audio
        }));
    }
}

function sendTextMessage(text) {
    if (state.ws && state.ws.readyState === WebSocket.OPEN) {
        state.ws.send(JSON.stringify({
            type: 'text',
            text: text
        }));
        addMessage(text, 'user');
        setThinking(true);
    }
}

// ===== Chat UI =====
function addMessage(text, sender, functionCalled = null) {
    // Remove welcome message if it exists
    const welcomeMsg = elements.chatContainer.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;

    const time = new Date().toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
    });

    let content = `<div class="message-content">${escapeHtml(text)}</div>`;
    
    if (functionCalled) {
        content += `<div class="function-badge">
            <span>🔧</span>
            <span>${formatFunctionName(functionCalled)}</span>
        </div>`;
    }
    
    content += `<div class="message-time">${time}</div>`;

    messageDiv.innerHTML = content;
    elements.chatContainer.appendChild(messageDiv);
    elements.chatContainer.scrollTop = elements.chatContainer.scrollHeight;
}

function clearChat() {
    elements.chatContainer.innerHTML = `
        <div class="welcome-message">
            <div class="welcome-icon">👋</div>
            <h3>Hello! I'm ARIA</h3>
            <p>Your AI-powered voice assistant. I can help you with reminders, messages, music, and more.</p>
        </div>
    `;
    elements.dataSection.innerHTML = '';
    showNotification('Chat cleared', 'info');
}

function setThinking(isThinking) {
    elements.thinkingIndicator.className = isThinking 
        ? 'thinking-indicator active' 
        : 'thinking-indicator';
}

// ===== Data Display =====
function displayData(functionName, data) {
    let html = '';

    switch(functionName) {
        case 'get_reminders':
            if (Array.isArray(data) && data.length > 0) {
                html = createDataCard('📅 Active Reminders', data.map(item => `
                    <div class="data-item">
                        <strong>${escapeHtml(item.text)}</strong><br>
                        <small>⏰ ${escapeHtml(item.time)}</small>
                    </div>
                `).join(''));
            }
            break;

        case 'get_messages':
            if (Array.isArray(data) && data.length > 0) {
                html = createDataCard('💬 Messages', data.map(item => `
                    <div class="data-item">
                        <strong>To: ${escapeHtml(item.recipient)}</strong><br>
                        ${escapeHtml(item.content)}<br>
                        <small>📅 ${escapeHtml(item.time)}</small>
                    </div>
                `).join(''));
            }
            break;

        case 'play_youtube':
            html = createDataCard('🎵 Now Playing', `
                <div class="data-item">
                    <strong>${escapeHtml(data.query)}</strong><br>
                    <small>Opening on YouTube...</small>
                </div>
            `);
            break;
    }

    if (html) {
        elements.dataSection.innerHTML = html;
    }
}

function createDataCard(title, content) {
    return `
        <div class="data-card">
            <h3>${title}</h3>
            ${content}
        </div>
    `;
}

// ===== Audio Playback =====
async function playAudioResponse(base64Audio) {
    try {
        const audioData = atob(base64Audio);
        const arrayBuffer = new Uint8Array(audioData.length);
        
        for (let i = 0; i < audioData.length; i++) {
            arrayBuffer[i] = audioData.charCodeAt(i);
        }

        const blob = new Blob([arrayBuffer], { type: 'audio/wav' });
        const url = URL.createObjectURL(blob);

        elements.audioPlayer.src = url;
        await elements.audioPlayer.play();

        // Clean up after playback
        elements.audioPlayer.onended = () => {
            URL.revokeObjectURL(url);
        };
    } catch (error) {
        console.error('Error playing audio:', error);
    }
}

// ===== Notifications =====
function showNotification(message, type = 'info', title = null) {
    // You can implement a custom notification system here
    console.log(`[${type.toUpperCase()}] ${title || ''} ${message}`);
}

// ===== Utility Functions =====
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatFunctionName(name) {
    return name
        .replace(/_/g, ' ')
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

function sendQuickAction(command) {
    elements.textInput.value = command;
    sendTextCommand();
}

function sendTextCommand() {
    const text = elements.textInput.value.trim();
    if (text && state.ws && state.ws.readyState === WebSocket.OPEN) {
        sendTextMessage(text);
        elements.textInput.value = '';
    }
}



elements.micButton.addEventListener('click', () => {
    // Play wake sound (user gesture → allowed by browser)
    wakeSound.currentTime = 0;
    wakeSound.play().catch(err => {
        console.warn('Wake sound blocked:', err);
    });

    if (!state.isRecording) {
        startRecording();
    } else {
        stopRecording();
    }
});


elements.sendButton.addEventListener('click', sendTextCommand);

elements.textInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendTextCommand();
    }
});

elements.clearChat.addEventListener('click', clearChat);

// Quick action buttons
document.querySelectorAll('.action-card').forEach(button => {
    button.addEventListener('click', () => {
        const command = button.getAttribute('data-command');
        if (command) {
            sendQuickAction(command);
        }
    });
});

// ===== Initialize =====
connectWebSocket();