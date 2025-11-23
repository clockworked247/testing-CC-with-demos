// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// Global chart instances
let priceChart = null;
let allocationChart = null;

// Tab Navigation
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tabId = btn.dataset.tab;

        // Update active tab button
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Update active tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabId).classList.add('active');

        // Load data when switching to certain tabs
        if (tabId === 'portfolio') {
            loadPortfolio();
        } else if (tabId === 'dashboard') {
            loadTopMovers();
        }
    });
});

// Currency Converter
async function convertCurrency() {
    const amount = document.getElementById('convert-amount').value;
    const from = document.getElementById('convert-from').value;
    const to = document.getElementById('convert-to').value;
    const resultDiv = document.getElementById('conversion-result');

    if (!amount || amount <= 0) {
        resultDiv.innerHTML = '<p class="error">Please enter a valid amount</p>';
        return;
    }

    resultDiv.innerHTML = '<p class="loading">Converting...</p>';

    try {
        const response = await fetch(
            `${API_BASE_URL}/api/rates/convert?amount=${amount}&from_currency=${from}&to_currency=${to}`
        );
        const data = await response.json();

        resultDiv.innerHTML = `
            <h3>${data.from.amount} ${data.from.currency} =</h3>
            <h2 style="color: var(--primary); font-size: 2rem;">${data.to.amount.toFixed(2)} ${data.to.currency}</h2>
            <p style="margin-top: 10px; color: var(--text-secondary);">
                Exchange Rate: 1 ${data.from.currency} = ${data.rate.toFixed(6)} ${data.to.currency}
            </p>
        `;
    } catch (error) {
        resultDiv.innerHTML = '<p class="error">Failed to convert currency</p>';
        console.error('Conversion error:', error);
    }
}

// Top Movers
async function loadTopMovers() {
    const moversDiv = document.getElementById('top-movers');
    moversDiv.innerHTML = '<p class="loading">Loading...</p>';

    const pairs = [
        ['EUR', 'USD'], ['USD', 'JPY'], ['GBP', 'USD'],
        ['USD', 'CHF'], ['AUD', 'USD']
    ];

    try {
        const movers = [];

        for (const [base, quote] of pairs) {
            const response = await fetch(`${API_BASE_URL}/api/historical/change/${base}/${quote}?hours=24`);
            if (response.ok) {
                const data = await response.json();
                movers.push({
                    pair: data.pair,
                    change: data.change_percent,
                    rate: data.current_rate
                });
            }
        }

        movers.sort((a, b) => Math.abs(b.change) - Math.abs(a.change));

        moversDiv.innerHTML = movers.map(mover => `
            <div class="mover-item">
                <span class="mover-pair">${mover.pair}</span>
                <span class="mover-change ${mover.change >= 0 ? 'positive' : 'negative'}">
                    ${mover.change >= 0 ? '+' : ''}${mover.change.toFixed(2)}%
                </span>
            </div>
        `).join('');
    } catch (error) {
        moversDiv.innerHTML = '<p class="error">Failed to load top movers</p>';
        console.error('Top movers error:', error);
    }
}

// Load Historical Chart
async function loadChart() {
    const base = document.getElementById('chart-base').value;
    const quote = document.getElementById('chart-quote').value;
    const days = document.getElementById('chart-period').value;

    try {
        const response = await fetch(`${API_BASE_URL}/api/historical/${base}/${quote}?days=${days}`);
        const data = await response.json();

        if (!data.data || data.data.length === 0) {
            alert('No historical data available');
            return;
        }

        const labels = data.data.map(d => new Date(d.timestamp).toLocaleDateString());
        const prices = data.data.map(d => d.rate);

        const ctx = document.getElementById('price-chart').getContext('2d');

        if (priceChart) {
            priceChart.destroy();
        }

        priceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: `${base}/${quote}`,
                    data: prices,
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false
                    }
                }
            }
        });
    } catch (error) {
        alert('Failed to load chart data');
        console.error('Chart error:', error);
    }
}

