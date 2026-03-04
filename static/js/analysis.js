/**
 * Analysis Form Handler and Results Display
 */

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('analysisForm');

    if (form) {
        form.addEventListener('submit', async function (e) {
            e.preventDefault();

            const formData = {
                title: document.getElementById('title').value || 'Untitled',
                language: document.getElementById('language').value,
                form: document.getElementById('form').value || null,
                text: document.getElementById('text').value,
                strictness: parseInt(document.getElementById('strictness').value)
            };

            if (!formData.text.trim()) {
                showToast('Please enter some text to analyze', 'warning');
                return;
            }

            showLoading('Analyzing your text with 70+ metrics...');

            try {
                const response = await axios.post('/analyze-run', formData);
                hideLoading();

                if (response.data && response.data.success) {
                    displayResults(response.data.data || response.data);
                    showToast('Analysis completed successfully!', 'success');
                } else {
                    const errorMsg = response.data?.message || response.data?.error || 'Analysis failed';
                    throw new Error(errorMsg);
                }

            } catch (error) {
                hideLoading();
                console.error('Analysis error:', error);
                const msg = error.response?.data?.message || error.response?.data?.error || error.message || 'Analysis failed';
                showToast(msg, 'error', 5000);
            }
        });
    }
});

function displayResults(data) {
    const modal = document.getElementById('resultsModal');
    const content = document.getElementById('resultsContent');
    if (!modal || !content) return;

    window.currentAnalysisResult = data;

    const result = data;
    const qm = result.quantitative_metrics || result.quantitative || {};
    const prosody = result.prosody_analysis || result.prosody || {};
    const literary = result.literary_devices || {};
    const evalData = result.evaluation || {};
    const ratings = evalData.ratings || {};

    content.innerHTML = `
        <div class="space-y-6">
            <!-- Header -->
            <div class="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6">
                <div class="flex justify-between items-start flex-wrap gap-4">
                    <div>
                        <h3 class="text-2xl font-bold text-gray-800">${result.title || 'Untitled'}</h3>
                        <p class="text-gray-600 mt-1">
                            <span class="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm mr-2">
                                <svg class="icon mr-1" aria-hidden="true"><use href="#icon-globe"></use></svg> ${result.language || 'en'}
                            </span>
                            <span class="inline-flex items-center px-2 py-1 bg-purple-100 text-purple-700 rounded text-sm mr-2">
                                <svg class="icon mr-1" aria-hidden="true"><use href="#icon-scroll"></use></svg> ${result.poetic_form || result.form || 'Auto-detected'}
                            </span>
                        </p>
                    </div>
                    <div class="text-right">
                        <div class="text-4xl font-bold text-primary">${(ratings.overall_quality || evalData.overall_score || result.overall_score || 0).toFixed(1)}</div>
                        <div class="text-gray-500 text-sm font-bold uppercase">Overall Score</div>
                    </div>
                </div>
            </div>

            <!-- Executive Summary -->
            <div class="bg-white rounded-xl shadow-lg p-6 border-l-4 border-primary">
                <h3 class="font-bold text-lg mb-2 text-gray-800">Executive Summary</h3>
                <p class="text-gray-700 leading-relaxed">${result.executive_summary || evalData.executive_summary || 'Analysis complete.'}</p>
            </div>

            <!-- Ratings -->
            <div class="bg-white rounded-xl shadow-lg p-6">
                <h3 class="font-bold text-lg mb-4 text-gray-800"><svg class="icon text-yellow-500 mr-2" aria-hidden="true"><use href="#icon-star"></use></svg>Quality Ratings</h3>
                <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
                    ${renderRatingCard('Technical', ratings.technical_craft || result.technical_craft_score)}
                    ${renderRatingCard('Language', ratings.language_diction || result.language_diction_score)}
                    ${renderRatingCard('Imagery', ratings.imagery_voice || result.imagery_voice_score)}
                    ${renderRatingCard('Impact', ratings.emotional_impact || result.emotional_impact_score)}
                    ${renderRatingCard('Culture', ratings.cultural_fidelity || result.cultural_fidelity_score)}
                    ${renderRatingCard('Originality', ratings.originality || result.originality_score)}
                    ${renderRatingCard('Greatness', ratings.computational_greatness || result.computational_greatness_score || result.computational_greatness || 0)}
                </div>
            </div>

            <!-- Quantitative -->
            <div class="bg-white rounded-xl shadow-lg p-6">
                <h3 class="font-bold text-lg mb-4 text-gray-800"><svg class="icon text-purple-500 mr-2" aria-hidden="true"><use href="#icon-calculator"></use></svg>Quantitative Metrics</h3>
                <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                    ${renderMetricCard('Words', qm.word_metrics?.total_words || qm.total_words || result.word_count)}
                    ${renderMetricCard('Unique', qm.word_metrics?.unique_words || qm.unique_words || result.unique_words)}
                    ${renderMetricCard('Lines', qm.structural_metrics?.total_lines || qm.total_lines || result.line_count)}
                    ${renderMetricCard('Sentences', qm.structural_metrics?.total_sentences || qm.total_sentences || result.sentence_count)}
                    ${renderMetricCard('TTR', qm.lexical_metrics?.type_token_ratio || qm.type_token_ratio || qm.ttr)}
                    ${renderMetricCard('Density', qm.lexical_metrics?.lexical_density || qm.lexical_density)}
                    ${renderMetricCard('Readability', qm.readability_metrics?.flesch_reading_ease || qm.flesch_reading_ease)}
                </div>
            </div>

            <!-- Prosody -->
            <div class="bg-white rounded-xl shadow-lg p-6">
                <h3 class="font-bold text-lg mb-4 text-gray-800"><svg class="icon text-red-500 mr-2" aria-hidden="true"><use href="#icon-music"></use></svg>Prosody & Meter</h3>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    ${renderMetricCard('Meter', prosody.meter?.detected_meter || prosody.detected_meter || 'Free Verse')}
                    ${renderMetricCard('Foot', prosody.meter?.foot_pattern || prosody.meter?.foot_count || 'N/A')}
                    ${renderMetricCard('Scheme', prosody.rhyme?.detected_scheme || prosody.rhyme_scheme || 'None')}
                    ${renderMetricCard('Scansion', formatScansion(prosody.scansion || prosody.meter?.scansion))}
                </div>
            </div>

            <!-- AI Emotional Nuance (Transformer Analysis) -->
            ${result.additional?.transformer_analysis?.emotions ? `
            <div class="bg-white rounded-xl shadow-lg p-6 border-l-4 border-rose-500">
                <h3 class="font-bold text-lg mb-4 text-gray-800">
                    <svg class="icon text-rose-500 mr-2" aria-hidden="true"><use href="#icon-brain"></use></svg> AI Emotional Nuance
                </h3>
                <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                    ${Object.entries(result.additional.transformer_analysis.emotions).map(([emotion, score]) => `
                        <div class="p-3 rounded-xl bg-rose-50 border border-rose-100 text-center">
                            <div class="text-xs font-black text-rose-400 uppercase tracking-widest mb-1">${emotion}</div>
                            <div class="text-xl font-black text-rose-600">${(score * 100).toFixed(1)}%</div>
                        </div>
                    `).join('')}
                </div>
                <div class="mt-4 p-4 bg-gray-50 rounded-xl text-sm italic text-gray-600">
                    <strong>Transformer Insight:</strong> The AI detects a dominant tone of 
                    <span class="font-bold text-rose-600 uppercase">${result.additional.transformer_analysis.dominant_emotion}</span> 
                    with ${result.additional.transformer_analysis.sentiment?.label} sentiment.
                </div>
            </div>
            ` : ''}

            <!-- Deep Linguistic Vectors (TextDescriptives) -->
            ${linguistic.text_descriptives ? `
            <div class="bg-white rounded-xl shadow-lg p-6">
                <h3 class="font-bold text-lg mb-4 text-gray-800">
                    <svg class="icon text-indigo-500 mr-2" aria-hidden="true"><use href="#icon-microscope"></use></svg> Deep Linguistic Vectors
                </h3>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    ${renderMetricCard('Dep. Distance', linguistic.text_descriptives.dependency_distance_mean)}
                    ${renderMetricCard('Prop. Nouns', linguistic.text_descriptives.propn_ratio)}
                    ${renderMetricCard('Noun Ratio', linguistic.text_descriptives.noun_ratio)}
                    ${renderMetricCard('Verb Ratio', linguistic.text_descriptives.verb_ratio)}
                </div>
            </div>
            ` : ''}

            <!-- Literary Devices -->
            <div class="bg-white rounded-xl shadow-lg p-6">
                <h3 class="font-bold text-lg mb-4 text-gray-800"><svg class="icon text-orange-500 mr-2" aria-hidden="true"><use href="#icon-palette"></use></svg>Literary Devices</h3>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    ${renderMetricCard('Metaphors', literary.tropes?.metaphor?.length || 0)}
                    ${renderMetricCard('Similes', literary.tropes?.simile?.length || 0)}
                    ${renderMetricCard('Imagery', Object.keys(literary.imagery || {}).length)}
                    ${renderMetricCard('Alankars', Object.keys(literary.sanskrit_alankar || {}).length)}
                </div>
            </div>

            <!-- Rasa -->
            ${literary.rasa_vector ? `
            <div class="bg-white rounded-xl shadow-lg p-6">
                <h3 class="font-bold text-lg mb-4 text-gray-800"><svg class="icon text-pink-500 mr-2" aria-hidden="true"><use href="#icon-spa"></use></svg>Navarasa Analysis</h3>
                <div class="grid grid-cols-3 md:grid-cols-5 lg:grid-cols-9 gap-2">
                    ${Object.entries(literary.rasa_vector.rasa_vector || {}).map(([rasa, score]) => `
                        <div class="p-2 text-center rounded bg-gray-50 border ${rasa === literary.rasa_vector.dominant_rasa ? 'border-primary ring-1 ring-primary' : 'border-gray-100'}">
                            <div class="text-[10px] font-bold text-gray-400 uppercase">${rasa}</div>
                            <div class="text-sm font-black text-gray-700">${(score * 100).toFixed(0)}%</div>
                        </div>
                    `).join('')}
                </div>
                <div class="mt-3 text-sm text-gray-600">
                    <strong>Dominant:</strong> ${literary.rasa_vector.dominant_rasa || 'N/A'}
                </div>
            </div>
            ` : ''}

            <!-- Strengths & Suggestions -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-green-50 rounded-xl p-6 border-l-4 border-green-500">
                    <h3 class="font-bold text-green-800 mb-3">Strengths</h3>
                    <ul class="space-y-2 text-sm text-green-700">
                        ${(evalData.strengths || []).map(s => `<li><svg class="icon mr-2" aria-hidden="true"><use href="#icon-check"></use></svg>${s.description || s}</li>`).join('') || '<li>No specific strengths identified</li>'}
                    </ul>
                </div>
                <div class="bg-blue-50 rounded-xl p-6 border-l-4 border-blue-500">
                    <h3 class="font-bold text-blue-800 mb-3">Suggestions</h3>
                    <ul class="space-y-2 text-sm text-blue-700">
                        ${(evalData.suggestions || []).map(s => `<li><svg class="icon mr-2" aria-hidden="true"><use href="#icon-lightbulb"></use></svg>${s.description || s}</li>`).join('') || '<li>No specific suggestions identified</li>'}
                    </ul>
                </div>
            </div>

            <!-- Footer Actions -->
            <div class="flex justify-between items-center pt-4 border-t">
                <button onclick="downloadResultsAsJSON()" class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition">
                    <svg class="icon mr-2" aria-hidden="true"><use href="#icon-download"></use></svg>Download JSON
                </button>
                <div class="flex gap-4">
                    <a href="${window.AppRoutes?.results || '/results'}" class="px-6 py-2 bg-primary text-white rounded-lg hover:bg-blue-700 transition">
                        <svg class="icon mr-2" aria-hidden="true"><use href="#icon-list"></use></svg>All Results
                    </a>
                    <button onclick="closeResults()" class="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition">
                        Close
                    </button>
                </div>
            </div>
        </div>
    `;

    if (!modal.open) {
        modal.showModal();
    }
}

