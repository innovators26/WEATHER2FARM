/**
 * AI Downscaling Tab
 * Clear presentation of the Block -> Panchayat ML pipeline problem statement and resolution.
 */

export async function render(state) {
  const container = document.getElementById('downscaling-tab');
  const gp_code  = state.panchayat ? state.panchayat.gp_code : '2731002008';
  const gp_name  = state.panchayat ? state.panchayat.gp_name : 'Unknown';
  const blk_name = state.block || 'Unknown';

  // Loading state
  container.innerHTML = `
    <div style="display:flex;align-items:baseline;gap:16px;margin-bottom:24px;">
      <h1 style="font-size:32px;font-weight:700;color:var(--primary);">AI Downscaling</h1>
      <span style="color:var(--text-muted);font-size:16px;">Converting Block-level weather forecasts into Panchayat-level forecasts using local geographic and historical information.</span>
    </div>
    <div style="padding: 40px; text-align: center; color: var(--text-muted);">
      <i class="ph-fill ph-spinner ph-spin" style="font-size: 32px; margin-bottom: 12px;"></i>
      <div>Loading downscaling model context for ${gp_name}...</div>
    </div>
  `;

  let block_rain = '--';
  let block_temp = '--';
  let block_rh = '--';
  let block_wind = '--';
  
  let predicted_residual = '--';
  let final_rain = '--';

  let hasData = false;
  
  try {
    const res = await fetch(`/api/panchayat/${gp_code}/forecast`);
    if (res.ok) {
        const d = await res.json();
        // The /forecast endpoint returns current { rain, temp, humidity, wind } and block_forecast_rain, residual, downscaled_rain
        block_rain = d.block_forecast_rain;
        // In the app architecture, IMD Block temp/humidity is represented by the base 'current' since we don't have block-specific temp in the JSON, but for visualization we'll show what we have.
        block_temp = d.current ? d.current.temp : '--';
        block_rh = d.current ? d.current.humidity : '--';
        block_wind = d.current ? d.current.wind : '--';
        predicted_residual = d.residual;
        final_rain = d.downscaled_rain;
        hasData = true;
    }
  } catch (err) {
    console.error("Failed to load forecast data:", err);
  }

  const sign = (typeof predicted_residual === 'number' && predicted_residual > 0) ? '+' : '';

  container.innerHTML = `
    <div style="display:flex;flex-direction:column;gap:24px;">
      
      <!-- HEADER -->
      <div style="border-bottom:1px solid #DDE6ED; padding-bottom:16px;">
        <h1 style="font-size:32px; font-weight:700; color:#064B70; margin:0;">AI DOWNSCALING</h1>
        <div style="font-size:16px; color:#64748B; margin-top:8px;">
          Converting Block-level weather forecasts into Panchayat-level forecasts using local geographic and historical information.
        </div>
      </div>

      <!-- WHY DOWNSCALING -->
      <div style="background:#F4F7F9; border:1px solid #DDE6ED; padding:20px; border-radius:8px;">
        <h2 style="font-size:14px; font-weight:700; color:#064B70; margin-bottom:8px; text-transform:uppercase;">Why Downscaling?</h2>
        <div style="font-size:14px; color:#17324D; line-height:1.6;">
          IMD provides weather forecasts at Block level, but weather conditions can vary significantly between Panchayats because of differences in elevation, terrain, location and historical rainfall patterns. Weather2Farm uses these Panchayat-level characteristics to estimate a local correction to the IMD Block forecast and produce a more localized Panchayat forecast.
        </div>
      </div>

      <div class="dash-layout">
        
        <!-- LEFT: Pipeline Architecture -->
        <div class="dash-left" style="flex:1;">
          
          <div class="card" style="background:#fff; border:1px solid #DDE6ED; padding:24px; border-radius:8px;">
            <div style="font-size:14px; font-weight:700; color:#064B70; margin-bottom:20px; text-transform:uppercase; border-bottom:1px solid #eee; padding-bottom:10px;">
              Model Architecture
            </div>

            <!-- IMD Block -->
            <div style="background:#F8FAFC; border:1px solid #CBD5E1; padding:16px; border-radius:6px;">
              <div style="font-size:12px; font-weight:700; color:#0B5E8E; margin-bottom:12px; text-transform:uppercase;">IMD Block Forecast</div>
              <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                <div><div style="font-size:11px; color:#64748B;">Location</div><div style="font-size:14px; font-weight:700; color:#17324D;">${blk_name}</div></div>
                <div><div style="font-size:11px; color:#64748B;">Rainfall</div><div style="font-size:14px; font-weight:700; color:#17324D;">${block_rain} mm/day</div></div>
                <div><div style="font-size:11px; color:#64748B;">Temperature</div><div style="font-size:14px; font-weight:700; color:#17324D;">${block_temp} °C</div></div>
                <div><div style="font-size:11px; color:#64748B;">Relative Humidity</div><div style="font-size:14px; font-weight:700; color:#17324D;">${block_rh} %</div></div>
                <div><div style="font-size:11px; color:#64748B;">Wind Speed</div><div style="font-size:14px; font-weight:700; color:#17324D;">${block_wind} km/h</div></div>
              </div>
            </div>

            <div style="text-align:center; padding:8px 0; color:#94A3B8;"><i class="ph-bold ph-arrow-down" style="font-size:20px;"></i></div>

            <!-- Panchayat Features -->
            <div style="background:#F8FAFC; border:1px solid #CBD5E1; padding:16px; border-radius:6px;">
              <div style="font-size:12px; font-weight:700; color:#0B5E8E; margin-bottom:12px; text-transform:uppercase;">Panchayat-level Features</div>
              <div style="display:grid; grid-template-columns: repeat(2, 1fr); gap:6px; font-size:13px; color:#17324D;">
                <div>• Block Forecast Rainfall</div>
                <div>• Latitude</div>
                <div>• Longitude</div>
                <div>• Elevation</div>
                <div>• Slope</div>
                <div>• Station Distance</div>
                <div>• Historical Mean Rainfall</div>
                <div>• Monsoon Indicator</div>
              </div>
            </div>

            <div style="text-align:center; padding:8px 0; color:#94A3B8;"><i class="ph-bold ph-arrow-down" style="font-size:20px;"></i></div>

            <!-- Residual XGBoost -->
            <div style="background:#F8FAFC; border:1px solid #CBD5E1; padding:16px; border-radius:6px;">
              <div style="font-size:12px; font-weight:700; color:#E59A17; margin-bottom:12px; text-transform:uppercase;">Residual XGBoost Model</div>
              <div style="font-size:13px; color:#17324D; line-height:1.5;">
                The model learns the local rainfall correction by learning the difference between observed Panchayat rainfall and the corresponding IMD Block forecast.
              </div>
              <div style="margin-top:12px; background:#fff; padding:10px; border:1px dashed #CBD5E1; text-align:center; font-family:monospace; font-size:13px; font-weight:700; color:#064B70;">
                Residual = Observed Panchayat Rainfall − IMD Block Forecast
              </div>
              <div style="margin-top:8px; background:#fff; padding:10px; border:1px dashed #CBD5E1; text-align:center; font-family:monospace; font-size:13px; font-weight:700; color:#4F8F3A;">
                Panchayat Forecast = IMD Block Forecast + Predicted Residual
              </div>
            </div>
            
            <div style="text-align:center; padding:8px 0; color:#94A3B8;"><i class="ph-bold ph-arrow-down" style="font-size:20px;"></i></div>
            
            <!-- Output -->
            <div style="background:#F8FAFC; border:1px solid #CBD5E1; padding:16px; border-radius:6px;">
              <div style="font-size:12px; font-weight:700; color:#D64545; margin-bottom:8px; text-transform:uppercase;">AI Predicted Local Correction</div>
              <div style="font-size:24px; font-weight:700; color:#D64545;">${sign}${predicted_residual} mm</div>
              <div style="font-size:12px; color:#64748B; margin-top:4px;">The predicted residual represents the local correction estimated for this Panchayat.</div>
            </div>

          </div>
          
          <div class="card" style="background:#fff; border:1px solid #DDE6ED; padding:24px; border-radius:8px;">
            <div style="font-size:14px; font-weight:700; color:#064B70; margin-bottom:12px; text-transform:uppercase; border-bottom:1px solid #eee; padding-bottom:10px;">
              Model Details
            </div>
            <div style="font-size:13px; color:#17324D; line-height:1.6;">
              <div style="margin-bottom:8px;"><strong>Model:</strong> XGBoost Residual</div>
              <div style="margin-bottom:8px;"><strong>Learning target:</strong> Observed Panchayat Rainfall − IMD Block Forecast</div>
              <div style="margin-bottom:8px;"><strong>Input features:</strong> Panchayat-level geographic, terrain, historical and forecast variables.</div>
              <div><strong>Output:</strong> Predicted local rainfall correction.</div>
            </div>
          </div>
          
        </div>

        <!-- RIGHT: Interactive Panel & Final Result -->
        <div class="dash-right" style="flex:0 0 40%; display:flex; flex-direction:column; gap:24px;">
          
          <div class="card" style="background:#fff; border:1px solid #DDE6ED; padding:24px; border-radius:8px; height:auto;">
            <div style="font-size:14px; font-weight:700; color:#064B70; margin-bottom:20px; text-transform:uppercase; border-bottom:1px solid #eee; padding-bottom:10px;">
              Run Prediction
            </div>
            <button id="runAiBtn" class="btn-primary" style="width:100%; justify-content:center; padding:12px; font-size:15px; margin-bottom:20px;">
              <i class="ph-fill ph-play"></i> Run Prediction
            </button>

            <div id="aiStatusList" style="display:none; font-size:13px; color:#17324D; display:flex; flex-direction:column; gap:12px;">
              <div id="step1" style="display:flex; align-items:center; gap:8px; opacity:0.4;"><i class="ph-bold ph-check-circle step-icon"></i> 1. Reading Block Forecast</div>
              <div id="step2" style="display:flex; align-items:center; gap:8px; opacity:0.4;"><i class="ph-bold ph-check-circle step-icon"></i> 2. Loading Panchayat Features</div>
              <div id="step3" style="display:flex; align-items:center; gap:8px; opacity:0.4;"><i class="ph-bold ph-check-circle step-icon"></i> 3. Running Residual XGBoost Model</div>
              <div id="step4" style="display:flex; align-items:center; gap:8px; opacity:0.4;"><i class="ph-bold ph-check-circle step-icon"></i> 4. Calculating Local Correction</div>
              <div id="step5" style="display:flex; align-items:center; gap:8px; opacity:0.4;"><i class="ph-bold ph-check-circle step-icon"></i> 5. Generating Panchayat Forecast</div>
            </div>
          </div>

          <div class="card" id="aiResultCard" style="background:#fff; border:1px solid #DDE6ED; padding:24px; border-radius:8px; height:auto; opacity:${hasData?1:0.3};">
            <div style="font-size:14px; font-weight:700; color:#064B70; margin-bottom:20px; text-transform:uppercase; border-bottom:1px solid #eee; padding-bottom:10px;">
              Final Result
            </div>

            <div style="text-align:center;">
              <div style="font-size:11px; color:#64748B; font-weight:700; text-transform:uppercase;">IMD Block Forecast</div>
              <div style="font-size:24px; font-weight:700; color:#17324D;">${block_rain} mm</div>
              
              <div style="font-size:24px; color:#94A3B8; margin:8px 0;">+</div>
              
              <div style="font-size:11px; color:#64748B; font-weight:700; text-transform:uppercase;">AI Local Correction</div>
              <div style="font-size:24px; font-weight:700; color:#D64545;">${sign}${predicted_residual} mm</div>
              
              <div style="font-size:24px; color:#94A3B8; margin:8px 0;">=</div>
              
              <div style="font-size:11px; color:#4F8F3A; font-weight:700; text-transform:uppercase;">Panchayat-level Forecast</div>
              <div style="font-size:32px; font-weight:700; color:#4F8F3A;">${final_rain} mm</div>
              
              <div style="font-size:13px; font-weight:700; color:#17324D; margin-top:12px; background:#F5FFF5; border:1px solid #CDE2F0; padding:8px; border-radius:4px;">
                Panchayat: ${gp_name}
              </div>
            </div>
          </div>
          
          <div class="card" style="background:#FDFDFD; border:1px solid #DDE6ED; padding:20px; border-radius:8px;">
            <div style="font-size:13px; font-weight:700; color:#E59A17; margin-bottom:8px; text-transform:uppercase;">Why is the forecast different?</div>
            <div style="font-size:13px; color:#17324D; line-height:1.5;">
              The Panchayat forecast is adjusted using local geographic and historical characteristics captured by the residual XGBoost model.
              <ul style="padding-left:20px; margin-top:8px; margin-bottom:0;">
                <li>Elevation</li>
                <li>Slope</li>
                <li>Historical rainfall</li>
                <li>Panchayat location</li>
                <li>Distance from observation station</li>
                <li>Monsoon condition</li>
              </ul>
            </div>
          </div>

        </div>
      </div>
    </div>
  `;

  const btn = document.getElementById('runAiBtn');
  btn.addEventListener('click', async () => {
    btn.disabled = true;
    btn.innerHTML = '<i class="ph ph-spinner ph-spin"></i> Running...';
    
    document.getElementById('aiStatusList').style.display = 'flex';
    for(let i=1; i<=5; i++) {
        const step = document.getElementById('step' + i);
        step.style.opacity = '0.4';
        step.querySelector('i').style.color = 'inherit';
    }

    async function tick(id, ms) {
        await sleep(ms);
        const step = document.getElementById(id);
        step.style.opacity = '1';
        step.querySelector('i').style.color = '#4F8F3A';
    }

    await tick('step1', 400);
    await tick('step2', 400);
    await tick('step3', 600);
    
    // During this, actually trigger the API if we want to emulate real time execution completely
    try {
      const res = await fetch('/api/downscale/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ gp_code, block_name: blk_name, district: state.district || 'Pune' })
      });
      const d = await res.json();
      
      await tick('step4', 300);
      await tick('step5', 300);

      // Update DOM
      document.getElementById('aiResultCard').style.opacity = '1';
      document.getElementById('aiResultCard').innerHTML = `
            <div style="font-size:14px; font-weight:700; color:#064B70; margin-bottom:20px; text-transform:uppercase; border-bottom:1px solid #eee; padding-bottom:10px;">
              Final Result
            </div>
            <div style="text-align:center;">
              <div style="font-size:11px; color:#64748B; font-weight:700; text-transform:uppercase;">IMD Block Forecast</div>
              <div style="font-size:24px; font-weight:700; color:#17324D;">${d.block_forecast} mm</div>
              <div style="font-size:24px; color:#94A3B8; margin:8px 0;">+</div>
              <div style="font-size:11px; color:#64748B; font-weight:700; text-transform:uppercase;">AI Local Correction</div>
              <div style="font-size:24px; font-weight:700; color:#D64545;">${(d.predicted_residual > 0 ? '+' : '')}${d.predicted_residual} mm</div>
              <div style="font-size:24px; color:#94A3B8; margin:8px 0;">=</div>
              <div style="font-size:11px; color:#4F8F3A; font-weight:700; text-transform:uppercase;">Panchayat-level Forecast</div>
              <div style="font-size:32px; font-weight:700; color:#4F8F3A;">${d.panchayat_forecast} mm</div>
              <div style="font-size:13px; font-weight:700; color:#17324D; margin-top:12px; background:#F5FFF5; border:1px solid #CDE2F0; padding:8px; border-radius:4px;">
                Panchayat: ${gp_name}
              </div>
            </div>`;
    } catch (e) {
      console.error(e);
    }

    btn.disabled = false;
    btn.innerHTML = '<i class="ph-fill ph-check"></i> Run Again';
  });
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