// Generate Trading Signal
async function generateSignal() {
    const base = document.getElementById('signal-base').value;
    const quote = document.getElementById('signal-quote').value;
    const useLLM = document.getElementById('signal-use-llm').checked;
    const resultDiv = document.getElementById('signal-result');

    resultDiv.innerHTML = '<p class="loading">Generating signal... This may take a moment.</p>';

    try {
        const response = await fetch(
            `${API_BASE_URL}/api/signals/${base}/${quote}?use_llm=${useLLM}`
        );
        const signal = await response.json();

        let html = `
            <div class="signal-badge ${signal.signal.toLowerCase()}">${signal.signal}</div>
            <h3>Strength: ${signal.strength.toFixed(1)}%</h3>
            <div class="strength-bar">
                <div class="strength-fill ${signal.signal.toLowerCase()}" style="width: ${signal.strength}%"></div>
            </div>
        `;

        if (signal.technical_analysis) {
            html += `
                <h4 style="margin-top: 20px;">Technical Analysis</h4>
                <p><strong>Signal:</strong> ${signal.technical_analysis.signal}</p>
                <p><strong>Reason:</strong> ${signal.technical_analysis.reason}</p>
                <h5>Indicators:</h5>
                <ul style="margin-left: 20px;">
                    <li>Current Price: ${signal.technical_analysis.indicators.current_price?.toFixed(4) || 'N/A'}</li>
                    <li>Short MA: ${signal.technical_analysis.indicators.short_ma?.toFixed(4) || 'N/A'}</li>
                    <li>Long MA: ${signal.technical_analysis.indicators.long_ma?.toFixed(4) || 'N/A'}</li>
                    <li>RSI: ${signal.technical_analysis.indicators.rsi?.toFixed(2) || 'N/A'}</li>
                    <li>MACD: ${signal.technical_analysis.indicators.macd?.toFixed(4) || 'N/A'}</li>
                </ul>
            `;
        }

        if (signal.llm_analysis) {
            html += `
                <h4 style="margin-top: 20px;">AI Analysis</h4>
                <div style="margin-top: 10px; line-height: 1.8;">
                    ${signal.llm_analysis.replace(/\n/g, '<br>')}
                </div>
            `;
        }

        resultDiv.innerHTML = html;
    } catch (error) {
        resultDiv.innerHTML = '<p class="error">Failed to generate signal</p>';
        console.error('Signal error:', error);
    }
}

// Scan for Opportunities
async function scanOpportunities() {
    const type = document.getElementById('scan-type').value;
    const strength = document.getElementById('scan-strength').value;
    const resultDiv = document.getElementById('scan-results');

    resultDiv.innerHTML = '<p class="loading">Scanning market for opportunities...</p>';

    try {
        const response = await fetch(
            `${API_BASE_URL}/api/signals/scan?signal_type=${type}&min_strength=${strength}`
        );
        const data = await response.json();

        if (data.opportunities.length === 0) {
            resultDiv.innerHTML = '<p>No opportunities found with the specified criteria.</p>';
            return;
        }

        resultDiv.innerHTML = data.opportunities.map(opp => `
            <div class="opportunity-item">
                <h4>${opp.currency_pair}</h4>
                <p><strong>Signal:</strong> ${opp.signal} | <strong>Strength:</strong> ${opp.strength.toFixed(1)}%</p>
                ${opp.technical_analysis ? `<p><strong>Reason:</strong> ${opp.technical_analysis.reason}</p>` : ''}
            </div>
        `).join('');
    } catch (error) {
        resultDiv.innerHTML = '<p class="error">Failed to scan opportunities</p>';
        console.error('Scan error:', error);
    }
}

// Load Recent Signals
async function loadRecentSignals() {
    const signalsDiv = document.getElementById('recent-signals');
    signalsDiv.innerHTML = '<p class="loading">Loading...</p>';

    try {
        const response = await fetch(`${API_BASE_URL}/api/signals/recent?limit=10`);
        const data = await response.json();

        if (data.signals.length === 0) {
            signalsDiv.innerHTML = '<p>No recent signals found.</p>';
            return;
        }

        signalsDiv.innerHTML = data.signals.map(signal => `
            <div class="opportunity-item">
                <h4>${signal.currency_pair}</h4>
                <p>
                    <strong>Signal:</strong> <span class="signal-badge ${signal.signal.toLowerCase()}">${signal.signal}</span>
                    | <strong>Strength:</strong> ${signal.strength.toFixed(1)}%
                </p>
                <p style="font-size: 0.9rem; color: var(--text-secondary);">
                    ${new Date(signal.timestamp).toLocaleString()}
                </p>
            </div>
        `).join('');
    } catch (error) {
        signalsDiv.innerHTML = '<p class="error">Failed to load signals</p>';
        console.error('Recent signals error:', error);
    }
}

// Portfolio Functions
async function addPosition(event) {
    event.preventDefault();

    const currency = document.getElementById('position-currency').value;
    const amount = document.getElementById('position-amount').value;
    const price = document.getElementById('position-price').value;
    const notes = document.getElementById('position-notes').value;

    try {
        const response = await fetch(
            `${API_BASE_URL}/api/portfolio/position?currency=${currency}&amount=${amount}&purchase_price_usd=${price}&notes=${encodeURIComponent(notes)}`,
            { method: 'POST' }
        );

        if (response.ok) {
            alert('Position added successfully!');
            document.getElementById('add-position-form').reset();
            loadPortfolio();
        } else {
            alert('Failed to add position');
        }
    } catch (error) {
        alert('Error adding position');
        console.error('Add position error:', error);
    }
}

