// Toggle del teclado e inserción en el input enfocado
document.addEventListener("DOMContentLoaded", () => {
  const kb = document.getElementById('kb');
  const toggleBtn = document.getElementById('toggleKb');
  const fx = document.querySelector('input[name="fx"]');
  const gx = document.querySelector('input[name="gx"]');
  const backspace = document.getElementById('backspace');
  const clearFx = document.getElementById('clearFx');
  const clearGx = document.getElementById('clearGx');

  if (!fx || !gx || !toggleBtn || !kb) return;

  let activeInput = fx;
  [fx, gx].forEach(el => {
    el.addEventListener('focus', () => activeInput = el);
    el.addEventListener('click', () => activeInput = el);
  });

  toggleBtn.addEventListener('click', () => {
    kb.classList.toggle('kb-hidden');
  });

  // Inserción en el input activo
  document.querySelectorAll('#kb [data-ins]').forEach(btn => {
    btn.addEventListener('click', () => {
      if (!activeInput) activeInput = fx;
      const ins = btn.getAttribute('data-ins');
      const start = activeInput.selectionStart ?? activeInput.value.length;
      const end = activeInput.selectionEnd ?? activeInput.value.length;
      const v = activeInput.value;
      activeInput.value = v.slice(0, start) + ins + v.slice(end);
      const newPos = start + ins.length;
      activeInput.focus();
      activeInput.setSelectionRange(newPos, newPos);
    });
  });

  backspace.addEventListener('click', () => {
    if (!activeInput) activeInput = fx;
    const start = activeInput.selectionStart ?? 0;
    const end = activeInput.selectionEnd ?? 0;
    if (start === end && start > 0) {
      const v = activeInput.value;
      activeInput.value = v.slice(0, start - 1) + v.slice(end);
      const newPos = start - 1;
      activeInput.focus();
      activeInput.setSelectionRange(newPos, newPos);
    } else {
      const v = activeInput.value;
      activeInput.value = v.slice(0, start) + v.slice(end);
      const newPos = start;
      activeInput.focus();
      activeInput.setSelectionRange(newPos, newPos);
    }
  });

  clearFx.addEventListener('click', () => { fx.value = ""; fx.focus(); });
  clearGx.addEventListener('click', () => { gx.value = ""; gx.focus(); });
});