function renderRatingCard(name, score) {
    const s = parseFloat(score) || 0;
    const color = getScoreColor(s);
    return `
        <div class="bg-gray-50 rounded-lg p-3 text-center border border-gray-100">
            <div class="text-xl font-black ${color}">${s.toFixed(1)}</div>
            <div class="text-[10px] text-gray-500 uppercase font-bold">${name}</div>
        </div>
    `;
}

function renderMetricCard(name, value) {
    let display = value;
    if (typeof value === 'number') display = value.toFixed(2);
    if (Array.isArray(value)) display = value.length;
    if (value === undefined || value === null || value === '') display = 'N/A';

    return `
        <div class="bg-gray-50 rounded-lg p-3 text-center border border-gray-100">
            <div class="text-lg font-bold text-gray-800 truncate" title="${value}">${display}</div>
            <div class="text-[10px] text-gray-500 uppercase font-bold">${name}</div>
        </div>
    `;
}

function formatScansion(scansion) {
    if (!scansion) return 'N/A';
    if (Array.isArray(scansion)) {
        if (scansion.length > 0 && scansion[0].matras !== undefined) {
            return scansion.map(s => s.matras).join(' | ');
        }
        return scansion.length + ' lines';
    }
    return scansion;
}

function closeResults() {
    const modal = document.getElementById('resultsModal');
    if (modal && modal.open) {
        modal.close();
    }
}

function downloadResultsAsJSON() {
    const data = window.currentAnalysisResult;
    if (!data) {
        showToast('No analysis data to download', 'warning');
        return;
    }
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analysis-${data.uuid || data.id || 'result'}.json`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    showToast('JSON Analysis Downloaded', 'success');
}
