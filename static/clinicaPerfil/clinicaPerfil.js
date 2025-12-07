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