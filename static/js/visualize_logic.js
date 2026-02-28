{% extends "admin/base_admin.html" %}

{% block title %}Visualize - Poetry Analyzer{% endblock %}

{% block content %}
<div class="max-w-7xl mx-auto">
    <!-- Page Header -->
    <div class="flex justify-between items-center mb-8">
        <div>
            <h1 class="text-3xl font-bold text-gray-800 mb-2">Visual Analysis</h1>
            <p class="text-gray-600 text-lg">Interactive data visualizations for literary patterns</p>
        </div>
        <div class="flex gap-4">
            <button onclick="loadRecentAnalyses()" class="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition">
                <i class="fas fa-sync-alt"></i>
            </button>
        </div>
    </div>

    <!-- Selection Bar -->
    <div class="bg-white rounded-2xl shadow-lg p-6 mb-8 border border-blue-50">
        <div class="flex flex-col md:flex-row gap-6 items-end">
            <div class="flex-1">
                <label class="block text-sm font-bold text-gray-700 mb-2 uppercase tracking-wider">Select Analysis ID</label>
                <div class="flex gap-2">
                    <input type="text" id="analysisId" placeholder="Enter Analysis UUID..." class="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:outline-none">
                    <button onclick="loadVisualization()" class="bg-primary text-white px-6 py-2 rounded-lg font-bold hover:bg-blue-700 transition">
                        Load Visuals
                    </button>
                </div>
            </div>
            <div class="flex-1">
                <label class="block text-sm font-bold text-gray-700 mb-2 uppercase tracking-wider">Quick Select (Recent)</label>
                <div id="recentAnalyses" class="flex flex-wrap gap-2">
                    <!-- Recent analysis buttons -->
                </div>
            </div>
        </div>
    </div>

    <!-- Loading State -->
    <div id="loadingViz" class="hidden py-20 text-center">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent mb-4"></div>
        <p class="text-xl text-gray-600">Generating interactive visualizations...</p>
    </div>

    <!-- Main Visualization Container -->
    <div id="vizContainer" class="hidden space-y-8">
        
        <!-- Top Row: Overview -->
        <div class="bg-gradient-to-br from-primary to-indigo-700 rounded-2xl shadow-xl p-8 text-white">
            <div class="flex flex-col md:flex-row justify-between items-center gap-6">
                <div>
                    <h2 class="text-3xl font-black mb-2" id="vizTitle">Analysis Overview</h2>
                    <p class="text-blue-100 text-lg opacity-90 max-w-2xl" id="execSummary">Loading summary...</p>
                </div>
                <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 text-center border border-white/20 min-w-[150px]">
                    <div class="text-6xl font-black mb-1" id="overallScore">0.0</div>
                    <div class="text-blue-100 font-bold uppercase tracking-widest text-xs">Total Score</div>
                </div>
            </div>
        </div>

        <!-- Row 1: Quality & Publishability -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div class="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
                <h3 class="text-xl font-bold text-gray-800 mb-6 flex items-center">
                    <i class="fas fa-star text-yellow-500 mr-2"></i> Quality Ratings Radar
                </h3>
                <div class="relative h-[400px]">
                    <canvas id="ratingsRadar"></canvas>
                </div>
            </div>
            
            <div class="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
                <h3 class="text-xl font-bold text-gray-800 mb-6 flex items-center">
                    <i class="fas fa-clipboard-check text-green-500 mr-2"></i> Publishability Status
                </h3>
                <div id="publishabilityContent" class="space-y-6">
                    <!-- Dynamic content -->
                </div>
            </div>
        </div>

        <!-- Row 2: Lexical Metrics -->
        <div class="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
            <h3 class="text-xl font-bold text-gray-800 mb-8 flex items-center">
                <i class="fas fa-book text-blue-500 mr-2"></i> Lexical Diversity & Vocabulary
            </h3>
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
                <div class="text-center p-4 bg-blue-50 rounded-xl border border-blue-100">
                    <div class="text-2xl font-black text-blue-600" id="ttrValue">0</div>
                    <div class="text-[10px] text-gray-500 font-bold uppercase mt-1">TTR</div>
                </div>
                <div class="text-center p-4 bg-purple-50 rounded-xl border border-purple-100">
                    <div class="text-2xl font-black text-purple-600" id="mattrValue">0</div>
                    <div class="text-[10px] text-gray-500 font-bold uppercase mt-1">MATTR</div>
                </div>
                <div class="text-center p-4 bg-emerald-50 rounded-xl border border-emerald-100">
                    <div class="text-2xl font-black text-emerald-600" id="mtldValue">0</div>
                    <div class="text-[10px] text-gray-500 font-bold uppercase mt-1">MTLD</div>
                </div>
                <div class="text-center p-4 bg-amber-50 rounded-xl border border-amber-100">
                    <div class="text-2xl font-black text-amber-600" id="yulesValue">0</div>
                    <div class="text-[10px] text-gray-500 font-bold uppercase mt-1">Yule's K</div>
                </div>
                <div class="text-center p-4 bg-rose-50 rounded-xl border border-rose-100">
                    <div class="text-2xl font-black text-rose-600" id="densityValue">0%</div>
                    <div class="text-[10px] text-gray-500 font-bold uppercase mt-1">Density</div>
                </div>
                <div class="text-center p-4 bg-indigo-50 rounded-xl border border-indigo-100">
                    <div class="text-2xl font-black text-indigo-600" id="hapaxValue">0</div>
                    <div class="text-[10px] text-gray-500 font-bold uppercase mt-1">Hapax</div>
                </div>
            </div>
            <div class="relative h-[300px]">
                <canvas id="lexicalChart"></canvas>
            </div>
        </div>

        <!-- Row 3: Prosody & Rhythm -->
        <div class="bg-white rounded-2xl shadow-xl p-8 border border-gray-100" id="matraContainer">
            <div class="flex justify-between items-center mb-8">
                <h3 class="text-xl font-bold text-gray-800 flex items-center">
                    <i class="fas fa-wave-square text-orange-500 mr-2"></i> Prosodic Rhythm (Matras/Line)
                </h3>
                <div class="flex gap-6">
                    <div class="text-center">
                        <div class="text-lg font-black text-orange-600" id="avgMatra">0</div>
                        <div class="text-[10px] uppercase font-bold text-gray-400">Average</div>
                    </div>
                    <div class="text-center">
                        <div class="text-lg font-black text-orange-600" id="regularity">0%</div>
                        <div class="text-[10px] uppercase font-bold text-gray-400">Regularity</div>
                    </div>
                </div>
            </div>
            <div class="relative h-[250px]">
                <canvas id="matraChart"></canvas>
            </div>
        </div>

        <!-- Row 4: Syllables and Word Length -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div class="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
                <h3 class="text-xl font-bold text-gray-800 mb-6 flex items-center">
                    <i class="fas fa-chart-pie text-pink-500 mr-2"></i> Syllable Distribution
                </h3>
                <div class="relative h-[350px]">
                    <canvas id="syllableChart"></canvas>
                </div>
            </div>
            <div class="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
                <h3 class="text-xl font-bold text-gray-800 mb-6 flex items-center">
                    <i class="fas fa-text-height text-cyan-500 mr-2"></i> Word Length Distribution
                </h3>
                <div class="relative h-[350px]">
                    <canvas id="wordLengthChart"></canvas>
                </div>
            </div>
        </div>

        <!-- Row 5: Navarasa Analysis -->
        <div class="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
            <h3 class="text-xl font-bold text-gray-800 mb-8 flex items-center">
                <i class="fas fa-spa text-emerald-500 mr-2"></i> Navarasa (Classical Aesthetic Emotions)
            </h3>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                <div class="relative h-[450px]">
                    <canvas id="rasaRadar"></canvas>
                </div>
                <div class="grid grid-cols-3 gap-3" id="rasaLegend">
                    <!-- Dynamic legend -->
                </div>
            </div>
        </div>

        <!-- Row 6: Sentiment and Literary Devices -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div class="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
                <h3 class="text-xl font-bold text-gray-800 mb-6 flex items-center">
                    <i class="fas fa-heart text-rose-500 mr-2"></i> Sentiment Arc
                </h3>
                <div class="grid grid-cols-4 gap-4 mb-6">
                    <div class="text-center p-3 bg-green-50 rounded-xl">
                        <div class="text-lg font-bold text-green-600" id="joyScore">0</div>
                        <div class="text-[10px] uppercase font-bold text-gray-400">Joy</div>
                    </div>
                    <div class="text-center p-3 bg-blue-50 rounded-xl">
                        <div class="text-lg font-bold text-blue-600" id="sadnessScore">0</div>
                        <div class="text-[10px] uppercase font-bold text-gray-400">Sad</div>
                    </div>
                    <div class="text-center p-3 bg-red-50 rounded-xl">
                        <div class="text-lg font-bold text-red-600" id="angerScore">0</div>
                        <div class="text-[10px] uppercase font-bold text-gray-400">Anger</div>
                    </div>
                    <div class="text-center p-3 bg-purple-50 rounded-xl">
                        <div class="text-lg font-bold text-purple-600" id="loveScore">0</div>
                        <div class="text-[10px] uppercase font-bold text-gray-400">Love</div>
                    </div>
                </div>
                <div class="relative h-[250px]">
                    <canvas id="sentimentArcChart"></canvas>
                </div>
            </div>

            <div class="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
                <h3 class="text-xl font-bold text-gray-800 mb-6 flex items-center">
                    <i class="fas fa-palette text-indigo-500 mr-2"></i> Literary Ornamentation
                </h3>
                <div id="literaryDevicesContent" class="grid grid-cols-1 gap-4">
                    <!-- Dynamic content -->
                </div>
            </div>
        </div>

        <!-- Row 7: Readability & Structure -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div class="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
                <h3 class="text-xl font-bold text-gray-800 mb-6 flex items-center">
                    <i class="fas fa-graduation-cap text-blue-600 mr-2"></i> Readability Assessment
                </h3>
                <div class="grid grid-cols-2 gap-4">
                    <div class="p-4 bg-blue-50 rounded-xl border border-blue-100">
                        <div class="text-xs text-gray-500 font-bold uppercase mb-1">Flesch Ease</div>
                        <div class="text-2xl font-black text-blue-600" id="fleschScore">0</div>
                    </div>
                    <div class="p-4 bg-purple-50 rounded-xl border border-purple-100">
                        <div class="text-xs text-gray-500 font-bold uppercase mb-1">FK Grade</div>
                        <div class="text-2xl font-black text-purple-600" id="fkGrade">0</div>
                    </div>
                    <div class="p-4 bg-emerald-50 rounded-xl border border-emerald-100">
                        <div class="text-xs text-gray-500 font-bold uppercase mb-1">Fog Index</div>
                        <div class="text-2xl font-black text-emerald-600" id="gunningFog">0</div>
                    </div>
                    <div class="p-4 bg-amber-50 rounded-xl border border-amber-100">
                        <div class="text-xs text-gray-500 font-bold uppercase mb-1">Average Grade</div>
                        <div class="text-2xl font-black text-amber-600" id="avgGrade">0</div>
                    </div>
                </div>
            </div>

            <div class="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
                <h3 class="text-xl font-bold text-gray-800 mb-6 flex items-center">
                    <i class="fas fa-ruler-combined text-gray-600 mr-2"></i> Architecture
                </h3>
                <div class="grid grid-cols-2 gap-4">
                    <div class="p-4 bg-gray-50 rounded-xl text-center">
                        <div class="text-2xl font-black text-gray-700" id="totalLines">0</div>
                        <div class="text-[10px] font-bold uppercase text-gray-400">Total Lines</div>
                    </div>
                    <div class="p-4 bg-gray-50 rounded-xl text-center">
                        <div class="text-2xl font-black text-gray-700" id="totalWords">0</div>
                        <div class="text-[10px] font-bold uppercase text-gray-400">Total Words</div>
                    </div>
                    <div class="p-4 bg-gray-50 rounded-xl text-center">
                        <div class="text-2xl font-black text-gray-700" id="totalSyllables">0</div>
                        <div class="text-[10px] font-bold uppercase text-gray-400">Syllables</div>
                    </div>
                    <div class="p-4 bg-gray-50 rounded-xl text-center">
                        <div class="text-2xl font-black text-gray-700" id="endStopped">0%</div>
                        <div class="text-[10px] font-bold uppercase text-gray-400">End-Stopped</div>
                    </div>
                </div>
            </div>
        </div>

    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