async function loadPortfolio() {
    const summaryDiv = document.getElementById('portfolio-summary');
    const positionsDiv = document.getElementById('portfolio-positions');

    summaryDiv.innerHTML = '<p class="loading">Loading...</p>';
    positionsDiv.innerHTML = '<p class="loading">Loading...</p>';

    try {
        const response = await fetch(`${API_BASE_URL}/api/portfolio`);
        const portfolio = await response.json();

        // Summary
        summaryDiv.innerHTML = `
            <div class="summary-item">
                <span class="summary-label">Total Value:</span>
                <span class="summary-value">$${portfolio.total_value_usd.toFixed(2)}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Total Invested:</span>
                <span class="summary-value">$${portfolio.total_invested_usd.toFixed(2)}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Total P&L:</span>
                <span class="summary-value ${portfolio.total_pnl_usd >= 0 ? 'positive' : 'negative'}">
                    ${portfolio.total_pnl_usd >= 0 ? '+' : ''}$${portfolio.total_pnl_usd.toFixed(2)}
                    (${portfolio.total_pnl_percent >= 0 ? '+' : ''}${portfolio.total_pnl_percent.toFixed(2)}%)
                </span>
            </div>
        `;

        // Positions
        if (portfolio.positions.length === 0) {
            positionsDiv.innerHTML = '<p>No positions in portfolio.</p>';
        } else {
            positionsDiv.innerHTML = portfolio.positions.map(pos => `
                <div class="position-item">
                    <div class="position-header">
                        <span class="position-currency">${pos.currency}</span>
                        <span class="position-pnl ${pos.pnl_usd >= 0 ? 'positive' : 'negative'}">
                            ${pos.pnl_usd >= 0 ? '+' : ''}$${pos.pnl_usd.toFixed(2)}
                        </span>
                    </div>
                    <p><strong>Amount:</strong> ${pos.amount}</p>
                    <p><strong>Purchase Price:</strong> $${pos.purchase_price.toFixed(6)}</p>
                    <p><strong>Current Price:</strong> $${pos.current_price.toFixed(6)}</p>
                    <p><strong>Current Value:</strong> $${pos.current_value_usd.toFixed(2)}</p>
                    <p><strong>P&L:</strong> ${pos.pnl_percent >= 0 ? '+' : ''}${pos.pnl_percent.toFixed(2)}%</p>
                    ${pos.notes ? `<p style="font-style: italic; margin-top: 10px;">${pos.notes}</p>` : ''}
                </div>
            `).join('');
        }

        // Load allocation chart
        loadAllocationChart(portfolio);
    } catch (error) {
        summaryDiv.innerHTML = '<p class="error">Failed to load portfolio</p>';
        positionsDiv.innerHTML = '';
        console.error('Portfolio error:', error);
    }
}

