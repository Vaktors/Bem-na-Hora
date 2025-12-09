function switchTab(tabId) {
    // 1. Remove a classe 'active' de todas as abas
    const navItems = document.querySelectorAll('.profile-tabs li');
    navItems.forEach(item => {
        item.classList.remove('active');
    });

    // 2. Esconde todo o conteúdo
    const panes = document.querySelectorAll('.tab-pane');
    panes.forEach(pane => {
        pane.classList.remove('active-pane');
    });

    // 3. Adiciona 'active' na aba clicada
    event.currentTarget.classList.add('active');

    // 4. Mostra o conteúdo correspondente
    const activePane = document.getElementById(tabId);
    if (activePane) {
        activePane.classList.add('active-pane');
    }
}

// --- LÓGICA DE DROPDOWN (se já existir foto de perfil) ---
document.addEventListener('DOMContentLoaded', () => {
    document.addEventListener('click', (e) => {
        const target = e.target;

        // 1. CLIQUE NA FOTO -> Abre/Fecha Menu
        const profileWrapper = target.closest('.profile-pic');
        if (profileWrapper) {
            const menu = profileWrapper.querySelector('.dropdown-menu');
            if (menu) {
                menu.classList.toggle('show');
                e.stopPropagation();
            }
            return;
        }

        // 2. CLIQUE FORA -> Fecha qualquer menu aberto
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
});