let charts = {};

// Load recent analyses for quick selection
async function loadRecentAnalyses() {
    try {
        const response = await axios.get('/api/results?limit=5');
        const data = response.data;
        const results = data.success ? data.data.results : data.results;
        
        const container = document.getElementById('recentAnalyses');
        if (!results || results.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-sm">No recent analyses</p>';
            return;
        }
        
        container.innerHTML = results.map(r => `
            <button onclick="selectAnalysis('${r.uuid}')" 
                class="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition text-sm font-bold">
                <i class="fas fa-file-alt mr-2"></i>${r.title || 'Untitled'}
            </button>
        `).join('');
    } catch (error) {
        console.error('Error loading recent:', error);
    }
}

function selectAnalysis(uuid) {
    document.getElementById('analysisId').value = uuid;
    loadVisualization();
}

async function loadVisualization() {
    const uuid = document.getElementById('analysisId').value.trim();
    if (!uuid) {
        showToast('Please enter or select an analysis ID', 'warning');
        return;
    }

    document.getElementById('loadingViz').classList.remove('hidden');
    document.getElementById('vizContainer').classList.add('hidden');
    
    try {
        // Get full result data
        const response = await axios.get(`/api/result/${uuid}`);
        const result = response.data.success ? response.data.data : response.data;
        
        renderVisualization(result);
        
        document.getElementById('loadingViz').classList.add('hidden');
        document.getElementById('vizContainer').classList.remove('hidden');
        showToast('Visualization loaded successfully!', 'success');
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('loadingViz').classList.add('hidden');
        showToast('Failed to load visualization. Check UUID.', 'error');
    }
}

