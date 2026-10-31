const apiBase = 'http://127.0.0.1:8000';

const questionInput = document.getElementById('questionInput');
const askButton = document.getElementById('askButton');
const loading = document.getElementById('loading');
const answerText = document.getElementById('answerText');
const methodology = document.getElementById('methodology');
const supportingFigures = document.getElementById('supportingFigures');
const errorPanel = document.getElementById('errorPanel');
const errorMessage = document.getElementById('errorMessage');
const canvas = document.getElementById('revenueChart');
const context = canvas.getContext('2d');

function showError(message) {
  errorMessage.textContent = message;
  errorPanel.classList.remove('hidden');
}

function hideError() {
  errorPanel.classList.add('hidden');
}

function renderSupportCards(items) {
  if (!items || items.length === 0) {
    supportingFigures.innerHTML = '<div class="metric-card"><div class="metric-label">No supporting figures</div><div class="metric-value">-</div></div>';
    return;
  }

  supportingFigures.innerHTML = items.map((item) => {
    const entries = Object.entries(item)
      .filter(([key]) => key !== 'month' && key !== 'month_key')
      .map(([key, value]) => {
        const label = key.replace(/_/g, ' ');
        return `<div class="metric-card"><div class="metric-label">${label}</div><div class="metric-value">${formatValue(value)}</div></div>`;
      })
      .join('');

    return entries;
  }).join('');
}

function formatValue(value) {
  if (typeof value === 'number') {
    if (Number.isInteger(value)) {
      return value.toLocaleString();
    }
    return value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  return value ?? '-';
}

function renderChart(rows) {
  if (!rows || rows.length === 0) {
    return;
  }

  const maxValue = Math.max(...rows.map((row) => Number(row.revenue || 0))) || 1;
  const width = canvas.width;
  const height = canvas.height;
  const padding = 40;
  const chartWidth = width - padding * 2;
  const chartHeight = height - padding * 2;

  context.clearRect(0, 0, width, height);
  context.strokeStyle = '#cbd5e1';
  context.lineWidth = 1;
  context.beginPath();
  context.moveTo(padding, padding);
  context.lineTo(padding, height - padding);
  context.lineTo(width - padding, height - padding);
  context.stroke();

  const barWidth = chartWidth / rows.length * 0.6;
  rows.forEach((row, index) => {
    const value = Number(row.revenue || 0);
    const x = padding + index * (chartWidth / rows.length) + 20;
    const barHeight = (value / maxValue) * chartHeight;
    const y = height - padding - barHeight;

    context.fillStyle = '#3b82f6';
    context.fillRect(x, y, barWidth, barHeight);

    context.fillStyle = '#334155';
    context.font = '12px Arial';
    context.fillText(row.month.slice(0, 3), x, height - 15);
  });
}

async function askQuestion() {
  const question = questionInput.value.trim();
  if (!question) {
    showError('Please enter a question.');
    return;
  }

  hideError();
  loading.classList.remove('hidden');
  askButton.disabled = true;

  try {
    const response = await fetch(`${apiBase}/api/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });

    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.detail || 'The server could not process the question.');
    }

    answerText.textContent = result.answer;
    methodology.textContent = result.methodology || 'Net revenue = (Quantity × Unit_price) − Discount_amount';

    let support = result.supporting_figures || [];
    if (result.intent === 'monthly_trend' && result.data && result.data.rows) {
      support = result.data.rows;
      renderChart(result.data.rows);
    } else if (result.intent === 'total_revenue' && result.data) {
      support = [{
        total_revenue: result.data.total_revenue,
        eligible_transactions: result.data.eligible_transactions,
      }];
    } else if (result.intent === 'product_revenue' && result.data && result.data.breakdown) {
      support = result.data.breakdown;
    } else if (result.intent === 'region_revenue' && result.data && result.data.rows) {
      support = result.data.rows;
    } else if (result.intent === 'monthly_comparison' && result.data) {
      support = [{
        month1: result.data.month1,
        month2: result.data.month2,
        month1_revenue: result.data.month1_revenue,
        month2_revenue: result.data.month2_revenue,
        absolute_difference: result.data.absolute_difference,
        percentage_change: result.data.percentage_change,
      }];
    }

    renderSupportCards(support);
    if (result.intent !== 'monthly_trend') {
      context.clearRect(0, 0, canvas.width, canvas.height);
    }
  } catch (error) {
    showError(error.message || 'Something went wrong.');
  } finally {
    loading.classList.add('hidden');
    askButton.disabled = false;
  }
}

askButton.addEventListener('click', askQuestion);
questionInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
    askQuestion();
  }
});

document.querySelectorAll('.suggestion').forEach((button) => {
  button.addEventListener('click', () => {
    questionInput.value = button.textContent.trim();
    askQuestion();
  });
});
