(() => {
  const count = document.getElementById('posts-per-day');
  const grid = document.getElementById('posting-times-grid');
  const template = document.getElementById('posting-time-template');
  if (!count || !grid || !template) return;

  function suggestedTime(existing) {
    for (let minute = 0; minute < 1440; minute += 30) {
      if (existing.every(value => {
        if (!/^\d{2}:\d{2}$/.test(value)) return true;
        const used = Number(value.slice(0, 2)) * 60 + Number(value.slice(3));
        const gap = Math.abs(minute - used);
        return Math.min(gap, 1440 - gap) >= 30;
      })) return `${String(Math.floor(minute / 60)).padStart(2, '0')}:${String(minute % 60).padStart(2, '0')}`;
    }
    return '';
  }

  function syncSlots() {
    const target = Number(count.value);
    if (!Number.isInteger(target) || target < 1 || target > 24) return;
    while (grid.children.length > target) grid.lastElementChild.remove();
    while (grid.children.length < target) {
      const index = grid.children.length + 1;
      const existing = [...grid.querySelectorAll('input[type="time"]')].map(input => input.value);
      const slot = template.content.firstElementChild.cloneNode(true);
      const input = slot.querySelector('input');
      input.id = `posting-time-${index}`;
      input.value = suggestedTime(existing);
      slot.querySelector('label').htmlFor = input.id;
      slot.querySelector('label').textContent = `Bài ${index}`;
      slot.querySelector('button').setAttribute('aria-label', `Chọn giờ cho bài ${index}`);
      grid.append(slot);
    }
  }

  count.addEventListener('input', syncSlots);
  grid.addEventListener('click', event => {
    const button = event.target.closest('.posting-time-pick');
    if (!button) return;
    const input = button.parentElement.querySelector('input[type="time"]');
    if (typeof input.showPicker === 'function') input.showPicker();
    else input.focus();
  });
})();
