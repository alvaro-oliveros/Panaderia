// Voice Chat JavaScript Functionality

class VoiceChatManager {
    constructor() {
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.currentSessionId = null;
        this.messageCount = 0;
        this.userData = null;
        
        // Get user data
        this.userData = checkAuth();
        if (!this.userData) {
            window.location.href = 'login.html';
            return;
        }
    }

    async init() {
        try {
            // Request microphone permission
            await this.requestMicrophoneAccess();
            this.updateStatus('Listo para escuchar');
            console.log('Voice chat initialized successfully');
        } catch (error) {
            console.error('Error initializing voice chat:', error);
            this.showError('Error al acceder al micrófono. Verifica los permisos.');
        }
    }

    async requestMicrophoneAccess() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 44100
                } 
            });
            
            // Test that we can create a media recorder
            this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });
            
            // Stop the test stream
            stream.getTracks().forEach(track => track.stop());
            
            console.log('Microphone access granted');
            return true;
        } catch (error) {
            console.error('Microphone access denied:', error);
            throw new Error('No se pudo acceder al micrófono');
        }
    }

    async startRecording() {
        if (this.isRecording) return;

        try {
            // Get fresh audio stream
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 44100
                } 
            });

            this.audioChunks = [];
            this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };

            this.mediaRecorder.onstop = () => {
                // Stop all tracks to release microphone
                stream.getTracks().forEach(track => track.stop());
                this.processRecording();
            };

            this.mediaRecorder.start();
            this.isRecording = true;
            
            // Update UI
            this.updateRecordingUI(true);
            this.updateStatus('Escuchando... Habla ahora');
            
            console.log('Recording started');

        } catch (error) {
            console.error('Error starting recording:', error);
            this.showError('Error al iniciar grabación');
        }
    }

    stopRecording() {
        if (!this.isRecording || !this.mediaRecorder) return;

        try {
            this.mediaRecorder.stop();
            this.isRecording = false;
            this.updateRecordingUI(false);
            this.updateStatus('Procesando audio...');
            
            console.log('Recording stopped');
        } catch (error) {
            console.error('Error stopping recording:', error);
            this.showError('Error al detener grabación');
        }
    }

    async processRecording() {
        try {
            if (this.audioChunks.length === 0) {
                this.showError('No se grabó audio');
                return;
            }

            // Create audio blob
            const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
            console.log('Audio blob created:', audioBlob.size, 'bytes');

            // Show loading
            this.showLoading('Transcribiendo audio...');

            // Send to backend
            await this.sendVoiceMessage(audioBlob);

        } catch (error) {
            console.error('Error processing recording:', error);
            this.showError('Error al procesar el audio');
        } finally {
            this.hideLoading();
            this.updateStatus('Presiona para hablar');
        }
    }

    async sendVoiceMessage(audioBlob) {
        try {
            // Prepare form data
            const formData = new FormData();
            formData.append('audio_file', audioBlob, 'voice_message.webm');
            formData.append('user_id', this.userData.userId);
            
            if (this.currentSessionId) {
                formData.append('session_id', this.currentSessionId);
            }

            this.updateLoadingText('Enviando al servidor...');

            // Send to backend
            const response = await fetch(`${API_URL}/voice/chat`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error del servidor');
            }

            const result = await response.json();
            console.log('Voice chat response:', result);

            if (result.success) {
                // Update session ID
                this.currentSessionId = result.session_id;
                
                // Add messages to chat
                this.addUserMessage(result.transcription);
                this.addBotMessage(result.response, result.query_type);
                
                // Update session info
                this.updateSessionInfo();
                
                // Play success sound (optional)
                this.playNotificationSound();
                
            } else {
                throw new Error('Error en el procesamiento de voz');
            }

        } catch (error) {
            console.error('Error sending voice message:', error);
            this.showError(`Error: ${error.message}`);
        }
    }

    addUserMessage(transcription) {
        const chatArea = document.getElementById('chatArea');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message user-message';
        
        messageDiv.innerHTML = `
            <div class="message-content">
                ${this.escapeHtml(transcription)}
                <div class="message-meta">
                    ${new Date().toLocaleTimeString('es-ES')}
                </div>
            </div>
        `;
        
        chatArea.appendChild(messageDiv);
        this.scrollToBottom();
        this.messageCount++;
    }

    addBotMessage(response, queryType = 'general') {
        const chatArea = document.getElementById('chatArea');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message bot-message';
        
        const typeIcon = this.getQueryTypeIcon(queryType);
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <span style="margin-right: 8px;">${typeIcon}</span>
                    <small style="color: #666; text-transform: capitalize;">${queryType}</small>
                </div>
                ${this.formatBotResponse(response)}
                <div class="message-meta">
                    ${new Date().toLocaleTimeString('es-ES')} • Asistente IA
                </div>
            </div>
        `;
        
        chatArea.appendChild(messageDiv);
        this.scrollToBottom();
    }

    formatBotResponse(response) {
        // Convert line breaks to HTML
        let formatted = this.escapeHtml(response);
        formatted = formatted.replace(/\n/g, '<br>');
        
        // Make numbers and monetary values stand out
        formatted = formatted.replace(/\$[\d,]+\.?\d*/g, '<strong>$&</strong>');
        formatted = formatted.replace(/\b\d+[\d,]*\.?\d*\s*(unidades?|productos?|items?|transacciones?)\b/gi, '<strong>$&</strong>');
        
        return formatted;
    }

    getQueryTypeIcon(queryType) {
        const icons = {
            'sales': '💰',
            'inventory': '📦', 
            'environmental': '🌡️',
            'locations': '🏪',
            'users': '👥',
            'general': '💬'
        };
        return icons[queryType] || '💬';
    }

    updateRecordingUI(isRecording) {
        const voiceButton = document.getElementById('voiceButton');
        const recordingIndicator = document.getElementById('recordingIndicator');
        const audioVisualizer = document.getElementById('audioVisualizer');
        const buttonText = voiceButton.querySelector('.button-text');
        const micIcon = voiceButton.querySelector('.mic-icon');

        if (isRecording) {
            voiceButton.classList.add('recording');
            buttonText.textContent = 'Detener';
            micIcon.textContent = '⏹️';
            recordingIndicator.style.display = 'flex';
            audioVisualizer.style.display = 'flex';
        } else {
            voiceButton.classList.remove('recording', 'processing');
            buttonText.textContent = 'Hablar';
            micIcon.textContent = '🎤';
            recordingIndicator.style.display = 'none';
            audioVisualizer.style.display = 'none';
        }
    }

    updateStatus(message) {
        const statusText = document.getElementById('statusText');
        statusText.textContent = message;
    }

    updateSessionInfo() {
        const sessionInfo = document.getElementById('sessionInfo');
        const clearBtn = document.getElementById('clearChatBtn');
        
        if (this.currentSessionId) {
            sessionInfo.textContent = `Sesión ${this.currentSessionId} • ${this.messageCount} mensajes`;
            clearBtn.style.display = 'inline-block';
        }
    }

    scrollToBottom() {
        const chatArea = document.getElementById('chatArea');
        chatArea.scrollTop = chatArea.scrollHeight;
    }

    showLoading(message = 'Procesando...') {
        const modal = document.getElementById('loadingModal');
        const loadingText = document.getElementById('loadingText');
        loadingText.textContent = message;
        modal.style.display = 'flex';
    }

    updateLoadingText(message) {
        const loadingText = document.getElementById('loadingText');
        if (loadingText) {
            loadingText.textContent = message;
        }
    }

    hideLoading() {
        const modal = document.getElementById('loadingModal');
        modal.style.display = 'none';
    }

    showError(message) {
        // Create error message in chat
        const chatArea = document.getElementById('chatArea');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `
            <strong>Error:</strong> ${this.escapeHtml(message)}
            <br><small>Inténtalo de nuevo o contacta al administrador</small>
        `;
        chatArea.appendChild(errorDiv);
        this.scrollToBottom();
    }

    async sendQuickQuery(query) {
        try {
            this.showLoading('Procesando consulta...');
            
            const formData = new FormData();
            formData.append('query', query);
            formData.append('user_id', this.userData.userId);
            
            if (this.currentSessionId) {
                formData.append('session_id', this.currentSessionId);
            }

            const response = await fetch(`${API_URL}/voice/query`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error del servidor');
            }

            const result = await response.json();

            if (result.success) {
                this.currentSessionId = result.session_id;
                this.addUserMessage(query);
                this.addBotMessage(result.response, result.query_type);
                this.updateSessionInfo();
            } else {
                throw new Error('Error en el procesamiento');
            }

        } catch (error) {
            console.error('Error sending quick query:', error);
            this.showError(`Error: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }

    clearChat() {
        if (confirm('¿Estás seguro de que quieres limpiar el chat?')) {
            const chatArea = document.getElementById('chatArea');
            // Keep only the welcome message
            const welcomeMessage = chatArea.querySelector('.welcome-message');
            chatArea.innerHTML = '';
            if (welcomeMessage) {
                chatArea.appendChild(welcomeMessage);
            }
            
            this.currentSessionId = null;
            this.messageCount = 0;
            this.updateSessionInfo();
            
            const sessionInfo = document.getElementById('sessionInfo');
            const clearBtn = document.getElementById('clearChatBtn');
            sessionInfo.textContent = 'Nueva sesión';
            clearBtn.style.display = 'none';
        }
    }

    playNotificationSound() {
        // Simple notification beep
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.value = 800;
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.3);
        } catch (error) {
            // Ignore audio context errors
            console.log('Audio notification not available');
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Global instance
let voiceChatManager;

// Global functions called from HTML
function initializeVoiceChat() {
    voiceChatManager = new VoiceChatManager();
    voiceChatManager.init();
}

function toggleRecording() {
    if (!voiceChatManager) return;
    
    if (voiceChatManager.isRecording) {
        voiceChatManager.stopRecording();
    } else {
        voiceChatManager.startRecording();
    }
}

function quickQuery(query) {
    if (!voiceChatManager) return;
    voiceChatManager.sendQuickQuery(query);
}

function clearChat() {
    if (!voiceChatManager) return;
    voiceChatManager.clearChat();
}

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Space bar to toggle recording (when not in input fields)
    if (event.code === 'Space' && !['INPUT', 'TEXTAREA'].includes(event.target.tagName)) {
        event.preventDefault();
        toggleRecording();
    }
    
    // Escape to stop recording
    if (event.code === 'Escape' && voiceChatManager && voiceChatManager.isRecording) {
        voiceChatManager.stopRecording();
    }
});

// Handle page visibility change (stop recording if page becomes hidden)
document.addEventListener('visibilitychange', function() {
    if (document.hidden && voiceChatManager && voiceChatManager.isRecording) {
        voiceChatManager.stopRecording();
    }
});

console.log('Voice chat script loaded');