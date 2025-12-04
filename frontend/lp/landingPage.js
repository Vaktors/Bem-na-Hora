(function () {
  const input = document.getElementById('location');
  const btn = document.getElementById('btnBuscar');

  function buscar() {
    const value = (input?.value || '').trim();
    if (!value) {
      alert('Digite sua cidade ou CEP para buscar clínicas.');
      input?.focus();
      return;
    }
    alert(`Buscando clínicas próximas a: ${value}`);
  }

  btn?.addEventListener('click', buscar);
  input?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') buscar();
  });

  // Suaviza âncoras internas
  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener('click', (e) => {
      const id = a.getAttribute('href') || '';
      const el = document.querySelector(id);
      if (el) {
        e.preventDefault();
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
})();