function loadAllocationChart(portfolio) {
    if (portfolio.positions.length === 0) return;

    const currencies = {};
    portfolio.positions.forEach(pos => {
        if (currencies[pos.currency]) {
            currencies[pos.currency] += pos.current_value_usd;
        } else {
            currencies[pos.currency] = pos.current_value_usd;
        }
    });

    const labels = Object.keys(currencies);
    const data = Object.values(currencies);

    const ctx = document.getElementById('allocation-chart').getContext('2d');

    if (allocationChart) {
        allocationChart.destroy();
    }

    allocationChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
                    '#ec4899', '#14b8a6', '#f97316', '#06b6d4', '#84cc16'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${context.label}: $${value.toFixed(2)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// AI Analysis Functions
async function getAIAnalysis() {
    const base = document.getElementById('analysis-base').value;
    const quote = document.getElementById('analysis-quote').value;
    const resultDiv = document.getElementById('ai-analysis-result');

    resultDiv.innerHTML = '<p class="loading">Generating AI analysis... This may take 30-60 seconds.</p>';

    try {
        const response = await fetch(
            `${API_BASE_URL}/api/analysis/currency-pair?base=${base}&quote=${quote}`,
            { method: 'POST' }
        );
        const data = await response.json();

        resultDiv.innerHTML = `
            <h3>${data.currency_pair} Analysis</h3>
            <div style="margin-top: 20px; line-height: 1.8;">
                ${data.ai_analysis.replace(/\n/g, '<br>')}
            </div>
        `;
    } catch (error) {
        resultDiv.innerHTML = '<p class="error">Failed to generate AI analysis. Make sure OpenRouter API key is configured.</p>';
        console.error('AI analysis error:', error);
    }
}

async function getDailySummary() {
    const resultDiv = document.getElementById('daily-summary');
    resultDiv.innerHTML = '<p class="loading">Generating daily summary... This may take 30-60 seconds.</p>';

    try {
        const response = await fetch(`${API_BASE_URL}/api/analysis/daily-summary`);
        const data = await response.json();

        let html = `
            <h3>Market Summary - ${data.date}</h3>
            <h4 style="margin-top: 20px;">Top Movers:</h4>
            <ul style="margin-left: 20px;">
        `;

        data.top_movers.forEach(mover => {
            html += `<li>${mover.pair}: ${mover.change_pct >= 0 ? '+' : ''}${mover.change_pct.toFixed(2)}%</li>`;
        });

        html += `</ul>`;

        if (data.upcoming_events.length > 0) {
            html += `<h4 style="margin-top: 20px;">Upcoming Events:</h4><ul style="margin-left: 20px;">`;
            data.upcoming_events.forEach(event => {
                html += `<li>${event}</li>`;
            });
            html += `</ul>`;
        }

        html += `
            <h4 style="margin-top: 20px;">AI Summary:</h4>
            <div style="margin-top: 10px; line-height: 1.8;">
                ${data.ai_summary.replace(/\n/g, '<br>')}
            </div>
        `;

        resultDiv.innerHTML = html;
    } catch (error) {
        resultDiv.innerHTML = '<p class="error">Failed to generate daily summary. Make sure OpenRouter API key is configured.</p>';
        console.error('Daily summary error:', error);
    }
}

async function getFundamentals() {
    const currency = document.getElementById('fundamentals-currency').value;
    const resultDiv = document.getElementById('fundamentals-result');

    resultDiv.innerHTML = '<p class="loading">Loading fundamentals... This may take 30-60 seconds.</p>';

    try {
        const response = await fetch(`${API_BASE_URL}/api/analysis/fundamentals/${currency}`);
        const data = await response.json();

        resultDiv.innerHTML = `
            <h3>${data.currency} Fundamentals</h3>
            <div style="margin-top: 20px; line-height: 1.8;">
                ${data.explanation.replace(/\n/g, '<br>')}
            </div>
        `;
    } catch (error) {
        resultDiv.innerHTML = '<p class="error">Failed to load fundamentals. Make sure OpenRouter API key is configured.</p>';
        console.error('Fundamentals error:', error);
    }
}

// News Functions
async function loadNews() {
    const newsDiv = document.getElementById('news-list');
    newsDiv.innerHTML = '<p class="loading">Loading news...</p>';

    try {
        const response = await fetch(`${API_BASE_URL}/api/news?use_mock=true`);
        const data = await response.json();

        if (data.articles.length === 0) {
            newsDiv.innerHTML = '<p>No news articles available.</p>';
            return;
        }

        newsDiv.innerHTML = data.articles.map(article => `
            <div class="news-item">
                <div class="news-title">${article.title}</div>
                <div class="news-meta">
                    ${article.source} | ${article.published_date ? new Date(article.published_date).toLocaleString() : 'Recent'}
                </div>
                ${article.url ? `<a href="${article.url}" target="_blank" style="color: var(--primary);">Read more →</a>` : ''}
            </div>
        `).join('');
    } catch (error) {
        newsDiv.innerHTML = '<p class="error">Failed to load news</p>';
        console.error('News error:', error);
    }
}

async function loadEconomicCalendar() {
    const calendarDiv = document.getElementById('economic-calendar');
    calendarDiv.innerHTML = '<p class="loading">Loading calendar...</p>';

    try {
        const response = await fetch(`${API_BASE_URL}/api/news/calendar`);
        const data = await response.json();

        if (data.events.length === 0) {
            calendarDiv.innerHTML = '<p>No upcoming events.</p>';
            return;
        }

        calendarDiv.innerHTML = data.events.map(event => `
            <div class="event-item">
                <div class="event-header">
                    <strong>${event.event}</strong>
                    <span class="event-impact ${event.impact}">${event.impact}</span>
                </div>
                <p><strong>Currency:</strong> ${event.currency}</p>
                <p><strong>Time:</strong> ${new Date(event.datetime).toLocaleString()}</p>
                <p><strong>Forecast:</strong> ${event.forecast || 'N/A'} | <strong>Previous:</strong> ${event.previous || 'N/A'}</p>
            </div>
        `).join('');
    } catch (error) {
        calendarDiv.innerHTML = '<p class="error">Failed to load economic calendar</p>';
        console.error('Calendar error:', error);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadTopMovers();
    loadChart();
});