function renderVisualization(result) {
    // Destroy previous charts
    Object.values(charts).forEach(c => c.destroy());
    charts = {};
    
    const qm = result.quantitative_metrics || result.quantitative || {};
    const eval = result.evaluation || {};
    
    // Header Info
    document.getElementById('vizTitle').textContent = result.title || 'Untitled Analysis';
    document.getElementById('execSummary').textContent = result.executive_summary || eval.executive_summary || 'No summary available';
    document.getElementById('overallScore').textContent = (result.overall_score || eval.overall_score || 0).toFixed(1);
    
    // Core Visualizations
    renderRatingsRadar(eval.ratings || {});
    renderPublishability(eval.publishability || {});
    renderLexicalMetrics(qm);
    renderSyllableChart(qm.syllable_metrics || {});
    renderWordLengthChart(qm.word_metrics || {});
    renderMatraAnalysis(result.prosody_analysis || {});
    renderRasaDistribution(result.literary_devices?.rasa_vector || {});
    renderSentimentArc(result.sentiment_analysis || {});
    renderLiteraryDevices(result.literary_devices || {});
    renderReadability(qm.readability_metrics || {});
    renderStructural(qm.structural_metrics || {}, qm.syllable_metrics || {}, result);
}

function renderRatingsRadar(ratings) {
    const ctx = document.getElementById('ratingsRadar').getContext('2d');
    const labels = [
        'Technical', 'Language', 'Imagery', 'Impact', 'Culture', 'Originality', 'Greatness'
    ];
    const data = [
        ratings.technical_craft || 0,
        ratings.language_diction || 0,
        ratings.imagery_voice || 0,
        ratings.emotional_impact || 0,
        ratings.cultural_fidelity || 0,
        ratings.originality || 0,
        ratings.computational_greatness || 0
    ];

    charts.ratings = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Score Profile',
                data: data,
                backgroundColor: 'rgba(59, 130, 246, 0.2)',
                borderColor: '#3b82f6',
                pointBackgroundColor: '#3b82f6',
                pointBorderColor: '#fff',
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 10,
                    ticks: { display: false }
                }
            }
        }
    });
}

