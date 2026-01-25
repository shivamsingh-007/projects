/**
 * Voice Deepfake Detector - Frontend JavaScript
 * Handles file upload, API communication, and UI interactions
 */

// Configuration
const API_BASE_URL = 'http://localhost:5000';
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

// State
let currentFile = null;
let wavesurfer = null;
let analysisStartTime = 0;

// DOM Elements
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const filePreview = document.getElementById('file-preview');
const fileName = document.getElementById('file-name');
const fileSize = document.getElementById('file-size');
const fileDuration = document.getElementById('file-duration');
const btnRemove = document.getElementById('btn-remove');
const btnAnalyze = document.getElementById('btn-analyze');
const btnPlay = document.getElementById('btn-play');
const timeDisplay = document.getElementById('time-display');
const processingOverlay = document.getElementById('processing-overlay');
const resultsSection = document.getElementById('results-section');
const uploadSection = document.getElementById('upload-section');
const btnAnalyzeAnother = document.getElementById('btn-analyze-another');
const errorToast = document.getElementById('error-toast');
const toastMessage = document.getElementById('toast-message');
const toastClose = document.getElementById('toast-close');
const infoHeader = document.getElementById('info-header');
const infoContent = document.getElementById('info-content');
const btnExpand = document.getElementById('btn-expand');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    initializeParticles();
    checkBackendHealth();
});

/**
 * Initialize all event listeners
 */
function initializeEventListeners() {
    // File upload events
    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop events
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);
    
    // Button events
    btnRemove.addEventListener('click', removeFile);
    btnAnalyze.addEventListener('click', analyzeAudio);
    btnAnalyzeAnother.addEventListener('click', resetAnalysis);
    btnPlay.addEventListener('click', toggleAudioPlayback);
    toastClose.addEventListener('click', hideToast);
    
    // Info section toggle
    infoHeader.addEventListener('click', toggleInfoSection);
    
    // Keyboard accessibility
    document.addEventListener('keydown', handleKeyboardShortcuts);
}

/**
 * Handle keyboard shortcuts
 */
function handleKeyboardShortcuts(e) {
    if (e.key === 'Escape') {
        if (!processingOverlay.classList.contains('hidden')) {
            // Don't allow closing during processing
            return;
        }
        if (!resultsSection.classList.contains('hidden')) {
            resetAnalysis();
        }
    }
}

/**
 * Check backend API health
 */
async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        console.log('Backend health:', data);
    } catch (error) {
        console.error('Backend not available:', error);
        showToast('Backend server is not running. Please start the server.');
    }
}

/**
 * Handle file selection
 */
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        validateAndLoadFile(file);
    }
}

/**
 * Handle drag over
 */
function handleDragOver(event) {
    event.preventDefault();
    dropZone.classList.add('drag-over');
}

/**
 * Handle drag leave
 */
function handleDragLeave(event) {
    event.preventDefault();
    dropZone.classList.remove('drag-over');
}

/**
 * Handle file drop
 */
function handleDrop(event) {
    event.preventDefault();
    dropZone.classList.remove('drag-over');
    
    const file = event.dataTransfer.files[0];
    if (file) {
        validateAndLoadFile(file);
    }
}

/**
 * Validate and load audio file
 */
async function validateAndLoadFile(file) {
    // Validate file type
    const allowedTypes = ['audio/mpeg', 'audio/wav', 'audio/x-wav', 'audio/mp4', 'audio/x-m4a', 'audio/ogg', 'audio/flac'];
    const allowedExtensions = ['.mp3', '.wav', '.m4a', '.ogg', '.flac'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
        showToast('Invalid file format. Please upload MP3, WAV, M4A, OGG, or FLAC files.');
        return;
    }
    
    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
        showToast('File too large. Maximum size is 10MB.');
        return;
    }
    
    // Store file
    currentFile = file;
    
    // Update UI
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    
    // Load audio for waveform and duration
    try {
        const audioUrl = URL.createObjectURL(file);
        const audio = new Audio(audioUrl);
        
        audio.addEventListener('loadedmetadata', () => {
            const duration = audio.duration;
            fileDuration.textContent = formatDuration(duration);
            
            // Validate duration
            if (duration < 0.5) {
                showToast('Audio too short. Minimum duration is 0.5 seconds.');
                removeFile();
                return;
            }
            
            if (duration > 60) {
                showToast('Audio too long. Maximum duration is 60 seconds.');
                removeFile();
                return;
            }
            
            // Show file preview
            dropZone.style.display = 'none';
            filePreview.classList.remove('hidden');
            btnAnalyze.disabled = false;
            
            // Initialize waveform
            initializeWaveform(audioUrl);
        });
        
    } catch (error) {
        console.error('Error loading audio:', error);
        showToast('Error loading audio file. Please try another file.');
    }
}

/**
 * Initialize WaveSurfer audio waveform
 */
