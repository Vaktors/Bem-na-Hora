function switchTab(tabId) {
    // 1. Remove a classe 'active' de todas as abas (li)
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
    // (Como a função é chamada no onclick, precisamos identificar qual elemento chamou)
    // Uma forma segura é buscar pelo texto ou passar 'event'
    // Aqui vamos iterar para achar qual tem o onclick correspondente ou usar o event.target se passado
    
    // Simplificação: vamos usar o event.currentTarget
    event.currentTarget.classList.add('active');

    // 4. Mostra o conteúdo correspondente ao ID
    const activePane = document.getElementById(tabId);
    if (activePane) {
        activePane.classList.add('active-pane');
    }
}

// Dropdown logic is handled globally by header.js

// Variável para armazenar o mapa
let map = null;

// Função para inicializar o mapa
function initMap() {
    const mapElement = document.getElementById('map');
    if (!mapElement || map) return; // Já inicializado

    // Obtém os dados do endereço dos atributos data
    const endereco = mapElement.getAttribute('data-endereco') || '';
    const bairro = mapElement.getAttribute('data-bairro') || '';
    const cidade = mapElement.getAttribute('data-cidade') || '';
    const estado = mapElement.getAttribute('data-estado') || '';

    // Monta o endereço completo para geocoding
    const fullAddress = [endereco, bairro, cidade, estado].filter(Boolean).join(', ');

    // Inicializa o mapa com coordenadas padrão (São Paulo)
    map = L.map('map').setView([-23.5505, -46.6333], 13);

    // Adiciona o tile layer do OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Se temos um endereço, faz geocoding
    if (fullAddress) {
        geocodeAddress(fullAddress);
    }
}

// Função para geocodificar o endereço
function geocodeAddress(address) {
    const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}&limit=1`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data && data.length > 0) {
                const lat = parseFloat(data[0].lat);
                const lon = parseFloat(data[0].lon);

                // Centraliza o mapa na localização encontrada
                map.setView([lat, lon], 16);

                // Adiciona um marcador
                L.marker([lat, lon]).addTo(map)
                    .bindPopup(address)
                    .openPopup();
            } else {
                console.warn('Endereço não encontrado:', address);
                // Mantém a visualização padrão
            }
        })
        .catch(error => {
            console.error('Erro no geocoding:', error);
        });
}
