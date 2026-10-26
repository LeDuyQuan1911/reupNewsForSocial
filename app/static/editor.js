const bodyField = document.querySelector('#post-body');

if (bodyField) {
  const saveForm = bodyField.closest('form');
  const generateForm = document.querySelector('#generate-form');
  const originalBody = bodyField.value;
  let leavingBySubmit = false;

  saveForm.addEventListener('submit', () => {
    leavingBySubmit = true;
  });

  generateForm?.addEventListener('submit', (event) => {
    const changed = bodyField.value !== originalBody;
    const message = changed
      ? 'Bạn có thay đổi chưa lưu. Viết lại bằng AI sẽ thay thế bản nháp đã lưu. Tiếp tục?'
      : 'Viết lại bằng AI sẽ thay thế nội dung bản nháp hiện tại. Tiếp tục?';
    if (bodyField.value.trim() && !window.confirm(message)) {
      event.preventDefault();
      return;
    }
    leavingBySubmit = true;
  });

  window.addEventListener('beforeunload', (event) => {
    if (!leavingBySubmit && bodyField.value !== originalBody) {
      event.preventDefault();
      event.returnValue = '';
    }
  });
}