function initializeWaveform(audioUrl) {
    if (wavesurfer) {
        wavesurfer.destroy();
    }
    
    wavesurfer = WaveSurfer.create({
        container: '#waveform',
        waveColor: 'rgba(0, 245, 255, 0.5)',
        progressColor: 'rgba(0, 245, 255, 1)',
        cursorColor: '#7b2cbf',
        barWidth: 2,
        barRadius: 3,
        cursorWidth: 2,
        height: 80,
        barGap: 2,
        responsive: true,
        normalize: true,
    });
    
    wavesurfer.load(audioUrl);
    
    // Update time display
    wavesurfer.on('audioprocess', () => {
        const current = formatDuration(wavesurfer.getCurrentTime());
        const total = formatDuration(wavesurfer.getDuration());
        timeDisplay.textContent = `${current} / ${total}`;
    });
    
    wavesurfer.on('finish', () => {
        const playIcon = btnPlay.querySelector('.icon-play');
        const pauseIcon = btnPlay.querySelector('.icon-pause');
        playIcon.classList.remove('hidden');
        pauseIcon.classList.add('hidden');
    });
}

/**
 * Toggle audio playback
 */
function toggleAudioPlayback() {
    if (!wavesurfer) return;
    
    const playIcon = btnPlay.querySelector('.icon-play');
    const pauseIcon = btnPlay.querySelector('.icon-pause');
    
    if (wavesurfer.isPlaying()) {
        wavesurfer.pause();
        playIcon.classList.remove('hidden');
        pauseIcon.classList.add('hidden');
    } else {
        wavesurfer.play();
        playIcon.classList.add('hidden');
        pauseIcon.classList.remove('hidden');
    }
}

/**
 * Remove uploaded file
 */
function removeFile() {
    currentFile = null;
    fileInput.value = '';
    dropZone.style.display = 'block';
    filePreview.classList.add('hidden');
    btnAnalyze.disabled = true;
    
    if (wavesurfer) {
        wavesurfer.destroy();
        wavesurfer = null;
    }
}

/**
 * Analyze audio file
 */
async function analyzeAudio() {
    console.log('🔵 Analyze button clicked');
    
    if (!currentFile) {
        console.error('❌ No file selected');
        return;
    }
    
    console.log('✅ File selected:', currentFile.name);
    
    // Record start time
    analysisStartTime = Date.now();
    
    // Show processing overlay
    console.log('🔵 Showing processing overlay');
    processingOverlay.classList.remove('hidden');
    updateProcessingSteps(0);
    
    // Prepare form data
    const formData = new FormData();
    formData.append('audio', currentFile);
    
    try {
        // Simulate processing steps
        setTimeout(() => updateProcessingSteps(1), 500);
        setTimeout(() => updateProcessingSteps(2), 1500);
        
        console.log('🔵 Making API request to:', `${API_BASE_URL}/api/analyze`);
        console.log('🔵 File details:', {
            name: currentFile.name,
            size: currentFile.size,
            type: currentFile.type
        });
        
        // Make API request
        const response = await fetch(`${API_BASE_URL}/api/analyze`, {
            method: 'POST',
            body: formData,
        });
        
        console.log('✅ API Response received:', response.status);
        
        const data = await response.json();
        console.log('✅ Response data:', data);
        
        if (!response.ok) {
            throw new Error(data.error || 'Analysis failed');
        }
        
        // Calculate analysis time
        const analysisTime = ((Date.now() - analysisStartTime) / 1000).toFixed(1);
        
        // Hide processing overlay
        processingOverlay.classList.add('hidden');
        
        console.log('🔵 Displaying results...');
        
        // Show results
        displayResults(data, analysisTime);
        
    } catch (error) {
        console.error('❌ Error during analysis:', error);
        console.error('❌ Error details:', {
            message: error.message,
            stack: error.stack
        });
        processingOverlay.classList.add('hidden');
        showToast(error.message || 'Failed to analyze audio. Please check if the backend is running.');
    }
}

/**
 * Update processing steps animation
 */
function updateProcessingSteps(step) {
    const steps = document.querySelectorAll('.step');
    steps.forEach((stepEl, index) => {
        if (index <= step) {
            stepEl.classList.add('active');
        } else {
            stepEl.classList.remove('active');
        }
    });
}

/**
 * Display analysis results
 */