function renderPublishability(p) {
    const container = document.getElementById('publishabilityContent');
    const color = p.ready ? 'green' : 'amber';
    container.innerHTML = `
        <div class="p-4 bg-${color}-50 border border-${color}-100 rounded-xl">
            <div class="flex items-center mb-3">
                <i class="fas ${p.ready ? 'fa-check-circle text-green-500' : 'fa-exclamation-circle text-amber-500'} text-2xl mr-3"></i>
                <div class="font-black text-lg text-${color}-800">${p.ready ? 'Market Ready' : 'Developmental Stage'}</div>
            </div>
            <p class="text-sm text-${color}-700 leading-relaxed">${p.assessment || 'Draft assessment.'}</p>
        </div>
        <div class="grid grid-cols-3 gap-3">
            <div class="text-center p-2 rounded-lg bg-gray-50 border">
                <div class="text-[10px] uppercase font-bold text-gray-400">Edits</div>
                <div class="font-bold text-xs">${p.needs_light_edits ? 'Yes' : 'No'}</div>
            </div>
            <div class="text-center p-2 rounded-lg bg-gray-50 border">
                <div class="text-[10px] uppercase font-bold text-gray-400">Revision</div>
                <div class="font-bold text-xs">${p.needs_heavy_revision ? 'Yes' : 'No'}</div>
            </div>
            <div class="text-center p-2 rounded-lg bg-gray-50 border">
                <div class="text-[10px] uppercase font-bold text-gray-400">Rework</div>
                <div class="font-bold text-xs">${p.major_rework_required ? 'Yes' : 'No'}</div>
            </div>
        </div>
    `;
}

