/**
 * Feedback Tab
 * Actual persistence via POST /api/feedback.
 * Shows success only after confirmed server save.
 */

export async function render(state) {
  const container = document.getElementById('feedback-tab');
  const gp_code  = state.panchayat ? state.panchayat.gp_code : '2731002008';
  const gp_name  = state.panchayat ? state.panchayat.gp_name : 'Tamhini';

  container.innerHTML = `
    <div style="display:flex;align-items:baseline;gap:16px;margin-bottom:24px;">
      <h1 style="font-size:32px;font-weight:700;color:var(--primary);">Feedback</h1>
      <span style="color:var(--text-muted);font-size:16px;">Report actual weather conditions for ${gp_name}</span>
    </div>

    <div class="dash-layout">
      <!-- LEFT: Form -->
      <div class="dash-left" style="flex:0 0 52%;">
        <div class="card">
          <div class="card-title" style="margin-bottom:22px;">
            <i class="ph-fill ph-clipboard-text"></i> What actually happened?
          </div>

          <div style="display:flex;flex-direction:column;gap:22px;">

            <!-- Q1 -->
            <div>
              <div style="font-size:14px;font-weight:700;margin-bottom:10px;">1. Did it rain today?</div>
              <div style="display:flex;gap:12px;">
                <button id="fbYes" class="btn-yes" style="flex:1;height:48px;font-size:15px;background:#fff;color:var(--success);border:2px solid var(--success);">
                  <i class="ph-bold ph-check"></i> Yes
                </button>
                <button id="fbNo" class="btn-no" style="flex:1;height:48px;font-size:15px;background:#fff;color:var(--danger);border:2px solid var(--danger);">
                  <i class="ph-bold ph-x"></i> No
                </button>
              </div>
            </div>

            <!-- Rain intensity (hidden until Yes) -->
            <div id="fbIntSection" style="display:none;opacity:0;transition:opacity 0.3s;">
              <div style="font-size:14px;font-weight:700;margin-bottom:10px;">Rain Intensity</div>
              <div style="display:flex;gap:8px;" id="fbIntBtns">
                <button class="btn-intensity fbInt" data-val="Light" style="flex:1;height:40px;">
                  <i class="ph-fill ph-cloud-rain"></i> Light
                </button>
                <button class="btn-intensity fbInt" data-val="Moderate" style="flex:1;height:40px;">
                  <i class="ph-fill ph-cloud-rain"></i> Moderate
                </button>
                <button class="btn-intensity fbInt" data-val="Heavy" style="flex:1;height:40px;">
                  <i class="ph-fill ph-cloud-lightning"></i> Heavy
                </button>
              </div>

              <div style="margin-top:14px;">
                <div style="font-size:14px;font-weight:700;margin-bottom:8px;">Actual Rainfall (mm, optional)</div>
                <input id="fbActRain" type="number" min="0" max="500" placeholder="e.g. 45"
                  style="width:100%;height:40px;border-radius:8px;border:1px solid var(--border);padding:0 12px;font-size:14px;">
              </div>
            </div>

            <hr style="border:none;border-top:1px solid var(--border);">

            <!-- Q2 -->
            <div>
              <div style="font-size:14px;font-weight:700;margin-bottom:10px;">2. Was the forecast useful?</div>
              <div style="display:flex;gap:12px;">
                <button class="btn-intensity fbUseful" data-val="true" style="flex:1;height:40px;">Yes</button>
                <button class="btn-intensity fbUseful" data-val="false" style="flex:1;height:40px;">No</button>
              </div>
            </div>

            <!-- Q3 -->
            <div>
              <div style="font-size:14px;font-weight:700;margin-bottom:8px;">3. Comments (optional)</div>
              <textarea id="fbComments" rows="3"
                style="width:100%;border-radius:8px;border:1px solid var(--border);padding:12px;font-family:inherit;font-size:13px;resize:vertical;">
              </textarea>
            </div>

            <button id="fbSubmit" class="btn-primary" style="width:100%;justify-content:center;height:48px;font-size:15px;">
              <i class="ph-fill ph-paper-plane-tilt"></i> Submit Feedback
            </button>

            <div id="fbSuccess" style="display:none;background:var(--secondary-bg);border:1px solid #D3EBCD;border-radius:8px;padding:16px;text-align:center;font-weight:700;color:var(--success);">
              <i class="ph-fill ph-check-circle" style="font-size:22px;"></i><br>
              Feedback submitted successfully. Thank you!
            </div>
            <div id="fbError" style="display:none;background:#FEE;border:1px solid var(--danger);border-radius:8px;padding:16px;color:var(--danger);font-size:13px;"></div>
          </div>
        </div>
      </div>

      <!-- RIGHT: Pipeline Info -->
      <div class="dash-right" style="flex:0 0 48%;">
        <div class="card" style="background:var(--primary);color:#fff;height:100%;">
          <div style="font-size:16px;font-weight:700;margin-bottom:16px;display:flex;align-items:center;gap:8px;">
            <i class="ph-fill ph-arrows-clockwise" style="color:var(--secondary);"></i>
            Feedback → Validation Loop
          </div>
          <div style="font-size:13px;color:rgba(255,255,255,0.85);margin-bottom:24px;line-height:1.6;">
            Your ground-truth reports are stored and used to evaluate forecast accuracy over time.
          </div>

          <div style="display:flex;flex-direction:column;gap:14px;">
            ${[
              ['ph-cloud-rain', '1. Forecast Generated', 'XGBoost Residual model outputs Panchayat-level rain prediction'],
              ['ph-user', '2. Farmer Receives Forecast', 'Via this dashboard or future mobile app'],
              ['ph-clipboard-text', '3. Ground Truth Feedback', 'You submit what actually happened'],
              ['ph-database', '4. Stored Persistently', 'Saved to data/feedback.json for analysis'],
              ['ph-chart-line-up', '5. Predicted vs Actual', 'Enables accuracy tracking per Panchayat'],
              ['ph-gear', '6. Future Recalibration', 'Feedback available for future model retraining (not automatic yet)']
            ].map(([icon, title, desc]) => `
              <div style="display:flex;align-items:flex-start;gap:12px;">
                <div style="width:36px;height:36px;border-radius:50%;background:rgba(255,255,255,0.1);display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                  <i class="ph-fill ${icon}" style="font-size:16px;color:var(--secondary);"></i>
                </div>
                <div>
                  <div style="font-weight:700;font-size:13px;">${title}</div>
                  <div style="font-size:12px;color:rgba(255,255,255,0.65);margin-top:2px;">${desc}</div>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    </div>
  `;

  // State
  let didRain = null;
  let intensity = null;
  let useful = null;

  // Rain Yes/No
  document.getElementById('fbYes').addEventListener('click', () => {
    didRain = true;
    document.getElementById('fbYes').style.background = 'var(--success)';
    document.getElementById('fbYes').style.color = '#fff';
    document.getElementById('fbNo').style.background = '#fff';
    document.getElementById('fbNo').style.color = 'var(--danger)';
    const intSec = document.getElementById('fbIntSection');
    intSec.style.display = 'block';
    setTimeout(() => { intSec.style.opacity = '1'; }, 10);
  });
  document.getElementById('fbNo').addEventListener('click', () => {
    didRain = false;
    document.getElementById('fbNo').style.background = 'var(--danger)';
    document.getElementById('fbNo').style.color = '#fff';
    document.getElementById('fbYes').style.background = '#fff';
    document.getElementById('fbYes').style.color = 'var(--success)';
    document.getElementById('fbIntSection').style.opacity = '0';
    setTimeout(() => { document.getElementById('fbIntSection').style.display = 'none'; }, 300);
  });

  // Intensity
  document.querySelectorAll('.fbInt').forEach(btn => {
    btn.addEventListener('click', () => {
      intensity = btn.dataset.val;
      document.querySelectorAll('.fbInt').forEach(b => {
        b.style.background = '#fff';
        b.style.color = 'var(--text-muted)';
        b.style.borderColor = 'var(--border)';
      });
      btn.style.background = 'var(--primary-bg)';
      btn.style.color = 'var(--primary)';
      btn.style.borderColor = 'var(--primary)';
    });
  });

  // Useful
  document.querySelectorAll('.fbUseful').forEach(btn => {
    btn.addEventListener('click', () => {
      useful = btn.dataset.val === 'true';
      document.querySelectorAll('.fbUseful').forEach(b => {
        b.style.background = '#fff';
        b.style.color = 'var(--text-muted)';
        b.style.borderColor = 'var(--border)';
      });
      btn.style.background = 'var(--primary-bg)';
      btn.style.color = 'var(--primary)';
      btn.style.borderColor = 'var(--primary)';
    });
  });

  // Submit
  document.getElementById('fbSubmit').addEventListener('click', async () => {
    if (didRain === null) {
      alert('Please indicate if it rained today.');
      return;
    }

    const btn = document.getElementById('fbSubmit');
    btn.disabled = true;
    btn.innerHTML = '<i class="ph ph-spinner"></i> Submitting...';

    const payload = {
      gp_code,
      gp_name,
      did_rain: didRain,
      intensity: didRain ? intensity : null,
      actual_rainfall_mm: didRain ? parseFloat(document.getElementById('fbActRain').value) || null : null,
      forecast_useful: useful,
      comments: document.getElementById('fbComments').value.trim(),
      timestamp: new Date().toISOString()
    };

    try {
      const res = await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const d = await res.json();

      if (res.ok && d.success) {
        document.getElementById('fbSubmit').style.display = 'none';
        document.getElementById('fbSuccess').style.display = 'block';
      } else {
        throw new Error(d.detail || 'Server error');
      }
    } catch (e) {
      const errEl = document.getElementById('fbError');
      errEl.style.display = 'block';
      errEl.innerText = 'Submission failed: ' + e.message + '. Please try again.';
      btn.disabled = false;
      btn.innerHTML = '<i class="ph-fill ph-paper-plane-tilt"></i> Submit Feedback';
    }
  });
}