function displayResults(data, analysisTime) {
    console.log('🔵 displayResults called with:', data);
    
    const isReal = data.is_real;
    const confidence = data.confidence;
    const authenticityScore = data.authenticity_score;
    
    console.log('🔵 Verdict:', isReal ? 'REAL' : 'FAKE');
    console.log('🔵 Confidence:', confidence);
    
    // Update verdict
    const verdictContainer = document.getElementById('verdict-container');
    const verdictIcon = document.getElementById('verdict-icon');
    const verdictTitle = document.getElementById('verdict-title');
    const verdictSubtitle = document.getElementById('verdict-subtitle');
    
    // Set verdict text and styling
    if (isReal) {
        verdictTitle.textContent = 'REAL VOICE';
        verdictTitle.className = 'verdict-title real';
        verdictSubtitle.textContent = 'Audio appears to be authentic';
        verdictIcon.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="#00ff88" stroke-width="2" fill="none"/>
                <path d="M8 12L11 15L16 9" stroke="#00ff88" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        `;
    } else {
        verdictTitle.textContent = 'SYNTHETIC VOICE';
        verdictTitle.className = 'verdict-title fake';
        verdictSubtitle.textContent = 'Audio appears to be synthetic or manipulated';
        verdictIcon.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="#ff006e" stroke-width="2" fill="none"/>
                <path d="M12 8V12M12 16H12.01" stroke="#ff006e" stroke-width="2" stroke-linecap="round"/>
            </svg>
        `;
    }
    
    // Update confidence score
    document.getElementById('confidence-value').textContent = `${confidence.toFixed(1)}%`;
    document.getElementById('authenticity-score').textContent = `${authenticityScore.toFixed(1)}%`;
    
    // Animate progress ring
    const progressCircle = document.getElementById('progress-circle');
    const progressText = document.getElementById('progress-text');
    const radius = 85;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (confidence / 100) * circumference;
    
    // Set SVG gradient
    if (!document.getElementById('gradient')) {
        const svg = progressCircle.closest('svg');
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        const gradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
        gradient.setAttribute('id', 'gradient');
        gradient.setAttribute('x1', '0%');
        gradient.setAttribute('y1', '0%');
        gradient.setAttribute('x2', '100%');
        gradient.setAttribute('y2', '100%');
        
        const stop1 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
        stop1.setAttribute('offset', '0%');
        stop1.setAttribute('style', `stop-color:${isReal ? '#00ff88' : '#ff006e'};stop-opacity:1`);
        
        const stop2 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
        stop2.setAttribute('offset', '100%');
        stop2.setAttribute('style', `stop-color:${isReal ? '#00f5ff' : '#ff8800'};stop-opacity:1`);
        
        gradient.appendChild(stop1);
        gradient.appendChild(stop2);
        defs.appendChild(gradient);
        svg.insertBefore(defs, svg.firstChild);
    }
    
    progressCircle.style.strokeDasharray = circumference;
    progressCircle.style.strokeDashoffset = circumference;
    
    // Animate to final value
    setTimeout(() => {
        progressCircle.style.strokeDashoffset = offset;
        animateProgressText(progressText, confidence);
    }, 100);
    
    // Update details
    if (data.details) {
        document.getElementById('result-duration').textContent = `${data.details.duration}s`;
        document.getElementById('result-sample-rate').textContent = `${data.details.sample_rate} Hz`;
    }
    document.getElementById('analysis-time').textContent = `${analysisTime}s`;
    
    // Hide upload section and show results
    uploadSection.style.display = 'none';
    resultsSection.classList.remove('hidden');
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Animate progress text
 */
function animateProgressText(element, targetValue) {
    let currentValue = 0;
    const increment = targetValue / 50;
    const timer = setInterval(() => {
        currentValue += increment;
        if (currentValue >= targetValue) {
            currentValue = targetValue;
            clearInterval(timer);
        }
        element.textContent = `${Math.round(currentValue)}%`;
    }, 20);
}

/**
 * Reset analysis and return to upload
 */
function resetAnalysis() {
    resultsSection.classList.add('hidden');
    uploadSection.style.display = 'block';
    removeFile();
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * Toggle info section
 */
function toggleInfoSection() {
    infoContent.classList.toggle('hidden');
    infoContent.classList.toggle('expanded');
    btnExpand.classList.toggle('expanded');
}

/**
 * Show error toast
 */
function showToast(message) {
    toastMessage.textContent = message;
    errorToast.classList.remove('hidden');
    
    // Auto-hide after 5 seconds
    setTimeout(hideToast, 5000);
}

/**
 * Hide error toast
 */
function hideToast() {
    errorToast.classList.add('hidden');
}

/**
 * Format file size
 */
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

/**
 * Format duration in seconds to MM:SS
 */
function formatDuration(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Initialize particle animation
 */
function initializeParticles() {
    const canvas = document.getElementById('particles');
    const ctx = canvas.getContext('2d');
    
    // Set canvas size
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    // Particle class
    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 2 + 0.5;
            this.speedX = (Math.random() - 0.5) * 0.5;
            this.speedY = (Math.random() - 0.5) * 0.5;
            this.opacity = Math.random() * 0.5 + 0.2;
        }
        
        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            
            if (this.x > canvas.width) this.x = 0;
            if (this.x < 0) this.x = canvas.width;
            if (this.y > canvas.height) this.y = 0;
            if (this.y < 0) this.y = canvas.height;
        }
        
        draw() {
            ctx.fillStyle = `rgba(0, 245, 255, ${this.opacity})`;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }
    
    // Create particles
    const particles = [];
    const particleCount = 50;
    
    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }
    
    // Animation loop
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach(particle => {
            particle.update();
            particle.draw();
        });
        
        requestAnimationFrame(animate);
    }
    
    animate();
}

// Export functions for testing (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        formatFileSize,
        formatDuration,
    };
}
