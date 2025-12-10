// ==========================================
// 1. VARIÁVEIS GLOBAIS
// ==========================================
let currentOffset = 3; // Para paginação de avaliações
let mapInstance = null; // Para o mapa Leaflet

// Variáveis de Agendamento
let dataSelecionada = null;
let horarioSelecionado = null;
let calendarioAtual = new Date();


// ==========================================
// 2. FUNÇÕES DE NAVEGAÇÃO (ABAS)
// ==========================================
function switchTab(tabId) {
    const navItems = document.querySelectorAll('.profile-tabs li');
    navItems.forEach(item => {
        item.classList.remove('active');
    });

    const panes = document.querySelectorAll('.tab-pane');
    panes.forEach(pane => {
        pane.classList.remove('active-pane');
    });

    if (event && event.currentTarget) {
        event.currentTarget.classList.add('active');
    }

    const activePane = document.getElementById(tabId);
    if (activePane) {
        activePane.classList.add('active-pane');
    }
}


// ==========================================
// 3. FUNÇÕES DE AVALIAÇÃO
// ==========================================
function verMaisAvaliacoes(tipo, idEntidade) {
    event.preventDefault();

    fetch(`/api/avaliacoes/${tipo}/${idEntidade}?offset=${currentOffset}&limit=6`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const reviewsGrid = document.querySelector('.reviews-grid');
                const verMaisContainer = document.querySelector('.ver-mais-container');

                data.avaliacoes.forEach(avaliacao => {
                    const reviewCard = document.createElement('div');
                    reviewCard.className = 'review-card';
                    reviewCard.innerHTML = `
                        <div class="review-header">
                            <div class="reviewer-avatar">${avaliacao.nome_usuario[0].toUpperCase()}</div>
                            <div class="reviewer-data">
                                <strong>${avaliacao.nome_usuario}</strong>
                                <div class="small-stars">
                                    ${Array.from({length: 5}, (_, i) =>
                                        i < avaliacao.nota ? '<i class="fa-solid fa-star"></i>' : '<i class="fa-regular fa-star"></i>'
                                    ).join('')}
                                </div>
                            </div>
                            <span class="review-date">${new Date(avaliacao.data_avaliacao).toLocaleDateString('pt-BR')}</span>
                        </div>
                        <p class="review-text">"${avaliacao.comentario}"</p>
                    `;
                    reviewsGrid.appendChild(reviewCard);
                });

                currentOffset += data.avaliacoes.length;

                if (data.avaliacoes.length < 6) {
                    if(verMaisContainer) verMaisContainer.style.display = 'none';
                }
            } else {
                alert('Erro ao carregar mais avaliações');
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao carregar mais avaliações');
        });
}

function abrirModalAvaliacao(tipo, idEntidade) {
    const modal = document.getElementById('modalAvaliacao');
    const modalTipo = document.getElementById('modalTipo');
    const form = document.getElementById('formAvaliacao');

    modalTipo.textContent = tipo === 'clinica' ? 'Clínica' : 'Profissional';
    modal.classList.add('show');

    form.reset();
    document.getElementById('ratingValue').value = '0';
    updateStarRating(0);

    form.onsubmit = function(e) {
        e.preventDefault();
        enviarAvaliacao(tipo, idEntidade);
    };
}

function fecharModalAvaliacao() {
    const modal = document.getElementById('modalAvaliacao');
    if(modal) modal.classList.remove('show');
}

function updateStarRating(rating) {
    const stars = document.querySelectorAll('#starRating i');
    stars.forEach((star, index) => {
        if (index < rating) {
            star.className = 'fa-solid fa-star active';
        } else {
            star.className = 'fa-regular fa-star';
        }
    });
    document.getElementById('ratingValue').value = rating;
}

function enviarAvaliacao(tipo, idEntidade) {
    const nota = document.getElementById('ratingValue').value;
    const comentario = document.getElementById('comentario').value;

    if (nota == '0') {
        alert('Por favor, selecione uma nota');
        return;
    }

    fetch('/api/avaliacao/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            tipo: tipo,
            id_entidade: idEntidade,
            nota: parseInt(nota),
            comentario: comentario
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            fecharModalAvaliacao();
            location.reload();
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao enviar avaliação');
    });
}


// ==========================================
// 4. FUNÇÕES DE AGENDAMENTO
// ==========================================

