/**
 * Analysis Form Handler and Results Display
 */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('analysisForm');
    const resultsSection = document.getElementById('resultsSection');
    
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Show loading
            showLoading();
            
            // Gather form data
            const formData = {
                title: document.getElementById('title').value || 'Untitled',
                language: document.getElementById('language').value,
                form: document.getElementById('form').value || null,
                text: document.getElementById('text').value,
                strictness: parseInt(document.getElementById('strictness').value)
            };
            
            try {
                // Send to API
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                if (!response.ok) {
                    throw new Error('Analysis failed: ' + response.statusText);
                }
                
                const result = await response.json();
                
                // Display results
                displayResults(result);
                
            } catch (error) {
                alert('Error: ' + error.message);
                console.error('Analysis error:', error);
            } finally {
                hideLoading();
            }
        });
    }
});

function displayResults(result) {
    const resultsSection = document.getElementById('resultsSection');
    if (!resultsSection) return;

    // Handle different response structures
    const data = result.data || result;
    const evaluation = data.evaluation || {};
    const ratings = evaluation.ratings || {};
    const quantitative = data.quantitative_metrics || data.quantitative || {};
    const prosody = data.prosody_analysis || data.prosody || {};
    const literaryDevices = data.literary_devices || data.literary_devices || {};
    
    // Get overall score from various possible locations
    const overallScore = ratings.overall_quality || evaluation.overall_score || data.overall_score || 0;

    // Build results HTML
    let html = `
        <div class="bg-white rounded-2xl shadow-xl p-8 mb-8 slide-up">
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-3xl font-bold text-gray-800">
                    <i class="fas fa-chart-bar text-primary mr-3"></i>
                    Analysis Results
                </h2>
                ${createRatingBadge(overallScore)}
            </div>

            <div class="mb-6">
                <h3 class="text-xl font-semibold text-gray-700 mb-2">${data.title || 'Untitled'}</h3>
                <p class="text-gray-600">${data.executive_summary || 'Analysis completed.'}</p>
            </div>

            <!-- Ratings Grid -->
            <div class="grid md:grid-cols-7 gap-4 mb-8">
                ${createRatingCard('Technical Craft', ratings.technical_craft || evaluation.technical_craft_score || 0)}
                ${createRatingCard('Language', ratings.language_diction || evaluation.language_diction_score || 0)}
                ${createRatingCard('Imagery', ratings.imagery_voice || evaluation.imagery_voice_score || 0)}
                ${createRatingCard('Emotion', ratings.emotional_impact || evaluation.emotional_impact_score || 0)}
                ${createRatingCard('Culture', ratings.cultural_fidelity || evaluation.cultural_fidelity_score || 0)}
                ${createRatingCard('Originality', ratings.originality || evaluation.originality_score || 0)}
                ${createRatingCard('Greatness', ratings.computational_greatness || 0)}
            </div>
    `;

    // Add quantitative metrics if available
    if (quantitative && Object.keys(quantitative).length > 0) {
        html += `
            <div class="mb-8">
                <h3 class="text-2xl font-bold text-gray-800 mb-4">
                    <i class="fas fa-calculator text-accent mr-2"></i>
                    Quantitative Metrics
                </h3>
                <div class="grid md:grid-cols-3 gap-4">
                    ${createMetricCard('Lexical Density', (quantitative.lexical_density || 0).toFixed(1) + '%', 'Content words %')}
                    ${createMetricCard('TTR', (quantitative.type_token_ratio || quantitative.ttr || 0).toFixed(3), '0-1 scale')}
                    ${createMetricCard('MTLD', (quantitative.mtld || 0).toFixed(1), 'Higher = diverse')}
                    ${createMetricCard('Readability', (quantitative.flesch_reading_ease || quantitative.flesch_kincaid || 0).toFixed(1), '0-100 scale')}
                    ${createMetricCard('Avg Syllables', (quantitative.avg_syllables_per_word || 0).toFixed(2), 'Syllable count')}
                    ${createMetricCard('Lines', quantitative.total_lines || quantitative.line_count || 0, 'Line count')}
                </div>
            </div>
        `;
    }

    // Add prosody if available
    if (prosody && Object.keys(prosody).length > 0) {
        const meter = prosody.meter || {};
        const rhyme = prosody.rhyme || {};
        html += `
            <div class="mb-8">
                <h3 class="text-2xl font-bold text-gray-800 mb-4">
                    <i class="fas fa-music text-secondary mr-2"></i>
                    Prosody Analysis
                </h3>
                <div class="bg-gray-50 rounded-lg p-4">
                    <p class="text-gray-700"><strong>Detected Meter:</strong> ${meter.detected_meter || 'Free verse'}</p>
                    <p class="text-gray-700"><strong>Regularity:</strong> ${formatNumber((meter.metrical_regularity || 0) * 100)}%</p>
                    <p class="text-gray-700"><strong>Rhyme Scheme:</strong> ${rhyme.detected_scheme || 'None detected'}</p>
                    <p class="text-gray-700"><strong>Rhyme Density:</strong> ${formatNumber((rhyme.rhyme_density || 0) * 100)}%</p>
                </div>
            </div>
        `;
    }

    const advanced = data.advanced || {};
    if (advanced && Object.keys(advanced).length > 0) {
        const tpcastt = advanced.tp_castt || null;
        const touchstone = advanced.touchstone || null;
        const swift = advanced.swift || null;
        
        html += `<div class="mb-8">
            <h3 class="text-2xl font-bold text-gray-800 mb-4">
                <i class="fas fa-microscope text-purple-600 mr-2"></i>
                Advanced Frameworks
            </h3>
            <div class="space-y-4">`;
            
        if (tpcastt) {
            html += `
                <div class="bg-purple-50 rounded-lg p-4 border-l-4 border-purple-500">
                    <h4 class="font-bold text-purple-800 mb-2">TP-CASTT Analysis</h4>
                    <p class="text-sm text-gray-700"><strong>Theme:</strong> ${tpcastt.theme || ''}</p>
                    <p class="text-sm text-gray-700"><strong>Attitude:</strong> ${tpcastt.attitude || ''}</p>
                </div>
            `;
        }
        
        if (swift) {
            html += `
                <div class="bg-blue-50 rounded-lg p-4 border-l-4 border-blue-500">
                    <h4 class="font-bold text-blue-800 mb-2">SWIFT Analysis</h4>
                    <p class="text-sm text-gray-700"><strong>Word Choice:</strong> ${swift.word_choice?.vocabulary_level || ''}</p>
                    <p class="text-sm text-gray-700"><strong>Theme:</strong> ${swift.theme || ''}</p>
                </div>
            `;
        }
        
        if (touchstone) {
            html += `
                <div class="bg-indigo-50 rounded-lg p-4 border-l-4 border-indigo-500">
                    <h4 class="font-bold text-indigo-800 mb-2">Touchstone Method</h4>
                    <p class="text-sm text-gray-700">${touchstone.overall_assessment || ''}</p>
                </div>
            `;
        }
        
        html += `</div></div>`;
    }

    // Add strengths
    const strengths = evaluation.strengths || [];
    if (strengths.length > 0) {
        html += `
            <div class="mb-8">
                <h3 class="text-2xl font-bold text-gray-800 mb-4">
                    <i class="fas fa-star text-yellow-500 mr-2"></i>
                    Strengths
                </h3>
                <div class="space-y-3">
                    ${strengths.map(s => `
                        <div class="bg-green-50 border-l-4 border-green-500 p-4 rounded">
                            <p class="font-semibold text-green-800">${s.category || 'Strength'}</p>
                            <p class="text-green-700">${s.description || s}</p>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    // Add suggestions
    const suggestions = evaluation.suggestions || [];
    if (suggestions.length > 0) {
        html += `
            <div class="mb-8">
                <h3 class="text-2xl font-bold text-gray-800 mb-4">
                    <i class="fas fa-lightbulb text-blue-500 mr-2"></i>
                    Suggestions
                </h3>
                <div class="space-y-3">
                    ${suggestions.map(s => `
                        <div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
                            <p class="font-semibold text-blue-800">Priority ${s.priority || 'Medium'}: ${s.category || 'Improvement'}</p>
                            <p class="text-blue-700">${s.description || s}</p>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    // Add publishability
    const publishability = evaluation.publishability || {};
    if (publishability.assessment || publishability.status) {
        html += `
            <div class="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-6">
                <h3 class="text-xl font-bold text-gray-800 mb-3">
                    <i class="fas fa-publish text-purple-600 mr-2"></i>
                    Publishability
                </h3>
                <p class="text-gray-700 mb-4">${publishability.assessment || publishability.status || 'N/A'}</p>
                ${publishability.recommended_venues && publishability.recommended_venues.length > 0 ? `
                    <div class="flex flex-wrap gap-2">
                        ${publishability.recommended_venues.map(v => `
                            <span class="bg-white px-3 py-1 rounded-full text-sm font-semibold shadow-sm">${v}</span>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }

    html += `</div>`;

    resultsSection.innerHTML = html;
    resultsSection.classList.remove('hidden');

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function createRatingCard(label, score) {
    return `
        <div class="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg p-4 text-center">
            <div class="text-sm text-gray-600 mb-2">${label}</div>
            <div class="text-3xl font-bold text-primary">${formatNumber(score)}</div>
            <div class="text-xs text-gray-500">/ 10</div>
        </div>
    `;
}

function createMetricCard(label, value, description) {
    return `
        <div class="bg-gray-50 rounded-lg p-4">
            <div class="text-sm text-gray-600 mb-1">${label}</div>
            <div class="text-2xl font-bold text-accent">${value !== undefined ? value : 'N/A'}</div>
            <div class="text-xs text-gray-500">${description}</div>
        </div>
    `;
}

function createRatingBadge(score) {
    if (score === undefined || score === null) return '';
    
    let colorClass = 'bg-red-500';
    if (score >= 8) colorClass = 'bg-green-500';
    else if (score >= 6) colorClass = 'bg-yellow-500';
    else if (score >= 4) colorClass = 'bg-orange-500';

    return `
        <span class="${colorClass} text-white px-4 py-2 rounded-full font-bold text-sm shadow-lg">
            Score: ${Number(score).toFixed(1)}/10
        </span>
    `;
}

function formatNumber(num, decimals = 2) {
    if (num === undefined || num === null) return 'N/A';
    return Number(num).toFixed(decimals);
}

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
