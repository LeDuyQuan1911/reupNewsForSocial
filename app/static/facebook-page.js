(() => {
  const card = document.querySelector('.facebook-connected[data-identity-url]');
  if (!card) return;
  const name = document.getElementById('facebook-connected-name');
  const pageId = document.getElementById('facebook-connected-id');
  const status = document.getElementById('facebook-connected-status');
  const badge = document.getElementById('facebook-page-badge');
  const savedName = card.dataset.savedName;

  fetch(card.dataset.identityUrl, { cache: 'no-store' })
    .then(response => {
      if (!response.ok) throw new Error('Không tải được thông tin Page.');
      return response.json();
    })
    .then(identity => {
      pageId.textContent = identity.page_id ? `Page ID: ${identity.page_id}` : 'Chưa có Page ID';
      if (identity.verified) {
        name.textContent = identity.name;
        status.textContent = 'Đã xác minh tên và ID Page qua Meta Graph API.';
        badge.textContent = 'Đã xác minh Page';
        badge.classList.add('ready');
      } else {
        name.textContent = savedName || (identity.page_id ? 'Chưa xác minh được tên Page' : 'Chưa có Facebook Page');
        status.textContent = `${savedName ? 'Tên Page đã lưu trước đây; chưa xác minh lại. ' : ''}${identity.error || 'Không xác minh được Page.'}`;
        badge.textContent = identity.page_id ? 'Cần kiểm tra' : 'Chưa kết nối';
      }
    })
    .catch(() => {
      name.textContent = savedName || 'Chưa xác minh được tên Page';
      status.textContent = `${savedName ? 'Tên Page đã lưu trước đây; chưa xác minh lại. ' : ''}Không tải được thông tin Page. Hãy thử tải lại trang.`;
      badge.textContent = 'Cần kiểm tra';
    });
})();