function abrirModalAgendamento(servicoId, servicoNome) {
    const modal = document.getElementById('modalAgendamento');
    modal.classList.add('show');

    // Reset state
    dataSelecionada = null;
    horarioSelecionado = null;
    calendarioAtual = new Date();

    document.getElementById('etapaData').style.display = 'block';
    document.getElementById('etapaHorarios').style.display = 'none';
    document.getElementById('btnConfirmarAgendamento').disabled = true;

    renderizarCalendario();

    // Salva os dados no dataset do modal para uso posterior
    modal.dataset.servicoId = servicoId;
    modal.dataset.servicoNome = servicoNome;
}

function fecharModalAgendamento() {
    const modal = document.getElementById('modalAgendamento');
    if(modal) modal.classList.remove('show');
}

function renderizarCalendario() {
    const calendarioContainer = document.getElementById('miniCalendario');
    const ano = calendarioAtual.getFullYear();
    const mes = calendarioAtual.getMonth();

    const nomesMeses = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ];

    const diasSemana = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];

    const primeiroDia = new Date(ano, mes, 1);
    const ultimoDia = new Date(ano, mes + 1, 0);
    const diaSemanaInicio = primeiroDia.getDay();

    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0);

    let html = `
        <div class="calendario-header">
            <button onclick="mudarMes(-1)"><</button>
            <span class="mes-ano">${nomesMeses[mes]} ${ano}</span>
            <button onclick="mudarMes(1)">></button>
        </div>
        <div class="dias-semana">
            ${diasSemana.map(dia => `<div>${dia}</div>`).join('')}
        </div>
        <div class="calendario-grid">
    `;

    for (let i = 0; i < diaSemanaInicio; i++) {
        html += '<div></div>';
    }

    for (let dia = 1; dia <= ultimoDia.getDate(); dia++) {
        const dataAtual = new Date(ano, mes, dia);
        const dataFormatada = dataAtual.toISOString().split('T')[0];
        const ehHoje = dataAtual.getTime() === hoje.getTime();
        const ehPassado = dataAtual < hoje;
        const ehSelecionado = dataSelecionada === dataFormatada;

        let classes = 'dia-calendario';
        if (ehPassado) classes += ' dia-desabilitado';
        if (ehHoje) classes += ' dia-atual';
        if (ehSelecionado) classes += ' dia-selecionado';

        // Note: onclick inline is kept for simplicity within the generated HTML string
        html += `<div class="${classes}" onclick="selecionarData('${dataFormatada}')" ${ehPassado ? 'style="pointer-events: none;"' : ''}>${dia}</div>`;
    }

    html += '</div>';
    calendarioContainer.innerHTML = html;
}

function mudarMes(direcao) {
    calendarioAtual.setMonth(calendarioAtual.getMonth() + direcao);
    renderizarCalendario();
}

function selecionarData(data) {
    dataSelecionada = data;
    renderizarCalendario();

    const dataObj = new Date(data + 'T00:00:00');
    const opcoes = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const dataFormatada = dataObj.toLocaleDateString('pt-BR', opcoes);

    document.getElementById('dataSelecionada').textContent = dataFormatada;

    setTimeout(() => {
        document.getElementById('etapaData').style.display = 'none';
        document.getElementById('etapaHorarios').style.display = 'block';
        carregarHorariosDisponiveis(data);
    }, 300);
}

function voltarParaData() {
    document.getElementById('etapaHorarios').style.display = 'none';
    document.getElementById('etapaData').style.display = 'block';
    horarioSelecionado = null;
    document.getElementById('btnConfirmarAgendamento').disabled = true;
}

function carregarHorariosDisponiveis(data) {
    const listaHorarios = document.getElementById('listaHorarios');
    listaHorarios.innerHTML = '<div style="text-align: center; padding: 20px;">Carregando horários...</div>';

    // Simulação de delay e horários
    setTimeout(() => {
        const horariosMock = [
            '08:00', '08:30', '09:00', '09:30', '10:00', '10:30',
            '14:00', '14:30', '15:00', '15:30', '16:00', '16:30'
        ];
        renderizarHorarios(horariosMock);
    }, 500);
}

function renderizarHorarios(horarios) {
    const listaHorarios = document.getElementById('listaHorarios');
    listaHorarios.innerHTML = horarios.map(horario => `
        <div class="horario-item" onclick="selecionarHorario('${horario}')">
            ${horario}
        </div>
    `).join('');
}

function selecionarHorario(horario) {
    horarioSelecionado = horario;

    document.querySelectorAll('.horario-item').forEach(item => {
        item.classList.remove('horario-selecionado');
    });

    event.target.classList.add('horario-selecionado');
    document.getElementById('btnConfirmarAgendamento').disabled = false;
}