function renderLexicalMetrics(qm) {
    const lex = qm.lexical_metrics || {};
    document.getElementById('ttrValue').textContent = (lex.type_token_ratio || 0).toFixed(3);
    document.getElementById('mattrValue').textContent = (lex.mattr || 0).toFixed(3);
    document.getElementById('mtldValue').textContent = Math.round(lex.mtld || 0);
    document.getElementById('yulesValue').textContent = (lex.yules_k || 0).toFixed(1);
    document.getElementById('densityValue').textContent = (lex.lexical_density || 0).toFixed(1) + '%';
    document.getElementById('hapaxValue').textContent = qm.word_metrics?.hapax_legomena || 0;
    
    const ctx = document.getElementById('lexicalChart').getContext('2d');
    charts.lexical = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Density', 'Content Ratio', 'Lexical Weight'],
            datasets: [{
                data: [lex.lexical_density || 0, (lex.content_word_ratio || 0) * 100, (lex.herdans_c || 0) * 100],
                backgroundColor: ['#3b82f6', '#8b5cf6', '#10b981']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } }
        }
    });
}

function renderSyllableChart(syllable) {
    const dist = syllable.syllable_distribution || {};
    const ctx = document.getElementById('syllableChart').getContext('2d');
    charts.syllable = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['1 Syllable', '2 Syllables', '3 Syllables', '4+ Syllables'],
            datasets: [{
                data: [
                    dist['1'] || 0,
                    dist['2'] || 0,
                    dist['3'] || 0,
                    Object.entries(dist).reduce((acc, [k, v]) => parseInt(k) >= 4 ? acc + v : acc, 0)
                ],
                backgroundColor: ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom' } }
        }
    });
}

function renderWordLengthChart(word) {
    const dist = word.word_length_distribution || {};
    const labels = Object.keys(dist).sort((a,b) => a-b);
    const ctx = document.getElementById('wordLengthChart').getContext('2d');
    charts.wordLength = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels.map(l => `${l}ch`),
            datasets: [{
                label: 'Frequency',
                data: labels.map(l => dist[l]),
                backgroundColor: '#6366f1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } }
        }
    });
}

