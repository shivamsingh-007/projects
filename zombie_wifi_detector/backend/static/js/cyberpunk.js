/**
 * ZOMBIE WIFI DETECTOR - CYBERPUNK EFFECTS
 * CyberSentry AI - Tarun, Shivam, Yash
 */

// ==================== PARTICLE SYSTEM ====================

class ParticleSystem {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.resize();
        
        window.addEventListener('resize', () => this.resize());
        this.init();
        this.animate();
    }
    
    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }
    
    init() {
        // Create WiFi signal particles
        for (let i = 0; i < 50; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                size: Math.random() * 3 + 1,
                speedX: (Math.random() - 0.5) * 0.5,
                speedY: (Math.random() - 0.5) * 0.5,
                color: ['#b026ff', '#00d9ff', '#ff0055'][Math.floor(Math.random() * 3)],
                alpha: Math.random() * 0.5 + 0.3
            });
        }
    }
    
    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.particles.forEach(particle => {
            // Update position
            particle.x += particle.speedX;
            particle.y += particle.speedY;
            
            // Wrap around screen
            if (particle.x < 0) particle.x = this.canvas.width;
            if (particle.x > this.canvas.width) particle.x = 0;
            if (particle.y < 0) particle.y = this.canvas.height;
            if (particle.y > this.canvas.height) particle.y = 0;
            
            // Draw particle
            this.ctx.fillStyle = particle.color;
            this.ctx.globalAlpha = particle.alpha;
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            this.ctx.fill();
            
            // Draw WiFi waves
            this.ctx.strokeStyle = particle.color;
            this.ctx.lineWidth = 1;
            for (let i = 1; i <= 3; i++) {
                this.ctx.globalAlpha = particle.alpha / (i * 2);
                this.ctx.beginPath();
                this.ctx.arc(particle.x, particle.y, particle.size + i * 5, 0, Math.PI * 2);
                this.ctx.stroke();
            }
        });
        
        this.ctx.globalAlpha = 1;
        requestAnimationFrame(() => this.animate());
    }
}

// ==================== MATRIX RAIN ====================

class MatrixRain {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        
        this.ctx = this.canvas.getContext('2d');
        this.resize();
        
        this.chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
        this.fontSize = 14;
        this.columns = 0;
        this.drops = [];
        
        window.addEventListener('resize', () => this.resize());
        this.init();
        this.animate();
    }
    
    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.columns = Math.floor(this.canvas.width / this.fontSize);
        this.drops = new Array(this.columns).fill(1);
    }
    
    init() {
        this.drops = new Array(this.columns).fill(1);
    }
    
    animate() {
        // Semi-transparent black to create fade effect
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.ctx.fillStyle = '#00d9ff';
        this.ctx.font = `${this.fontSize}px monospace`;
        
        for (let i = 0; i < this.drops.length; i++) {
            const char = this.chars[Math.floor(Math.random() * this.chars.length)];
            const x = i * this.fontSize;
            const y = this.drops[i] * this.fontSize;
            
            this.ctx.fillText(char, x, y);
            
            // Reset drop to top randomly
            if (y > this.canvas.height && Math.random() > 0.975) {
                this.drops[i] = 0;
            }
            
            this.drops[i]++;
        }
        
        setTimeout(() => requestAnimationFrame(() => this.animate()), 50);
    }
}

// ==================== SCAN LINE ====================

function createScanLine() {
    const scanLine = document.createElement('div');
    scanLine.className = 'scan-line';
    document.body.appendChild(scanLine);
}

// ==================== NUMBER COUNTER ANIMATION ====================

function animateCounter(element, target, duration = 1000) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current);
    }, 16);
}

// ==================== COUNTDOWN TIMER ====================

function startCountdown(element, seconds) {
    let remaining = seconds;
    
    function update() {
        const hours = Math.floor(remaining / 3600);
        const minutes = Math.floor((remaining % 3600) / 60);
        const secs = remaining % 60;
        
        element.innerHTML = `
            <span>${String(hours).padStart(2, '0')}</span>:
            <span>${String(minutes).padStart(2, '0')}</span>:
            <span>${String(secs).padStart(2, '0')}</span>
        `;
        
        if (remaining > 0) {
            remaining--;
            setTimeout(update, 1000);
        }
    }
    
    update();
}

