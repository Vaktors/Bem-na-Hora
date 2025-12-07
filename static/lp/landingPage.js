// landingPage.js — versão corrigida e resistente a erros
(function () {
  // --- Util helpers ---
  const safe = fn => {
    try { return fn(); } catch (err) { console.error(err); return null; }
  };

  // --- Busca (opcional) ---
  safe(() => {
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

    if (btn) btn.addEventListener('click', buscar);
    if (input) {
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') buscar();
      });
    }
  });

  // --- Lógica Unificada de Login/Dropdown (Mais Robusta) ---
  document.addEventListener('click', (e) => {
    const target = e.target;

    // 1. CLIQUE NO BOTÃO DE LOGIN -> Vira Foto
    if (target.classList.contains('btn-login')) {
      e.preventDefault();
      const loginBtn = target;

      // Cria o elemento da foto (Wrapper)
      const profilePic = document.createElement('div');
      profilePic.className = 'profile-pic';

      // --- AQUI ESTAVA A DIFERENÇA ---
      // Agora está igual ao global: tenta a imagem local, se falhar, usa o ícone do CDN.
      profilePic.innerHTML = `
        <img src="img/do-utilizador.png" alt="Perfil" onerror="this.src='https://cdn-icons-png.flaticon.com/512/3135/3135715.png'">
        <div class="dropdown-menu">
          <a href="#" class="dropdown-item">Meu Perfil</a>
          <div class="dropdown-divider"></div>
          <a href="#" class="dropdown-item">Sair</a>
        </div>
      `;
      // -------------------------------

      // Substitui botão pela foto
      loginBtn.parentNode.replaceChild(profilePic, loginBtn);
      return; // Para a execução aqui
    }

    // 2. CLIQUE NA FOTO -> Abre/Fecha Menu
    const profileWrapper = target.closest('.profile-pic');
    if (profileWrapper) {
      // Se clicou na foto (e não no menu dentro dela)
      const menu = profileWrapper.querySelector('.dropdown-menu');
      if (menu) {
        menu.classList.toggle('show');
        e.stopPropagation(); // Impede que o clique feche o menu imediatamente
      }
      return;
    }

    // 3. CLIQUE NO BOTÃO "SAIR" -> Vira Botão Login
    if (target.classList.contains('dropdown-item') && target.textContent.trim() === 'Sair') {
      e.preventDefault();
      // Acha o wrapper da foto para substituir
      const profilePic = target.closest('.profile-pic');
      if (profilePic) {
        const loginBtn = document.createElement('button');
        loginBtn.textContent = 'Login';
        loginBtn.className = 'btn-login';
        profilePic.parentNode.replaceChild(loginBtn, profilePic);
      }
      return;
    }

    // 4. CLIQUE FORA -> Fecha qualquer menu aberto
    document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
      menu.classList.remove('show');
    });
  });

  // Fechar com tecla ESC
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.dropdown-menu.show').forEach(m => m.classList.remove('show'));
    }
  });

  // --- Smooth scroll seguro para âncoras internas ---
  safe(() => {
    document.querySelectorAll('a[href^="#"]').forEach((a) => {
      a.addEventListener('click', (e) => {
        const href = a.getAttribute('href') || '';
        // Ignora href apenas "#" (que é comum em menus / dropdowns)
        if (href === '#') {
          // optional: evitar navegação padrão que pode pular ao topo
          e.preventDefault();
          return;
        }
        // Se href for algo como "#id", só tentar encontrar quando houver mais que 1 caractere
        if (href.length > 1) {
          const el = document.querySelector(href);
          if (el) {
            e.preventDefault();
            el.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        }
      });
    });
  });

})();