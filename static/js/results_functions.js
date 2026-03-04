async function viewResultDetail(uuid) {
    showLoading('Loading full comprehensive report...');

    try {
        const response = await axios.get(`/result/${uuid}`);
        const result = response.data.data || response.data;

        // Store current result for JSON download
        window.currentAnalysisResult = result;

        const modalContent = document.getElementById('modalContent');

        // Extract nested data
        const qm = result.quantitative_metrics || result.quantitative || {};
        const prosody = result.prosody_analysis || result.prosody || {};
        const literary = result.literary_devices || {};
        const evalData = result.evaluation || {};
        const ratingsData = evalData.ratings || {};

        // Detailed mapping for ratings to ensure NO zeros if data exists
        const ratings = {
            overall: result.overall_score || evalData.overall_score || 0,
            technical: result.technical_craft_score || ratingsData.technical_craft || 0,
            language: result.language_diction_score || ratingsData.language_diction || 0,
            imagery: result.imagery_voice_score || ratingsData.imagery_voice || 0,
            impact: result.emotional_impact_score || ratingsData.emotional_impact || 0,
            culture: result.cultural_fidelity_score || ratingsData.cultural_fidelity || 0,
            originality: result.originality_score || ratingsData.originality || 0,
            greatness: result.computational_greatness_score || ratingsData.computational_greatness || qm.computational_greatness_score || 0
        };

        // Nested metric extraction
        const lm = qm.lexical_metrics || {};
        const sm = qm.structural_metrics || {};
        const rm = qm.readability_metrics || {};
        const wm = qm.word_metrics || {};

        modalContent.innerHTML = `
            <div class="space-y-8">
                <!-- Header Card -->
                <div class="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-100">
                    <div class="flex justify-between items-start">
                        <div>
                            <h3 class="text-3xl font-bold text-gray-900">${result.title || 'Untitled'}</h3>
                            <div class="flex gap-3 mt-3">
                                <span class="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-semibold">
                                    <svg class="icon mr-1" aria-hidden="true"><use href="#icon-globe"></use></svg> ${result.language || 'en'}
                                </span>
                                <span class="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-semibold">
                                    <svg class="icon mr-1" aria-hidden="true"><use href="#icon-scroll"></use></svg> ${result.poetic_form || result.form || 'Auto-detected'}
                                </span>
                            </div>
                        </div>
                        <div class="text-right">
                            <div class="text-5xl font-black text-primary">${Number(ratings.overall).toFixed(1)}</div>
                            <div class="text-gray-500 font-bold uppercase tracking-wider text-xs">Overall Score</div>
                        </div>
                    </div>
                </div>

                <!-- Text Content -->
                <div class="bg-white rounded-xl border p-6 shadow-sm">
                    <h4 class="text-sm font-bold text-gray-400 uppercase tracking-widest mb-4">Original Text</h4>
                    <div class="font-serif text-xl leading-relaxed text-gray-800 whitespace-pre-line italic border-l-4 border-gray-200 pl-6">${result.text || ''}</div>
                </div>

                <!-- Executive Summary -->
                <div class="bg-blue-50 rounded-xl p-6 border-l-8 border-primary">
                    <h4 class="font-bold text-primary mb-2 flex items-center">
                        <svg class="icon mr-2" aria-hidden="true"><use href="#icon-quote-left"></use></svg> Executive Summary
                    </h4>
                    <p class="text-gray-800 text-lg leading-relaxed">${result.executive_summary || evalData.executive_summary || 'Analysis completed.'}</p>
                </div>

                <!-- Quality Ratings Grid -->
                <div>
                    <h4 class="text-lg font-bold text-gray-800 mb-4 flex items-center">
                        <svg class="icon text-yellow-500 mr-2" aria-hidden="true"><use href="#icon-star"></use></svg> Quality Assessment
                    </h4>
                    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
                        ${renderRatingCard('Technical', ratings.technical)}
                        ${renderRatingCard('Language', ratings.language)}
                        ${renderRatingCard('Imagery', ratings.imagery)}
                        ${renderRatingCard('Impact', ratings.impact)}
                        ${renderRatingCard('Culture', ratings.culture)}
                        ${renderRatingCard('Originality', ratings.originality)}
                        ${renderRatingCard('Greatness', ratings.greatness)}
                        ${renderRatingCard('OVERALL', ratings.overall)}
                    </div>
                </div>

                <!-- Two Column Details -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <!-- Quantitative -->
                    <div class="bg-gray-50 rounded-2xl p-6 border border-gray-200">
                        <h4 class="font-bold text-gray-800 mb-4 flex items-center">
                            <svg class="icon text-purple-600 mr-2" aria-hidden="true"><use href="#icon-calculator"></use></svg> Quantitative Metrics
                        </h4>
                        <div class="grid grid-cols-2 gap-4">
                            ${renderDetailItem('Total Words', wm.total_words || qm.total_words || result.word_count)}
                            ${renderDetailItem('Total Lines', sm.total_lines || qm.total_lines || result.line_count)}
                            ${renderDetailItem('Lexical Density', (lm.lexical_density || qm.lexical_density || 0).toFixed(1) + '%')}
                            ${renderDetailItem('TTR (Richness)', (lm.type_token_ratio || qm.type_token_ratio || 0).toFixed(3))}
                            ${renderDetailItem('Readability', (rm.flesch_reading_ease || qm.flesch_reading_ease || 0).toFixed(1))}
                            ${renderDetailItem('Grade Level', (rm.flesch_kincaid_grade || qm.flesch_kincaid_grade || 0).toFixed(1))}
                        </div>
                    </div>

                    <!-- Prosody -->
                    <div class="bg-gray-50 rounded-2xl p-6 border border-gray-200">
                        <h4 class="font-bold text-gray-800 mb-4 flex items-center">
                            <svg class="icon text-red-600 mr-2" aria-hidden="true"><use href="#icon-music"></use></svg> Prosody & Meter
                        </h4>
                        <div class="grid grid-cols-2 gap-4">
                            ${renderDetailItem('Meter Type', prosody.meter?.detected_meter || prosody.detected_meter || 'Free Verse')}
                            ${renderDetailItem('Foot Pattern', prosody.meter?.foot_pattern || prosody.meter?.foot_count || 'N/A')}
                            ${renderDetailItem('Rhyme Scheme', prosody.rhyme?.detected_scheme || prosody.rhyme_scheme || 'None')}
                            ${renderDetailItem('Metrical Reg.', (prosody.meter?.metrical_regularity || prosody.metrical_regularity || 0).toFixed(2))}
                        </div>
                        <div class="mt-4 pt-4 border-t border-gray-200">
                            <p class="text-xs font-bold text-gray-400 uppercase mb-2">Scansion (Matras/Stress)</p>
                            <p class="font-mono text-sm bg-white p-2 rounded border truncate" title="View in JSON for full scansion">${formatScansion(prosody.scansion || prosody.meter?.scansion)}</p>
                        </div>
                    </div>
                </div>

                <!-- AI Emotional Nuance (Transformer Analysis) -->
                ${result.additional?.transformer_analysis?.emotions ? `
                <div class="bg-white rounded-[2rem] shadow-xl p-8 border border-rose-100 border-l-8 border-l-rose-500">
                    <h3 class="text-xl font-bold text-gray-800 mb-6 flex items-center">
                        <svg class="icon text-rose-500 mr-3" aria-hidden="true"><use href="#icon-brain"></use></svg> AI Emotional Nuance (Transformer Vectors)
                    </h3>
                    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                        ${Object.entries(result.additional.transformer_analysis.emotions).map(([emotion, score]) => `
                            <div class="p-4 rounded-2xl bg-rose-50 border border-rose-100 text-center">
                                <div class="text-[10px] font-black text-rose-300 uppercase tracking-widest mb-1">${emotion}</div>
                                <div class="text-2xl font-black text-rose-600">${(score * 100).toFixed(1)}%</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                ` : ''}

                <!-- Deep Linguistic Vectors -->
                ${linguistic.text_descriptives ? `
                <div class="bg-white rounded-[2rem] shadow-xl p-8 border border-indigo-100">
                    <h3 class="text-xl font-bold text-gray-800 mb-6 flex items-center">
                        <svg class="icon text-indigo-500 mr-3" aria-hidden="true"><use href="#icon-microscope"></use></svg> Deep Linguistic Vectors
                    </h3>
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
                        ${renderDetailItem('Avg. Dep. Distance', linguistic.text_descriptives.dependency_distance_mean?.toFixed(2))}
                        ${renderDetailItem('Proper Noun Ratio', (linguistic.text_descriptives.propn_ratio * 100)?.toFixed(1) + '%')}
                        ${renderDetailItem('Noun Content Ratio', (linguistic.text_descriptives.noun_ratio * 100)?.toFixed(1) + '%')}
                        ${renderDetailItem('Verb Content Ratio', (linguistic.text_descriptives.verb_ratio * 100)?.toFixed(1) + '%')}
                    </div>
                </div>
                ` : ''}

                <!-- Literary Devices -->
                <div class="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm">
                    <h4 class="font-bold text-gray-800 mb-4 flex items-center">
                        <svg class="icon text-orange-500 mr-2" aria-hidden="true"><use href="#icon-palette"></use></svg> Literary Devices & Tropes
                    </h4>
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                        ${renderDetailItem('Metaphors', literary.tropes?.metaphor?.length || 0)}
                        ${renderDetailItem('Similes', literary.tropes?.simile?.length || 0)}
                        ${renderDetailItem('Imagery Types', Object.keys(literary.imagery || {}).length)}
                        ${renderDetailItem('Sanskrit Alankars', Object.keys(literary.sanskrit_alankar || {}).length)}
                    </div>
                    
                    <!-- Rasa Analysis -->
                    ${literary.rasa_vector ? `
                    <div class="mt-6 pt-6 border-t border-gray-100">
                        <p class="text-sm font-bold text-gray-800 mb-4">Navarasa Distribution</p>
                        <div class="grid grid-cols-3 md:grid-cols-9 gap-2">
                            ${Object.entries(literary.rasa_vector.rasa_vector || {}).map(([rasa, score]) => `
                                <div class="text-center p-2 rounded bg-gray-50 border ${rasa === literary.rasa_vector.dominant_rasa ? 'border-primary ring-1 ring-primary' : 'border-gray-100'}">
                                    <div class="text-[10px] font-bold text-gray-400 uppercase">${rasa.substring(0, 4)}</div>
                                    <div class="text-xs font-black text-gray-700">${(score * 100).toFixed(0)}%</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    ` : ''}
                </div>

                <!-- Footer Info -->
                <div class="flex justify-between items-center text-xs text-gray-400 border-t pt-6">
                    <div>UUID: ${result.uuid}</div>
                    <div>Analyzed on: ${formatDate(result.created_at)}</div>
                </div>
            </div>
        `;

        hideLoading();
        const modal = document.getElementById('viewModal');
        if (modal && !modal.open) {
            modal.showModal();
        }

    } catch (error) {
        console.error('Error loading result:', error);
        hideLoading();
        showToast('Failed to load comprehensive report', 'error');
    }
}

function renderRatingCard(label, score) {
    const s = parseFloat(score) || 0;
    const color = getScoreColor(s);
    return `
        <div class="bg-white border rounded-xl p-3 text-center shadow-sm">
            <div class="text-xl font-black ${color}">${s.toFixed(1)}</div>
            <div class="text-[10px] text-gray-500 uppercase font-bold mt-1">${label}</div>
        </div>
    `;
}

function renderDetailItem(label, value) {
    return `
        <div>
            <p class="text-[10px] text-gray-400 font-bold uppercase tracking-wider">${label}</p>
            <p class="text-lg font-bold text-gray-700">${value !== undefined && value !== null ? value : 'N/A'}</p>
        </div>
    `;
}

function formatScansion(scansion) {
    if (!scansion) return 'N/A';
    if (Array.isArray(scansion)) {
        if (scansion.length > 0 && scansion[0].matras !== undefined) {
            return scansion.map(s => s.matras).join(' | ');
        }
        return scansion.length + ' lines scanned';
    }
    return scansion;
}

function downloadResultsAsJSON() {
    const data = window.currentAnalysisResult;
    if (!data) {
        showToast('No analysis data loaded to download', 'warning');
        return;
    }

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analysis-${data.uuid || 'result'}.json`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    showToast('JSON Analysis Downloaded', 'success');
}
