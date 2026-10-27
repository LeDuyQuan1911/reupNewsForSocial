(() => {
  const page = document.querySelector('.hermes-layout[data-status-url]');
  if (!page) return;
  const byId = id => document.getElementById(id);

  function displayTime(value) {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return new Intl.DateTimeFormat('vi-VN', {
      timeZone: 'Asia/Bangkok', day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit', hour12: false,
    }).format(date);
  }

  function showStatus(status) {
    const active = status.job_state === 'active';
    const paused = status.job_state === 'paused';
    const running = active && status.gateway_running;
    const badge = byId('hermes-state');
    badge.textContent = running ? 'Đang chạy' : paused ? 'Đã tạm dừng' : 'Cần kiểm tra';
    badge.classList.toggle('ready', running);
    byId('hermes-gateway').textContent = status.gateway_running ? 'Đang hoạt động' : 'Không xác nhận được';
    byId('hermes-job').textContent = active ? 'Đang bật' : paused ? 'Tạm dừng' : 'Chưa xác định';
    byId('hermes-run').disabled = !running;
    byId('hermes-pause-form').hidden = !active;
    byId('hermes-resume-form').hidden = !paused;

    const error = byId('hermes-error');
    error.hidden = !status.error;
    error.textContent = status.error ? `${status.error}. Kiểm tra cài đặt Hermes và job của repo.` : '';

    const list = byId('hermes-runs');
    list.replaceChildren();
    for (const run of status.runs || []) {
      const row = document.createElement('li');
      const time = document.createElement('span');
      const result = document.createElement('strong');
      time.textContent = displayTime(run.at);
      result.textContent = run.status === 'completed' ? 'Hoàn tất' : run.status === 'failed' ? 'Lỗi' : run.status;
      row.append(time, result);
      list.append(row);
    }
    list.hidden = !list.children.length;
    byId('hermes-empty').hidden = !!list.children.length;
    if (!list.children.length) byId('hermes-empty').textContent = 'Chưa có lịch sử chạy hoặc Hermes chưa phản hồi.';
  }

  fetch(page.dataset.statusUrl, { cache: 'no-store' })
    .then(response => {
      if (!response.ok) throw new Error('Không tải được trạng thái Hermes');
      return response.json();
    })
    .then(showStatus)
    .catch(() => showStatus({ gateway_running: false, job_state: 'unknown', runs: [], error: 'Không tải được trạng thái Hermes' }));
})();
