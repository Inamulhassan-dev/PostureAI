/**
 * main.js - Frontend JavaScript for Exercise Posture Analysis
 * Handles real-time dashboard updates and exercise switching
 */

let currentExercise = 'squat';
let lastRepCount = 0;
let updateInterval = null;

/**
 * Set the current exercise via API
 */
function setExercise(exercise) {
    currentExercise = exercise;

    fetch('/set_exercise', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ exercise: exercise })
    })
    .then(response => response.json())
    .then(data => {
        const nameEl = document.getElementById('exerciseName');
        if (nameEl) {
            nameEl.textContent = exercise.replace(/_/g, ' ')
                .replace(/\b\w/g, c => c.toUpperCase());
        }
        console.log('Exercise switched to:', data.exercise);
    })
    .catch(err => console.error('Set exercise error:', err));
}

/**
 * Change exercise from dropdown
 */
function changeExercise() {
    const select = document.getElementById('exerciseSelect');
    if (select) {
        setExercise(select.value);
        // Reset dashboard
        document.getElementById('repCount').textContent = '0';
        document.getElementById('stageBadge').textContent = 'READY';
        updateFormScore(100);
    }
}

/**
 * Reset rep counter
 */
function resetCounter() {
    fetch('/reset_counter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(() => {
        const repCountEl = document.getElementById('repCount');
        if (repCountEl) {
            // Animate reset
            repCountEl.style.transform = 'scale(0.8)';
            repCountEl.style.opacity = '0.5';
            setTimeout(() => {
                repCountEl.textContent = '0';
                repCountEl.style.transform = 'scale(1)';
                repCountEl.style.opacity = '1';
            }, 200);
        }
        lastRepCount = 0;
        console.log('Counter reset');
    })
    .catch(err => console.error('Reset error:', err));
}

/**
 * Update the form score display with animation
 */
function updateFormScore(score) {
    const formScoreEl = document.getElementById('formScore');
    const scoreFillEl = document.getElementById('scoreFill');
    const gaugeEl = document.getElementById('gaugeFill');
    const gaugeValueEl = document.getElementById('formScore');

    if (formScoreEl) formScoreEl.textContent = score;

    // Update progress bar
    if (scoreFillEl) {
        scoreFillEl.style.width = score + '%';
    }

    // Update SVG gauge
    if (gaugeEl) {
        const circumference = 2 * Math.PI * 50; // r=50
        const offset = circumference * (1 - score / 100);
        gaugeEl.style.strokeDashoffset = offset;
    }

    // Update colors based on score
    let color;
    if (score > 70) {
        color = '#00ff88';
    } else if (score > 40) {
        color = '#ff6b35';
    } else {
        color = '#ff2d78';
    }

    if (gaugeValueEl) gaugeValueEl.style.color = color;
    if (gaugeEl) gaugeEl.style.stroke = color;
}

/**
 * Render feedback list
 */
function renderFeedback(feedbackData) {
    const feedbackListEl = document.getElementById('feedbackList');
    if (!feedbackListEl) return;

    if (!feedbackData || feedbackData.length === 0) {
        feedbackListEl.innerHTML = `
            <div class="feedback-item fi-info">
                <i class="fas fa-circle-notch fa-spin"></i>
                <span>Waiting for pose detection...</span>
            </div>`;
        return;
    }

    feedbackListEl.innerHTML = '';

    feedbackData.forEach(item => {
        const div = document.createElement('div');
        let cssClass = 'fi-info';
        let icon = 'info-circle';

        if (item.type === 'correct') {
            cssClass = 'fi-correct';
            icon = 'check-circle';
        } else if (item.type === 'incorrect') {
            cssClass = 'fi-incorrect';
            icon = 'exclamation-circle';
        } else if (item.type === 'warning') {
            cssClass = 'fi-warning';
            icon = 'exclamation-triangle';
        }

        div.className = `feedback-item ${cssClass}`;
        div.innerHTML = `<i class="fas fa-${icon}"></i><span>${item.message}</span>`;
        feedbackListEl.appendChild(div);
    });
}

/**
 * Render joint angles as tiles
 */
function renderAngles(angles) {
    const anglesListEl = document.getElementById('anglesList');
    if (!anglesListEl) return;

    const angleKeys = Object.keys(angles || {});

    if (angleKeys.length === 0) {
        anglesListEl.innerHTML = `
            <div class="no-data-msg">
                <i class="fas fa-circle-notch fa-spin"></i>
                Waiting for detection...
            </div>`;
        return;
    }

    anglesListEl.innerHTML = '';
    angleKeys.forEach(key => {
        const div = document.createElement('div');
        div.className = 'angle-item';
        div.innerHTML = `
            <div class="angle-name">${key.replace(/_/g, ' ')}</div>
            <div class="angle-value">${angles[key]}°</div>
        `;
        anglesListEl.appendChild(div);
    });
}

/**
 * Update dashboard with latest analysis data
 */
function updateDashboard() {
    fetch('/get_analysis')
        .then(response => {
            if (!response.ok) throw new Error('Network error');
            return response.json();
        })
        .then(data => {
            // Update rep count with animation
            const repCountEl = document.getElementById('repCount');
            if (repCountEl) {
                const newCount = data.rep_count || 0;
                if (newCount !== lastRepCount && newCount > lastRepCount) {
                    // Flash animation on new rep
                    repCountEl.style.transform = 'scale(1.3)';
                    setTimeout(() => {
                        repCountEl.style.transform = 'scale(1)';
                    }, 300);
                }
                repCountEl.textContent = newCount;
                lastRepCount = newCount;
            }

            // Update stage badge
            const stageBadgeEl = document.getElementById('stageBadge');
            if (stageBadgeEl) {
                const stage = (data.stage || 'READY').toUpperCase();
                stageBadgeEl.textContent = stage;
            }

            // Update form score
            if (data.form_score !== undefined) {
                updateFormScore(data.form_score);
            }

            // Update feedback
            renderFeedback(data.feedback);

            // Update angles
            renderAngles(data.angles);
        })
        .catch(() => {
            // Silent fail to avoid console spam during polling
        });
}

// Initialize transition on rep number
document.addEventListener('DOMContentLoaded', () => {
    const repNumberEl = document.getElementById('repCount');
    if (repNumberEl) {
        repNumberEl.style.transition = 'transform 0.3s ease, opacity 0.3s ease, color 0.3s ease';
    }

    // Add SVG gradient definition for gauge
    const svg = document.getElementById('gaugeSvg');
    if (svg) {
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        defs.innerHTML = `
            <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" style="stop-color:#ff2d78"/>
                <stop offset="50%" style="stop-color:#ff6b35"/>
                <stop offset="100%" style="stop-color:#00ff88"/>
            </linearGradient>
        `;
        svg.prepend(defs);
    }
});
