// Voice Control Module
class VoiceControl {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.audioContext = null;
        this.mediaRecorder = null;
        this.audioChunks = [];
        
        // DOM Elements
        this.micButton = document.getElementById('micButton');
        this.micIcon = document.getElementById('micIcon');
        this.micStatus = document.getElementById('micStatus');
        this.recognizedText = document.getElementById('recognizedText');
        this.arduinoCommand = document.getElementById('arduinoCommand');
        this.robotResponse = document.getElementById('robotResponse');
        this.historyList = document.getElementById('historyList');
        this.connectionStatus = document.getElementById('connectionStatus');
        this.statusDot = document.getElementById('statusDot');
        this.connectionText = document.getElementById('connectionText');
        this.notification = document.getElementById('notification');
        this.notificationText = document.getElementById('notificationText');
        
        // Initialize
        this.init();
    }
    
    async init() {
        // Check for Web Speech API support
        if (!('webkitSpeechRecognition' in window)) {
            this.showNotification('Web Speech API is not supported in this browser', 'error');
            this.micButton.disabled = true;
            this.micStatus.textContent = 'Speech recognition not supported';
            return;
        }
        
        // Initialize Web Speech API
        this.recognition = new webkitSpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = 'en-US';
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Check connection status
        this.checkConnection();
        
        // Load command history
        this.loadHistory();
    }
    
    setupEventListeners() {
        // Microphone button click
        this.micButton.addEventListener('click', () => this.toggleRecording());
        
        // Suggestion chips
        document.querySelectorAll('.suggestion-chip').forEach(chip => {
            chip.addEventListener('click', () => {
                const command = chip.getAttribute('data-command');
                this.processTextCommand(chip.querySelector('span').textContent);
            });
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === ' ' && !this.isListening) {
                e.preventDefault();
                this.toggleRecording();
            } else if (e.key === 'Escape' && this.isListening) {
                this.stopRecording();
            }
        });
    }
    
    async toggleRecording() {
        if (this.isListening) {
            this.stopRecording();
        } else {
            await this.startRecording();
        }
    }
    
    async startRecording() {
        try {
            // Request microphone access
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Initialize MediaRecorder
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];
            
            // Handle data available
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            
            // Handle recording stop
            this.mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                await this.sendAudioToServer(audioBlob);
                
                // Stop all tracks in the stream
                stream.getTracks().forEach(track => track.stop());
            };
            
            // Start recording
            this.mediaRecorder.start();
            this.isListening = true;
            
            // Update UI
            this.micButton.classList.add('listening');
            this.micIcon.classList.remove('fa-microphone');
            this.micIcon.classList.add('fa-stop');
            this.micStatus.textContent = 'Listening...';
            
            // Auto-stop after 5 seconds of silence
            this.recognition.start();
            this.recognition.onspeechend = () => {
                if (this.isListening) {
                    this.stopRecording();
                }
            };
            
        } catch (error) {
            console.error('Error accessing microphone:', error);
            this.showNotification('Could not access microphone', 'error');
            this.micStatus.textContent = 'Microphone access denied';
        }
    }
    
    stopRecording() {
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
        }
        
        if (this.recognition) {
            this.recognition.stop();
        }
        
        this.isListening = false;
        
        // Update UI
        this.micButton.classList.remove('listening');
        this.micIcon.classList.remove('fa-stop');
        this.micIcon.classList.add('fa-microphone');
        this.micStatus.textContent = 'Click the microphone to start';
    }
    
    async sendAudioToServer(audioBlob) {
        try {
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.wav');
            
            // Show loading state
            this.recognizedText.textContent = 'Processing...';
            this.arduinoCommand.textContent = 'Waiting...';
            this.robotResponse.textContent = 'Waiting...';
            
            // Send to server
            const response = await fetch('/api/process_audio', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('Server error');
            }
            
            const result = await response.json();
            
            // Update UI with results
            this.updateUI(result);
            
            // Add to history
            this.addToHistory(result);
            
        } catch (error) {
            console.error('Error sending audio to server:', error);
            this.showNotification('Error processing audio', 'error');
            
            // Reset UI
            this.recognizedText.textContent = '-';
            this.arduinoCommand.textContent = '-';
            this.robotResponse.textContent = '-';
        }
    }
    
    updateUI(result) {
        this.recognizedText.textContent = result.text || '-';
        this.arduinoCommand.textContent = result.command || '-';
        this.robotResponse.textContent = result.response || '-';
        
        // Update status indicator
        if (result.status === 'success') {
            this.showNotification('Command executed successfully', 'success');
        } else if (result.status === 'error') {
            this.showNotification('Error processing command', 'error');
        }
    }
    
    async checkConnection() {
        try {
            const response = await fetch('/api/check-connection');
            const data = await response.json();
            
            if (data.connected) {
                this.connectionStatus.classList.remove('disconnected');
                this.connectionStatus.classList.add('connected');
                this.statusDot.classList.remove('disconnected');
                this.statusDot.classList.add('connected');
                this.connectionText.textContent = `Connected to ${data.port}`;
            } else {
                this.connectionStatus.classList.remove('connected');
                this.connectionStatus.classList.add('disconnected');
                this.statusDot.classList.remove('connected');
                this.statusDot.classList.add('disconnected');
                this.connectionText.textContent = 'Simulation Mode';
            }
            
            return data.connected;
            
        } catch (error) {
            console.error('Error checking connection:', error);
            this.connectionStatus.classList.add('disconnected');
            this.statusDot.classList.add('disconnected');
            this.connectionText.textContent = 'Connection Error';
            return false;
        }
    }
    
    async loadHistory() {
        try {
            const response = await fetch('/api/history');
            const data = await response.json();
            
            if (data.status === 'ok' && data.history.length > 0) {
                this.historyList.innerHTML = ''; // Clear loading/empty message
                
                // Add each history item
                data.history.reverse().forEach(item => {
                    this.addHistoryItem(item);
                });
            }
            
        } catch (error) {
            console.error('Error loading history:', error);
        }
    }
    
    addToHistory(result) {
        // Add to the beginning of the history list
        this.addHistoryItem(result);
        
        // If this is the first item, remove the empty message
        const emptyMessage = this.historyList.querySelector('.empty-message');
        if (emptyMessage) {
            this.historyList.removeChild(emptyMessage);
        }
        
        // Keep only the last 10 items
        const items = this.historyList.querySelectorAll('.history-item');
        if (items.length > 10) {
            this.historyList.removeChild(items[items.length - 1]);
        }
    }
    
    addHistoryItem(item) {
        const historyItem = document.createElement('div');
        historyItem.className = `history-item ${item.status}`;
        
        const time = new Date().toLocaleTimeString();
        
        historyItem.innerHTML = `
            <div class="history-command">${item.text || 'No text recognized'}</div>
            <div class="history-time">${time}</div>
            <div class="history-status">
                <i class="fas fa-${item.status === 'success' ? 'check-circle' : 'times-circle'}"></i>
            </div>
        `;
        
        // Add click handler to show details
        historyItem.addEventListener('click', () => {
            this.showCommandDetails(item);
        });
        
        // Insert at the beginning
        if (this.historyList.firstChild) {
            this.historyList.insertBefore(historyItem, this.historyList.firstChild);
        } else {
            this.historyList.appendChild(historyItem);
        }
    }
    
    showCommandDetails(item) {
        // Update the main display with the selected command
        this.recognizedText.textContent = item.text || '-';
        this.arduinoCommand.textContent = item.command || '-';
        this.robotResponse.textContent = item.response || '-';
        
        // Show a notification
        this.showNotification('Command details loaded', 'info');
    }
    
    processTextCommand(text) {
        // Simulate a voice command with the given text
        this.recognizedText.textContent = text;
        this.arduinoCommand.textContent = 'Processing...';
        this.robotResponse.textContent = 'Waiting...';
        
        // Send to server
        fetch('/api/process_text', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text })
        })
        .then(response => response.json())
        .then(data => {
            this.updateUI(data);
            this.addToHistory(data);
        })
        .catch(error => {
            console.error('Error:', error);
            this.showNotification('Error processing text command', 'error');
        });
    }
    
    showNotification(message, type = 'info') {
        this.notificationText.textContent = message;
        this.notification.className = `notification ${type}`;
        
        // Show the notification
        this.notification.classList.add('show');
        
        // Hide after 3 seconds
        setTimeout(() => {
            this.notification.classList.remove('show');
        }, 3000);
    }
}

// Initialize when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    window.voiceControl = new VoiceControl();
});
