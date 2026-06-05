export function renderCountdownHTML() {
  return `
    <div class="countdown-timer" data-state="running">
      <div class="countdown-header">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <polyline points="12 6 12 12 16 14"/>
        </svg>
        <span>Oferta expira em</span>
      </div>
      <div class="countdown-boxes">
        <div class="countdown-box">
          <span class="countdown-value" data-unit="hours">00</span>
          <span class="countdown-label">h</span>
        </div>
        <span class="countdown-sep">:</span>
        <div class="countdown-box">
          <span class="countdown-value" data-unit="minutes">00</span>
          <span class="countdown-label">m</span>
        </div>
        <span class="countdown-sep">:</span>
        <div class="countdown-box">
          <span class="countdown-value" data-unit="seconds">00</span>
          <span class="countdown-label">s</span>
        </div>
      </div>
    </div>
  `;
}

function pad(n) {
  return n.toString().padStart(2, '0');
}

export function initCountdownTimer(container, slug) {
  if (!container) return;
  const key = `countdown-${slug}`;
  let endTime = parseInt(localStorage.getItem(key));

  if (!endTime || isNaN(endTime)) {
    const hours = Math.floor(Math.random() * 11) + 1;
    const minutes = Math.floor(Math.random() * 60);
    const seconds = Math.floor(Math.random() * 60);
    endTime = Date.now() + ((hours * 3600) + (minutes * 60) + seconds) * 1000;
    localStorage.setItem(key, endTime.toString());
  }

  container.innerHTML = renderCountdownHTML();
  const root = container.querySelector('.countdown-timer');
  const hoursEl = root.querySelector('[data-unit="hours"]');
  const minutesEl = root.querySelector('[data-unit="minutes"]');
  const secondsEl = root.querySelector('[data-unit="seconds"]');

  function tick() {
    const remaining = endTime - Date.now();
    if (remaining <= 0) {
      root.dataset.state = 'ended';
      root.innerHTML = `
        <div class="countdown-ended">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <span>Oferta encerrada</span>
        </div>
      `;
      clearInterval(intervalId);
      return;
    }

    const totalSeconds = Math.floor(remaining / 1000);
    const h = Math.floor(totalSeconds / 3600);
    const m = Math.floor((totalSeconds % 3600) / 60);
    const s = totalSeconds % 60;
    hoursEl.textContent = pad(h);
    minutesEl.textContent = pad(m);
    secondsEl.textContent = pad(s);
  }

  tick();
  const intervalId = setInterval(tick, 1000);
  return {
    reset(newHours) {
      const h = newHours || (Math.floor(Math.random() * 11) + 1);
      const m = Math.floor(Math.random() * 60);
      const s = Math.floor(Math.random() * 60);
      endTime = Date.now() + ((h * 3600) + (m * 60) + s) * 1000;
      localStorage.setItem(key, endTime.toString());
      tick();
    }
  };
}
