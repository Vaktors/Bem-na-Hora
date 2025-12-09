// --- FUNÇÃO DE ABAS (Mantida Original) ---
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
    if (event && event.currentTarget) {
        event.currentTarget.classList.add('active');
    }

    // 4. Mostra o conteúdo correspondente
    const activePane = document.getElementById(tabId);
    if (activePane) {
        activePane.classList.add('active-pane');
    }
}

// --- LÓGICA DE INTERFACE E MAPA ---
document.addEventListener('DOMContentLoaded', () => {
    
    // --- DROPDOWN (Mantido Original) ---
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

    // --- LÓGICA DO MAPA (Corrigida) ---
    
    // Observer para detectar quando a aba 'local' é aberta
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                const target = mutation.target;
                if (target.id === 'local' && target.classList.contains('active-pane')) {
                    // Delay para garantir que a div está visível antes de desenhar o mapa
                    setTimeout(() => {
                        initMap();
                    }, 200);
                }
            }
        });
    });

    const localTab = document.getElementById('local');
    if (localTab) {
        observer.observe(localTab, { attributes: true });
    } else {
        // Se não tiver abas ou a aba já estiver visível, tenta iniciar direto
        initMap();
    }
});

// Variável global para o mapa
let mapInstance = null;

function initMap() {
    const mapElement = document.getElementById('map');
    
    // Verificações de segurança
    if (!mapElement) return;
    if (typeof L === 'undefined') {
        console.error("Leaflet (L) não foi carregado. Adicione os scripts no HTML.");
        return;
    }
    
    // Se o mapa já existe, apenas atualiza o tamanho (correção para abas)
    if (mapInstance) {
        mapInstance.invalidateSize();
        return;
    }

    // Coletar dados
    const endereco = mapElement.getAttribute('data-endereco') || '';
    const bairro = mapElement.getAttribute('data-bairro') || '';
    const cidade = mapElement.getAttribute('data-cidade') || '';
    const estado = mapElement.getAttribute('data-estado') || '';

    // Monta string de busca
    const fullAddress = [endereco, bairro, cidade, estado, "Brasil"].filter(Boolean).join(', ');

    // Inicializa o mapa
    try {
        mapInstance = L.map('map').setView([-14.2350, -51.9253], 4); // Centro do Brasil inicial

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(mapInstance);

        if (fullAddress.length > 10) { // Validação simples se tem endereço
            geocodeAddress(fullAddress);
        } else {
            showMapPlaceholder("Endereço não informado.");
        }
    } catch (e) {
        console.error("Erro ao iniciar mapa:", e);
    }
}

function geocodeAddress(address) {
    const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}&limit=1`;

    fetch(url, { headers: { 'User-Agent': 'BemNaHoraApp/1.0' } })
        .then(response => response.json())
        .then(data => {
            if (data && data.length > 0) {
                const lat = parseFloat(data[0].lat);
                const lon = parseFloat(data[0].lon);

                mapInstance.setView([lat, lon], 16);

                L.marker([lat, lon]).addTo(mapInstance)
                    .bindPopup(`<b>Endereço:</b><br>${address}`)
                    .openPopup();
            } else {
                console.warn('Endereço não encontrado nas coordenadas:', address);
                // Tenta buscar apenas pela cidade se falhar
                if(address.includes(',')) {
                    // Pega o que está depois da primeira vírgula (geralmente Bairro/Cidade)
                    const fallbackAddress = address.split(',').slice(1).join(',');
                    if(fallbackAddress.trim().length > 5) {
                         geocodeAddress(fallbackAddress.trim());
                         return;
                    }
                }
                showMapPlaceholder("Endereço exato não localizado no mapa.");
            }
        })
        .catch(error => {
            console.error('Erro no geocoding:', error);
            showMapPlaceholder("Erro de conexão com o mapa.");
        });
}

function showMapPlaceholder(msg) {
    const mapElement = document.getElementById('map');
    // Só substitui se o mapa não foi desenhado corretamente ou se quisermos forçar erro
    if (mapElement) {
        // Se existir instância de mapa, removemos para limpar a visualização cinza
        if(mapInstance) {
            mapInstance.remove();
            mapInstance = null;
        }

        const endereco = mapElement.getAttribute('data-endereco') || '';
        const cidade = mapElement.getAttribute('data-cidade') || '';
        const linkGoogle = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(endereco + ' ' + cidade)}`;

        mapElement.innerHTML = `
            <div class="map-placeholder" style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%; text-align:center; padding:20px; background:#f9f9f9;">
                <i class="fa-solid fa-map-location-dot" style="font-size:40px; color:#ccc; margin-bottom:10px;"></i>
                <p style="color:#666; margin-bottom:15px;">${msg}</p>
                <a href="${linkGoogle}" target="_blank" class="btn-secondary" style="padding: 8px 16px; font-size: 0.9rem;">
                   <i class="fa-solid fa-external-link-alt"></i> Abrir no Google Maps
                </a>
            </div>
        `;
    }
}