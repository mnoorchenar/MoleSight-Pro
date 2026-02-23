/**
 * MoleSight AI — Drug Discovery Dashboard
 * Main client-side JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {

  // ── Pill → SMILES input fill ─────────────────────────────────────────
  const smilesInput = document.getElementById('smiles-input');
  document.querySelectorAll('.pill[data-smiles]').forEach(pill => {
    pill.addEventListener('click', () => {
      if (smilesInput) {
        smilesInput.value = pill.dataset.smiles;
        smilesInput.focus();
      }
    });
  });

  // ── Responsive Plotly resize ─────────────────────────────────────────
  window.addEventListener('resize', () => {
    document.querySelectorAll('.js-plotly-plot').forEach(el => {
      Plotly.Plots.resize(el);
    });
  });

  // ── Animate KPI values on page load ──────────────────────────────────
  document.querySelectorAll('.kpi-value').forEach(el => {
    const target = parseFloat(el.textContent);
    if (isNaN(target)) return;
    const isDecimal = el.textContent.includes('.');
    const decimals  = isDecimal ? (el.textContent.split('.')[1]?.length || 2) : 0;
    let start = 0;
    const duration = 900;
    const step = target / (duration / 16);
    const timer = setInterval(() => {
      start += step;
      if (start >= target) {
        el.textContent = isDecimal ? target.toFixed(decimals) : target;
        clearInterval(timer);
      } else {
        el.textContent = isDecimal ? start.toFixed(decimals) : Math.floor(start);
      }
    }, 16);
  });

  // ── SMILES validation feedback ────────────────────────────────────────
  if (smilesInput) {
    smilesInput.addEventListener('input', () => {
      const val = smilesInput.value.trim();
      smilesInput.style.borderColor = val.length > 5 ? 'var(--g1)' : 'var(--border)';
    });
  }

});
