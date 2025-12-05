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

  // --- Dropdown do perfil ---
  function initProfileDropdown() {
    const profilePic = document.querySelector('.profile-pic');
    if (profilePic) {
      profilePic.addEventListener('click', (e) => {
        e.stopPropagation();
        const dropdown = profilePic.querySelector('.dropdown-menu');
        if (!dropdown) return;
        dropdown.classList.toggle('show');
      });
    } else {
      console.warn('Elemento .profile-pic não encontrado no DOM.');
    }
  }

  initProfileDropdown();

  // Fechar dropdown ao clicar fora
  document.addEventListener('click', (e) => {
    // se não achou, silently ignore
    const p = document.querySelector('.profile-pic');
    if (!p) return;
    if (!p.contains(e.target)) {
      const dropdown = p.querySelector('.dropdown-menu');
      dropdown?.classList.remove('show');
    }
  });

  // Fechar com ESC
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      const p = document.querySelector('.profile-pic');
      if (!p) return;
      const dropdown = p.querySelector('.dropdown-menu');
      dropdown?.classList.remove('show');
    }
  });

  // Funcionalidade do botão "Sair" usando event delegation
  document.addEventListener('click', (e) => {
    if (e.target.classList.contains('dropdown-item') && e.target.textContent.trim() === 'Sair') {
      e.preventDefault();
      const profilePic = document.querySelector('.profile-pic');
      if (profilePic) {
        const loginBtn = document.createElement('button');
        loginBtn.textContent = 'Login';
        loginBtn.className = 'btn-login';
        profilePic.parentNode.replaceChild(loginBtn, profilePic);
      }
    }
  });

  // Funcionalidade do botão "Login" - regenera o profile pic
  document.addEventListener('click', (e) => {
    if (e.target.classList.contains('btn-login')) {
      e.preventDefault();
      const loginBtn = e.target;
      const profilePic = document.createElement('div');
      profilePic.className = 'profile-pic';
      profilePic.innerHTML = `
        <img src="img/do-utilizador.png" alt="Perfil do Usuário">
        <div class="dropdown-menu">
          <a href="#" class="dropdown-item">Meu Perfil</a>
          <div class="dropdown-divider"></div>
          <a href="#" class="dropdown-item">Sair</a>
        </div>
      `;
      loginBtn.parentNode.replaceChild(profilePic, loginBtn);
      initProfileDropdown(); // Reinitialize the dropdown functionality

      // Attach event listener to the newly created "Sair" link
      const sairLink = profilePic.querySelector('.dropdown-menu .dropdown-item:last-child');
      if (sairLink) {
        sairLink.addEventListener('click', (e) => {
          e.preventDefault();
          const profilePic = document.querySelector('.profile-pic');
          if (profilePic) {
            const loginBtn = document.createElement('button');
            loginBtn.textContent = 'Login';
            loginBtn.className = 'btn-login';
            profilePic.parentNode.replaceChild(loginBtn, profilePic);
          }
        });
      }

      // TODO: Link to login page here - replace with actual login logic
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