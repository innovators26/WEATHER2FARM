export const state = {
  district: "Pune",
  block: null,
  panchayat: null, // { gp_code, gp_name }
  crop: "Wheat",
  sowingDate: null,
  forecastDay: 1,
  mapVariable: "downscaled_rain"
};

const listeners = [];

export function subscribe(listener) {
  listeners.push(listener);
}

function notify() {
  listeners.forEach(listener => listener(state));
}

export function loadState() {
  try {
    const saved = localStorage.getItem("agroscale_state");
    if (saved) {
      const parsed = JSON.parse(saved);
      Object.assign(state, parsed);
    }
  } catch (err) {
    console.error("Failed to load state from localStorage", err);
  }
}

function saveState() {
  try {
    localStorage.setItem("agroscale_state", JSON.stringify(state));
  } catch (err) {
    console.error("Failed to save state", err);
  }
}

export function updateState(updates) {
  Object.assign(state, updates);
  saveState();
  notify();
}

