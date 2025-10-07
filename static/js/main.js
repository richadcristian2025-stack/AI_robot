document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const startButton = document.getElementById('startButton');
    const statusDiv = document.getElementById('status');
    const resultDiv = document.getElementById('result');
    const commandText = document.getElementById('commandText');
    const responseText = document.getElementById('responseText');
    const connectionStatus = document.getElementById('connectionStatus');
    const connectionText = document.getElementById('connectionText');
    
    // State
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    let isConnected = false;
    
    // Check connection status from server
    async function checkConnection() {
        try {
            const response = await fetch('/check-connection');
            const data = await response.json();
            isConnected = data.connected;
            
            // Update UI based on connection status
            if (isConnected) {
                connectionStatus.classList.add('connected');
                connectionText.textContent = 'ARDUINO CONNECTED';
                startButton.classList.remove('simulation');
                startButton.classList.add('connected');
                startButton.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                        <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                        <line x1="12" y1="19" x2="12" y2="23"></line>
                        <line x1="8" y1="23" x2="16" y2="23"></line>
                    </svg>
                    <span class="mic-tooltip">Tekan dan tahan untuk berbicara</span>
                `;
                statusDiv.textContent = 'Sistem siap menerima perintah suara';
            } else {
                connectionStatus.classList.remove('connected');
                connectionText.textContent = 'SIMULATION MODE';
                startButton.classList.add('simulation');
                startButton.classList.remove('connected');
                startButton.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                        <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                        <line x1="12" y1="19" x2="12" y2="23"></line>
                        <line x1="8" y1="23" x2="16" y2="23"></line>
                    </svg>
                    <span class="mic-tooltip">Mode simulasi - tidak terhubung ke Arduino</span>
                `;
                statusDiv.textContent = 'Mode simulasi - perintah tidak akan mengendalikan perangkat fisik';
            }
        } catch (error) {
            console.error('Error checking connection:', error);
            isConnected = false;
        }
    }
    
    // Initial connection check
    
    // Check connection status every 5 seconds
    setInterval(checkConnection, 5000);

    // Touch and mouse event handlers
    startButton.addEventListener('mousedown', async (e) => {
        // Don't proceed if in simulation mode
        if (!isConnected) {
            statusDiv.textContent = 'Mode simulasi: Perintah tidak akan mengendalikan perangkat fisik';
            statusDiv.style.color = '#ff6b6b';
            return;
        }
        await startRecording();
    });
    startButton.addEventListener('touchstart', (e) => {
        e.preventDefault();
        startRecording();
    });
    
    startButton.addEventListener('mouseup', async (e) => {
        // Don't proceed if in simulation mode
        if (!isConnected) {
            return;
        }
        await stopRecording();
    });
    startButton.addEventListener('mouseleave', stopRecording);
    startButton.addEventListener('touchend', stopRecording);
    startButton.addEventListener('touchcancel', stopRecording);

    // Prevent context menu on long press (mobile)
    startButton.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        return false;
    });

    // Initial connection check
    checkConnection();

    async function startRecording() {
        if (isRecording) return;
        isRecording = true;
        
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            
            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };

            mediaRecorder.onstop = processAudio;
            mediaRecorder.start();
            
            // Update UI
            startButton.classList.add('recording');
            statusDiv.textContent = 'Mendengarkan...';
            resultDiv.style.display = 'none';
            
        } catch (err) {
            console.error('Error accessing microphone:', err);
            statusDiv.textContent = 'Error: Tidak bisa mengakses mikrofon';
            isRecording = false;
        }
    }

    function stopRecording() {
        if (!isRecording) return;
        isRecording = false;
        
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            // Stop all tracks in the stream
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
            
            // Update UI
            statusDiv.textContent = 'Memproses suara...';
        }
    }

    // Send audio to server for processing
    async function sendAudio(audioBlob) {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');

        // Show recording status
        statusDiv.textContent = 'Mengirim perintah...';
        statusDiv.style.color = '';

        try {
            const response = await fetch('/process_audio', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const result = await response.json();
            
            // Update UI with results
            commandText.textContent = result.text || 'Tidak terdeteksi';
            responseText.textContent = result.response || 'Tidak ada respon';
            
            // Show result box
            resultDiv.style.display = 'block';
            statusDiv.textContent = 'Selesai memproses';
            
        } catch (error) {
            console.error('Error:', error);
            statusDiv.textContent = 'Error: Gagal memproses suara';
            resultDiv.style.display = 'none';
        }
    }

    // Add haptic feedback for mobile devices
    function vibrate() {
        if ('vibrate' in navigator) {
            navigator.vibrate(50);
        }
    }
});