// ==================== RIPPLE EFFECT ====================

function createRipple(e, button) {
    const ripple = document.createElement('span');
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;
    
    ripple.style.width = ripple.style.height = `${size}px`;
    ripple.style.left = `${x}px`;
    ripple.style.top = `${y}px`;
    ripple.classList.add('ripple');
    
    button.appendChild(ripple);
    
    setTimeout(() => ripple.remove(), 600);
}

// Add CSS for ripple
const style = document.createElement('style');
style.textContent = `
    .neon-btn, .scan-btn {
        position: relative;
        overflow: hidden;
    }
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple-animation 0.6s ease-out;
        pointer-events: none;
    }
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ==================== INPUT PARTICLE TRAIL ====================

function handleInputFocus(input) {
    input.addEventListener('focus', () => {
        input.classList.add('typing');
    });
    
    input.addEventListener('blur', () => {
        input.classList.remove('typing');
    });
    
    input.addEventListener('input', () => {
        if (input.value) {
            input.classList.add('typing');
        } else {
            input.classList.remove('typing');
        }
    });
}

// ==================== SCAN EXPLOSION EFFECT ====================

function createScanExplosion() {
    const explosion = document.createElement('div');
    explosion.className = 'scan-explosion';
    document.body.appendChild(explosion);
    
    setTimeout(() => explosion.remove(), 1000);
}

// ==================== TYPING EFFECT ====================

function typeWriter(element, text, speed = 50) {
    let i = 0;
    element.textContent = '';
    
    function type() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    
    type();
}

// ==================== GLITCH TEXT EFFECT ====================

function glitchText(element) {
    const text = element.textContent;
    const chars = '!<>-_\\/[]{}—=+*^?#________';
    
    let iterations = 0;
    const maxIterations = text.length;
    
    const interval = setInterval(() => {
        element.textContent = text
            .split('')
            .map((char, index) => {
                if (index < iterations) {
                    return text[index];
                }
                return chars[Math.floor(Math.random() * chars.length)];
            })
            .join('');
        
        if (iterations >= maxIterations) {
            clearInterval(interval);
        }
        
        iterations += 1 / 3;
    }, 30);
}

// ==================== NETWORK SIGNAL ANIMATION ====================

function animateSignalBar(element, percentage) {
    element.style.width = '0%';
    
    setTimeout(() => {
        element.style.width = percentage + '%';
    }, 100);
}

// ==================== MODAL FUNCTIONS ====================

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
}

// ==================== INITIALIZATION ====================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize particle systems
    new ParticleSystem('particleCanvas');
    
    // Initialize matrix rain (if on login screen)
    const matrixCanvas = document.getElementById('matrixCanvas');
    if (matrixCanvas) {
        new MatrixRain('matrixCanvas');
    }
    
    // Create scanning line
    createScanLine();
    
    // Add ripple effect to all buttons
    document.querySelectorAll('.neon-btn, .scan-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            createRipple(e, button);
        });
    });
    
    // Handle input particle trails
    document.querySelectorAll('.cyber-input').forEach(input => {
        handleInputFocus(input);
    });
    
    // Add glitch effect to glitch elements on hover
    document.querySelectorAll('.glitch').forEach(element => {
        element.addEventListener('mouseenter', () => {
            glitchText(element);
        });
    });
    
    // Close modals when clicking outside
    document.querySelectorAll('.cyber-modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal(modal.id);
            }
        });
    });
    
    console.log('🎮 Cyberpunk theme initialized');
    console.log('🤖 CyberSentry AI - Tarun, Shivam, Yash');
});

// ==================== EXPORT FUNCTIONS ====================

window.CyberFX = {
    animateCounter,
    startCountdown,
    createScanExplosion,
    typeWriter,
    glitchText,
    animateSignalBar,
    openModal,
    closeModal
};
