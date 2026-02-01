/**
 * TikTok Viral Script Generator - Frontend Application v1.1
 * With live trends from X, TikTok, Google
 */

class TikTokScriptGenerator {
    constructor() {
        this.form = document.getElementById('scriptForm');
        this.generateBtn = document.getElementById('generateBtn');
        this.loadingEl = document.getElementById('loading');
        this.outputEl = document.getElementById('scriptOutput');
        this.ctaToggle = document.getElementById('ctaToggle');
        this.trendsContainer = document.getElementById('liveTrendsContainer');
        this.trendsUpdatedEl = document.getElementById('trendsUpdatedAt');
        this.locationTextEl = document.getElementById('locationText');

        this.currentTrends = null;
        this.currentSource = 'merged';

        this.init();
    }

    init() {
        // Form submission
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));

        // CTA toggle
        this.ctaToggle.addEventListener('click', () => this.toggleCTA());

        // Load live trends
        this.loadLiveTrends();

        // Trend tabs
        document.querySelectorAll('.trend-tab').forEach(tab => {
            tab.addEventListener('click', (e) => this.switchTrendSource(e.target));
        });

        // Refresh trends button
        document.getElementById('refreshTrends')?.addEventListener('click', () => {
            this.loadLiveTrends(true);
        });

        // Copy functionality
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('copy-btn')) {
                this.copyToClipboard(e.target);
            }
            if (e.target.classList.contains('hashtag')) {
                this.copyHashtag(e.target);
            }
        });

        // Auto-refresh trends every 30 minutes
        setInterval(() => this.loadLiveTrends(), 30 * 60 * 1000);
    }

    toggleCTA() {
        this.ctaToggle.classList.toggle('active');
    }

    async loadLiveTrends(forceRefresh = false) {
        this.trendsContainer.innerHTML = `
            <div class="trends-loading">
                <div class="spinner-small"></div>
                Chargement des tendances...
            </div>
        `;

        try {
            const response = await fetch('/api/trends/live');
            const data = await response.json();

            if (data.success) {
                this.currentTrends = data.trends;

                // Update location
                if (data.location && this.locationTextEl) {
                    this.locationTextEl.textContent = `${data.location.city}, ${data.location.country}`;
                }

                // Render trends
                this.renderTrends(this.currentSource);

                // Update timestamp
                if (this.trendsUpdatedEl) {
                    const date = new Date(data.updated_at);
                    this.trendsUpdatedEl.textContent = `Mis à jour: ${date.toLocaleTimeString('fr-FR')}`;
                }
            } else {
                this.trendsContainer.innerHTML = `
                    <div style="text-align: center; padding: 20px; color: var(--text-secondary);">
                        Impossible de charger les tendances
                    </div>
                `;
            }
        } catch (error) {
            console.error('Failed to load live trends:', error);
            this.trendsContainer.innerHTML = `
                <div style="text-align: center; padding: 20px; color: var(--text-secondary);">
                    Erreur de connexion
                </div>
            `;
        }
    }

    switchTrendSource(tab) {
        // Update active tab
        document.querySelectorAll('.trend-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        // Get source and render
        this.currentSource = tab.dataset.source;
        this.renderTrends(this.currentSource);
    }

    renderTrends(source) {
        if (!this.currentTrends) return;

        const trends = this.currentTrends[source] || [];

        if (trends.length === 0) {
            this.trendsContainer.innerHTML = `
                <div style="text-align: center; padding: 20px; color: var(--text-secondary);">
                    Aucune tendance disponible
                </div>
            `;
            return;
        }

        const sourceLabels = {
            'tiktok': 'TikTok',
            'x': '𝕏',
            'google': 'Google',
            'merged': ''
        };

        this.trendsContainer.innerHTML = trends.map((trend, i) => `
            <div class="live-trend-item" onclick="app.useTrend('${this.escapeTrendTerm(trend.term)}')">
                <div class="trend-rank">${i + 1}</div>
                <div class="trend-info">
                    <div class="trend-term">${trend.term}</div>
                    <div class="trend-meta">
                        ${source === 'merged' ? `<span class="trend-source">${sourceLabels[trend.source] || trend.source}</span>` : ''}
                        <span class="trend-category">${trend.category || 'general'}</span>
                        ${trend.volume ? `<span>${this.formatVolume(trend.volume)} posts</span>` : ''}
                    </div>
                </div>
            </div>
        `).join('');
    }

    escapeTrendTerm(term) {
        return term.replace(/'/g, "\\'").replace(/"/g, '\\"');
    }

    formatVolume(num) {
        if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
        if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
        return num.toString();
    }

    useTrend(term) {
        const topicEl = document.getElementById('topic');
        topicEl.value = term.replace('#', '');
        topicEl.focus();

        // Scroll to top of form
        topicEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    async handleSubmit(e) {
        e.preventDefault();

        // Get form data
        const formData = new FormData(this.form);
        const data = {
            topic: formData.get('topic'),
            niche: formData.get('niche'),
            hook_style: formData.get('hook_style'),
            length: formData.get('length'),
            target_audience: formData.get('target_audience') || null,
            tone: formData.get('tone') || null,
            include_cta: this.ctaToggle.classList.contains('active')
        };

        // Validate
        if (!data.topic || data.topic.length < 3) {
            this.showError('Veuillez entrer un sujet (minimum 3 caractères)');
            return;
        }

        // Show loading
        this.showLoading();

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                this.displayScript(result.script, result.generation_time_ms);
            } else {
                this.showError(result.error || 'Erreur lors de la génération');
            }
        } catch (error) {
            this.showError('Erreur de connexion au serveur');
            console.error(error);
        }

        this.hideLoading();
    }

    showLoading() {
        this.generateBtn.disabled = true;
        this.generateBtn.innerHTML = '<span class="spinner-small"></span> Génération en cours...';
        this.loadingEl.classList.add('visible');
        this.outputEl.classList.remove('visible');
    }

    hideLoading() {
        this.generateBtn.disabled = false;
        this.generateBtn.innerHTML = '✨ Générer le Script';
        this.loadingEl.classList.remove('visible');
    }

    displayScript(script, generationTime) {
        this.outputEl.classList.add('visible');
        this.outputEl.classList.add('fade-in');

        // Build sections
        const sections = ['hook', 'setup', 'content', 'payoff'];
        if (script.cta) sections.push('cta');

        let sectionsHTML = '';
        sections.forEach(name => {
            const section = script[name];
            if (section) {
                sectionsHTML += this.renderSection(name, section);
            }
        });

        // Build stats
        const statsHTML = `
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">${script.total_duration}s</div>
                    <div class="stat-label">Durée</div>
                </div>
                <div class="stat">
                    <div class="stat-value">${script.hook_score}/10</div>
                    <div class="stat-label">Score Hook</div>
                </div>
                <div class="stat">
                    <div class="stat-value">${generationTime}ms</div>
                    <div class="stat-label">Temps</div>
                </div>
            </div>
        `;

        // Build hashtags
        const hashtagsHTML = `
            <div class="hashtags">
                ${script.hashtags.map(h => `<span class="hashtag">${h}</span>`).join('')}
            </div>
        `;

        // Build tips
        const tipsHTML = script.tips.length > 0 ? `
            <div class="tips">
                <h4 style="margin-bottom: 15px; color: var(--text-secondary);">Conseils</h4>
                ${script.tips.map(tip => `
                    <div class="tip">
                        <span class="tip-icon">✓</span>
                        <span>${tip}</span>
                    </div>
                `).join('')}
            </div>
        ` : '';

        // Viral potential badge
        const potentialColor = script.viral_potential.includes('Excellent') ? 'var(--success)' :
                              script.viral_potential.includes('Bon') ? 'var(--tiktok-cyan)' : 'var(--warning)';

        this.outputEl.innerHTML = `
            <div class="card-title">
                <span class="icon">📝</span>
                Script Généré
                <span style="margin-left: auto; font-size: 0.9rem; color: ${potentialColor};">
                    ${script.viral_potential}
                </span>
            </div>

            <div style="position: relative;">
                <button class="copy-btn" data-full="true">📋 Copier tout</button>
                ${sectionsHTML}
            </div>

            ${statsHTML}
            ${hashtagsHTML}
            ${tipsHTML}
        `;

        // Scroll to output
        this.outputEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    renderSection(name, section) {
        const labels = {
            hook: 'HOOK',
            setup: 'SETUP',
            content: 'CONTENU',
            payoff: 'PAYOFF',
            cta: 'CALL TO ACTION'
        };

        return `
            <div class="script-section ${name}">
                <div class="section-header">
                    <span class="section-name">${labels[name]}</span>
                    <span class="section-timecode">${section.timecode}</span>
                </div>
                <div class="section-text">${section.text}</div>
                ${section.visual_notes ? `<div class="section-visual">💡 ${section.visual_notes}</div>` : ''}
            </div>
        `;
    }

    showError(message) {
        this.outputEl.classList.add('visible');
        this.outputEl.innerHTML = `
            <div style="text-align: center; padding: 40px; color: var(--tiktok-red);">
                <div style="font-size: 3rem; margin-bottom: 15px;">⚠️</div>
                <div style="font-size: 1.1rem;">${message}</div>
            </div>
        `;
    }

    copyToClipboard(btn) {
        // Get all script text
        const sections = document.querySelectorAll('.script-section');
        let fullText = '';

        sections.forEach(section => {
            const name = section.querySelector('.section-name').textContent;
            const timecode = section.querySelector('.section-timecode').textContent;
            const text = section.querySelector('.section-text').textContent;
            fullText += `[${timecode}] ${name}\n${text}\n\n`;
        });

        // Add hashtags
        const hashtags = document.querySelectorAll('.hashtag');
        if (hashtags.length > 0) {
            fullText += '\nHashtags: ';
            hashtags.forEach(h => fullText += h.textContent + ' ');
        }

        navigator.clipboard.writeText(fullText.trim()).then(() => {
            btn.textContent = '✓ Copié!';
            btn.classList.add('copied');
            setTimeout(() => {
                btn.textContent = '📋 Copier tout';
                btn.classList.remove('copied');
            }, 2000);
        });
    }

    copyHashtag(el) {
        navigator.clipboard.writeText(el.textContent).then(() => {
            const original = el.textContent;
            el.textContent = '✓ Copié';
            setTimeout(() => {
                el.textContent = original;
            }, 1000);
        });
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    window.app = new TikTokScriptGenerator();
});
