/**
 * Main JavaScript for Ultimate Literary Master System
 */

// Strictness slider value display
document.addEventListener('DOMContentLoaded', function() {
    const strictnessSlider = document.getElementById('strictness');
    const strictnessValue = document.getElementById('strictnessValue');
    
    if (strictnessSlider && strictnessValue) {
        strictnessSlider.addEventListener('input', function() {
            strictnessValue.textContent = this.value;
        });
    }
});

// Loading overlay functions
function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.remove('hidden');
        overlay.classList.add('flex');
    }
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.add('hidden');
        overlay.classList.remove('flex');
    }
}

// Format numbers with proper decimals
function formatNumber(num, decimals = 2) {
    return Number(num).toFixed(decimals);
}

// Create rating badge
function createRatingBadge(score) {
    let colorClass = 'bg-red-500';
    if (score >= 8) colorClass = 'bg-green-500';
    else if (score >= 6) colorClass = 'bg-yellow-500';
    else if (score >= 4) colorClass = 'bg-orange-500';
    
    return `
        <span class="${colorClass} text-white px-3 py-1 rounded-full font-bold text-sm">
            ${formatNumber(score)}/10
        </span>
    `;
}
