// Main entry point for the voice control application
// This file initializes the VoiceControl class when the DOM is fully loaded

document.addEventListener('DOMContentLoaded', () => {
    // Check if the VoiceControl class is available
    if (typeof VoiceControl === 'undefined') {
        console.error('VoiceControl class is not defined. Make sure voice-control.js is loaded.');
        return;
    }
    
    // Initialize the voice control system
    try {
        const voiceControl = new VoiceControl();
        console.log('Voice control system initialized successfully');
        
        // Make it globally available for debugging
        window.voiceControl = voiceControl;
        
    } catch (error) {
        console.error('Failed to initialize voice control:', error);
        
        // Show error message to the user
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background-color: #f8d7da;
            color: #721c24;
            padding: 15px 25px;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            z-index: 1000;
            max-width: 90%;
            text-align: center;
        `;
        errorDiv.textContent = 'Error initializing voice control. Please check the console for details.';
        document.body.appendChild(errorDiv);
        
        // Remove the error message after 5 seconds
        setTimeout(() => {
            if (document.body.contains(errorDiv)) {
                document.body.removeChild(errorDiv);
            }
        }, 5000);
    }
});