function renderMatraAnalysis(prosody) {
    const meter = prosody.meter || {};
    const matraCounts = meter.matra_counts || [];
    
    if (matraCounts.length === 0) {
        document.getElementById('matraContainer').style.display = 'none';
        return;
    }
    
    document.getElementById('matraContainer').style.display = 'block';
    document.getElementById('avgMatra').textContent = (matraCounts.reduce((a, b) => a + b, 0) / matraCounts.length).toFixed(1);
    document.getElementById('regularity').textContent = Math.round((meter.metrical_regularity || 0) * 100) + '%';
    
    const ctx = document.getElementById('matraChart').getContext('2d');
    charts.matra = new Chart(ctx, {
        type: 'line',
        data: {
            labels: matraCounts.map((_, i) => `L${i + 1}`),
            datasets: [{
                label: 'Matra Count',
                data: matraCounts,
                borderColor: '#f97316',
                backgroundColor: 'rgba(249, 115, 22, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

function renderRasaDistribution(rasaData) {
    // Robust data path selection for the rasa vector
    const vector = rasaData.rasa_vector || rasaData || {};
    const ctx = document.getElementById('rasaRadar').getContext('2d');
    const labels = Object.keys(vector).map(k => k.toUpperCase());
    const data = Object.values(vector);

    if (labels.length > 0) {
        charts.rasa = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Aesthetic Intensity',
                    data: data,
                    backgroundColor: 'rgba(16, 185, 129, 0.2)',
                    borderColor: '#10b981',
                    pointBackgroundColor: '#10b981'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: { r: { beginAtZero: true, max: 1, ticks: { display: false } } }
            }
        });
        
        // Populate Legend
        const legend = document.getElementById('rasaLegend');
        legend.innerHTML = Object.entries(vector).map(([k, v]) => `
            <div class="flex flex-col items-center p-2 bg-gray-50 rounded-xl border ${k === rasaData.dominant_rasa ? 'border-emerald-500 bg-emerald-50' : 'border-gray-100'}">
                <span class="text-[8px] font-black text-gray-400 uppercase">${k.substring(0, 4)}</span>
                <span class="font-black text-gray-800 text-xs">${(v * 100).toFixed(0)}%</span>
            </div>
        `).join('');
        
        document.getElementById('dominantRasaLabel').textContent = rasaData.dominant_rasa || 'None detected';
    }
}

function renderSentimentArc(sentiment) {
    const arc = sentiment.sentiment_arc || [];
    const emotions = sentiment.emotion_distribution || {};
    
    document.getElementById('joyScore').textContent = (emotions.joy || 0).toFixed(2);
    document.getElementById('sadnessScore').textContent = (emotions.sadness || 0).toFixed(2);
    document.getElementById('angerScore').textContent = (emotions.anger || 0).toFixed(2);
    document.getElementById('loveScore').textContent = (emotions.love || 0).toFixed(2);
    
    if (arc.length > 0) {
        const ctx = document.getElementById('sentimentArcChart').getContext('2d');
        charts.sentiment = new Chart(ctx, {
            type: 'line',
            data: {
                labels: arc.map((_, i) => `L${i + 1}`),
                datasets: [{
                    label: 'Valence',
                    data: arc,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
}

function renderLiteraryDevices(literary) {
    const container = document.getElementById('literaryDevicesContent');
    const schemes = literary.schemes || {};
    const tropes = literary.tropes || {};
    const alankar = literary.sanskrit_alankar || {};
    
    const countItems = (obj) => Object.values(obj).reduce((sum, arr) => sum + (Array.isArray(arr) ? arr.length : 0), 0);
    
    container.innerHTML = `
        <div class="flex justify-between items-center p-4 bg-gray-50 rounded-xl">
            <span class="font-bold text-gray-600">Schemes & Structures</span>
            <span class="text-xl font-black text-blue-600">${countItems(schemes)}</span>
        </div>
        <div class="flex justify-between items-center p-4 bg-gray-50 rounded-xl">
            <span class="font-bold text-gray-600">Figurative Tropes</span>
            <span class="text-xl font-black text-purple-600">${countItems(tropes)}</span>
        </div>
        <div class="flex justify-between items-center p-4 bg-gray-50 rounded-xl">
            <span class="font-bold text-gray-600">Classical Alankars</span>
            <span class="text-xl font-black text-emerald-600">${countItems(alankar)}</span>
        </div>
    `;
}

function renderReadability(rm) {
    document.getElementById('fleschScore').textContent = (rm.flesch_reading_ease || 0).toFixed(1);
    document.getElementById('fkGrade').textContent = (rm.flesch_kincaid_grade || 0).toFixed(1);
    document.getElementById('gunningFog').textContent = (rm.gunning_fog || 0).toFixed(1);
    document.getElementById('avgGrade').textContent = (rm.average_grade_level || 0).toFixed(1);
}

function renderStructural(sm, syl, res) {
    document.getElementById('totalLines').textContent = sm.total_lines || res.line_count || 0;
    document.getElementById('totalWords').textContent = sm.total_words || res.word_count || 0;
    document.getElementById('totalSyllables').textContent = syl.total_syllables || 0;
    document.getElementById('endStopped').textContent = Math.round((sm.end_stopped_ratio || 0) * 100) + '%';
}

// Initialize
document.addEventListener('DOMContentLoaded', loadRecentAnalyses);
</script>
{% endblock %}