function confirmarAgendamento() {
    if (!dataSelecionada || !horarioSelecionado) {
        alert('Por favor, selecione uma data e horário.');
        return;
    }

    const modal = document.getElementById('modalAgendamento');
    // IMPORTANTE: Recupera o ID salvo no modal
    const servicoId = modal.dataset.servicoId; 

    console.log("Enviando Agendamento:", { servicoId, dataSelecionada, horarioSelecionado });

    fetch('/api/agendar-consulta', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            servico_id: servicoId,
            data: dataSelecionada,
            horario: horarioSelecionado
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Consulta agendada com sucesso!');
            fecharModalAgendamento();
            location.reload();
        } else {
            alert(data.message || 'Erro ao agendar consulta.');
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao conectar com o servidor.');
    });
}


// ==========================================
// 5. FUNÇÕES DO MAPA (LEAFLET)
// ==========================================
function initMap() {
    const mapElement = document.getElementById('map');
    
    if (!mapElement) return;
    if (typeof L === 'undefined') {
        console.error("Leaflet (L) não encontrado.");
        return;
    }
    
    if (mapInstance) {
        mapInstance.invalidateSize();
        return;
    }

    const endereco = mapElement.getAttribute('data-endereco') || '';
    const bairro = mapElement.getAttribute('data-bairro') || '';
    const cidade = mapElement.getAttribute('data-cidade') || '';
    const estado = mapElement.getAttribute('data-estado') || '';

    const fullAddress = [endereco, bairro, cidade, estado, "Brasil"].filter(Boolean).join(', ');

    try {
        mapInstance = L.map('map').setView([-14.2350, -51.9253], 4); 

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(mapInstance);

        if (fullAddress.length > 10) {
            geocodeAddress(fullAddress);
        } else {
            showMapPlaceholder("Endereço não informado.");
        }
    } catch (e) {
        console.error("Erro mapa:", e);
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
                if(address.includes(',')) {
                    const fallbackAddress = address.split(',').slice(1).join(',');
                    if(fallbackAddress.trim().length > 5) {
                        geocodeAddress(fallbackAddress.trim());
                        return;
                    }
                }
                showMapPlaceholder("Não foi possível localizar o endereço exato.");
            }
        })
        .catch(error => {
            console.error('Erro Geocoding:', error);
            showMapPlaceholder("Erro ao carregar mapa.");
        });
}

function showMapPlaceholder(msg) {
    const mapElement = document.getElementById('map');
    if (mapElement) {
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


// ==========================================
// 6. INICIALIZAÇÃO (DOM LOADED)
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    
    // --- LÓGICA DO MAPA (Observador de Abas) ---
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                const target = mutation.target;
                if (target.id === 'local' && target.classList.contains('active-pane')) {
                    setTimeout(() => { initMap(); }, 200);
                }
            }
        });
    });

    const localTab = document.getElementById('local');
    if (localTab) {
        observer.observe(localTab, { attributes: true });
    } else {
        initMap();
    }

    // --- ESTRELAS DA AVALIAÇÃO ---
    const stars = document.querySelectorAll('#starRating i');
    stars.forEach((star, index) => {
        star.addEventListener('click', () => updateStarRating(index + 1));
    });

    // --- CONTADOR DE CARACTERES ---
    const comentario = document.getElementById('comentario');
    const charCount = document.getElementById('charCount');
    if (comentario && charCount) {
        comentario.addEventListener('input', function() {
            charCount.textContent = `${this.value.length}/500 caracteres`;
        });
    }

    // --- CORREÇÃO 1: LISTENER PARA O BOTÃO "AGENDAR" ---
    // Usa 'event delegation' no document para garantir que pegue o botão
    document.addEventListener('click', function(e) {
        const btn = e.target.closest('.btn-agendar'); // Garante que pegou o botão ou ícone dentro dele

        if (btn) {
            e.preventDefault();
            
            const serviceItem = btn.closest('.service-item');
            const serviceName = serviceItem.querySelector('h4').textContent;
            
            // AQUI ESTAVA O ERRO: Pegar o ID diretamente do dataset do botão
            const serviceId = btn.dataset.id; 

            if (!serviceId) {
                alert("Erro: ID do serviço não encontrado.");
                return;
            }

            abrirModalAgendamento(serviceId, serviceName);
        }
    });

    // --- CORREÇÃO 2: LISTENER PARA O BOTÃO "CONFIRMAR" ---
    const btnConfirmar = document.getElementById('btnConfirmarAgendamento');
    if (btnConfirmar) {
        btnConfirmar.addEventListener('click', confirmarAgendamento);
    }
});