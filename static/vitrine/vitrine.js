document.addEventListener('DOMContentLoaded', () => {

    // --- POPULAR INPUTS COM PARÂMETROS DA URL ---
    const urlParams = new URLSearchParams(window.location.search);
    const buscaParam = urlParams.get('busca');
    const localizacaoParam = urlParams.get('localizacao');

    // --- ELEMENTOS DE FILTRO ---
    const searchInput = document.getElementById('search-input');
    const locationInput = document.getElementById('location-input');
    const btnPesquisar = document.getElementById('btn-pesquisar'); // Botão Azul "Pesquisar"

    // Preencher inputs com parâmetros da URL
    if (searchInput && buscaParam) {
        searchInput.value = buscaParam;
    }
    if (locationInput && localizacaoParam) {
        locationInput.value = localizacaoParam;
    }

    // Select de Especialidade
    const especialidadeSelect = document.getElementById('especialidade-select'); // O select escondido

    // Checkboxes de Modalidade
    const modalidadeChecks = document.querySelectorAll('input[name="modalidade"]');

    // Slider de Preço
    const priceRange = document.getElementById('price-range');
    const priceValue = document.getElementById('price-value');

    // Toggles (Switches)
    const toggleConvenio = document.querySelector('input[name="convenio"]');
    const toggleEstacionamento = document.querySelector('input[name="estacionamento"]');
    const toggleAcessibilidade = document.querySelector('input[name="acessibilidade"]');

    // Variável global para controlar o tipo atual (profissional ou clinica)
    let tipoAtual = 'profissional';

    // Array para armazenar IDs de timeouts pendentes
    let pendingTimeouts = [];

    // --- 1. LÓGICA DO SLIDER DE PREÇO (Visual) ---
    if (priceRange && priceValue) {
        function updateSliderColor(input) {
            const min = input.min;
            const max = input.max;
            const val = input.value;
            const percentage = ((val - min) / (max - min)) * 100;
            input.style.background = `linear-gradient(to right, #003459 ${percentage}%, #d3d3d3 ${percentage}%)`;
        }

        function updateUI() {
            updateSliderColor(priceRange);
            if (priceRange.value == priceRange.max) {
                priceValue.textContent = `R$ ${priceRange.max}+`;
            } else {
                priceValue.textContent = `Até R$ ${priceRange.value}`;
            }
        }

        priceRange.addEventListener('input', () => {
            updateUI();
            // Debounce para não recarregar a cada milímetro arrastado
            clearTimeout(window.searchTimeout);
            window.searchTimeout = setTimeout(() => carregarCards(), 500);
        });

        updateUI();
    }

    // --- 2. FUNÇÃO CENTRAL: CARREGAR CARDS ---
    function carregarCards() {
        const container = document.getElementById('cards-container');
        const countEl = document.getElementById('results-count');

        // 1. LIMPEZA TOTAL: Cancelar timeouts pendentes de carregamentos anteriores
        // Isso impede que cards da aba anterior apareçam "atrasados" na aba nova
        if (typeof pendingTimeouts !== 'undefined') {
            pendingTimeouts.forEach(id => clearTimeout(id));
            pendingTimeouts = [];
        }

        // Limpar container imediatamente
        container.innerHTML = '';

        // Mantém altura mínima consistente durante todo o carregamento
        container.style.minHeight = '400px';
        // Mantém um placeholder visível
        container.innerHTML = '<div style="width: 700px; min-height: 400px; display: flex; align-items: center; justify-content: center;"><p style="text-align: center; padding: 40px;">Carregando...</p></div>';

        // Coletar valores dos filtros
        const params = new URLSearchParams();
        params.append('tipo', tipoAtual);

        // Busca textual (se tiver)
        if (searchInput && searchInput.value) params.append('busca', searchInput.value);
        if (locationInput && locationInput.value) params.append('localizacao', locationInput.value);

        // Especialidade
        if (especialidadeSelect && especialidadeSelect.value && especialidadeSelect.value !== "Todas as especialidades") {
            params.append('especialidade', especialidadeSelect.value);
        }

        // Ordenação
        const ordenarSelect = document.getElementById('ordenar-select');
        if (ordenarSelect && ordenarSelect.value && ordenarSelect.value !== "relevancia") {
            params.append('ordenar', ordenarSelect.value);
        }

        // Modalidades (Múltiplas)
        modalidadeChecks.forEach(chk => {
            if (chk.checked) {
                let modalidadeLimpa = chk.parentElement.textContent.replace(/[0-9]/g, '').trim();
                params.append('modalidades[]', modalidadeLimpa);
            }
        });

        // Preço
        if (priceRange && priceRange.value < 999) {
            params.append('valor_max', priceRange.value);
        }

        // Toggles
        if (toggleConvenio && toggleConvenio.checked) params.append('aceita_convenio', 'true');
        if (toggleEstacionamento && toggleEstacionamento.checked) params.append('estacionamento', 'true');
        if (toggleAcessibilidade && toggleAcessibilidade.checked) params.append('acessibilidade', 'true');

        // CHAMADA AO BACKEND
        fetch(`/api/vitrine?${params.toString()}`)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.resultados) {
                    container.innerHTML = '<div id="layout-placeholder" style="width: 700px; height: 400px; visibility: hidden; position: absolute;"></div>';

                    if (data.resultados.length === 0) {
                        container.innerHTML = '<div style="width: 700px; min-height: 400px; display: flex; align-items: center; justify-content: center;"><p style="text-align: center; color: #777; font-size: 1.1rem;">Nenhum resultado encontrado com esses filtros.</p></div>';
                        countEl.textContent = '0 resultados encontrados';
                        container.style.minHeight = '';
                        return;
                    }

                    countEl.textContent = `${data.resultados.length} ${tipoAtual === 'profissional' ? 'Profissionais' : 'Clínicas'} encontrados`;

                    // Criar todos os cards primeiro
                    const cards = data.resultados.map(item => criarCard(item));

                    // Adicionar cada card com delay sequencial
                    cards.forEach((card, index) => {
                        // CORREÇÃO: Capturamos o ID do timeout
                        const timeoutId = setTimeout(() => {
                            container.appendChild(card);
                            requestAnimationFrame(() => {
                                card.classList.add('animate');
                            });
                        }, index * 50);

                        // CORREÇÃO: Salvamos na lista global para poder cancelar se trocar de aba
                        pendingTimeouts.push(timeoutId);
                    });

                    // Timeout para limpar a altura mínima
                    const totalAnimationTime = (cards.length - 1) * 200 + 600;
                    const cleanupTimeoutId = setTimeout(() => {
                        container.style.minHeight = '';
                    }, totalAnimationTime);
                    
                    // Também salvamos esse timeout de limpeza
                    pendingTimeouts.push(cleanupTimeoutId);

                } else {
                    container.innerHTML = '<div style="width: 700px; min-height: 400px; display: flex; align-items: center; justify-content: center;"><p style="text-align: center; padding: 40px; color: #ff4b4b;">Erro ao carregar resultados.</p></div>';
                    container.style.minHeight = '';
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                container.innerHTML = '<div style="width: 700px; min-height: 400px; display: flex; align-items: center; justify-content: center;"><p style="text-align: center; padding: 40px; color: #ff4b4b;">Erro ao conectar com o servidor.</p></div>';
            });
    }

    // --- 3. FUNÇÃO PARA CARREGAR CONTAGENS DINÂMICAS ---
    function carregarContagens() {
        fetch(`/api/vitrine/counts?tipo=${tipoAtual}`)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.counts) {
                    // Atualizar os spans de count nas checkboxes
                    const modalidadeChecks = document.querySelectorAll('input[name="modalidade"]');
                    modalidadeChecks.forEach(chk => {
                        const label = chk.parentElement;
                        const countSpan = label.querySelector('.count');
                        if (countSpan) {
                            // Pegar o texto da modalidade (remover números existentes)
                            let modalidadeNome = label.textContent.replace(/[0-9]/g, '').trim();
                            // Remover espaços extras e pegar apenas o nome
                            modalidadeNome = modalidadeNome.split(' ')[0]; // Pega primeira palavra
                            const count = data.counts[modalidadeNome] || 0;
                            countSpan.textContent = count;
                        }
                    });
                }
            })
            .catch(error => {
                console.error('Erro ao carregar contagens:', error);
            });
    }

    // --- 4. CRIAÇÃO DO HTML DO CARD (Com Layout Ajustado) ---
    function criarCard(item) {
        const card = document.createElement('div');
        card.className = 'card-item';

        const fotoUrl = item.foto ? `static/uploads/${item.foto}` : null;
        const iconClass = item.tipo === 'profissional' ? 'fa-user-doctor' : 'fa-hospital';
        const badgeClass = item.tipo === 'profissional' ? 'badge-pro' : 'badge-clinic';
        const badgeText = item.tipo === 'profissional' ? 'Profissional' : 'Clínica';
        const linkUrl = item.tipo === 'profissional'
            ? `/profissional/perfil/${item.id}`
            : `/clinica/perfil/${item.id}`;
        const linkText = item.tipo === 'profissional' ? 'Ver Perfil' : 'Ver Clínica';

        // --- PREÇO MÉDIO ---
        let precoDisplay = "Sob consulta";
        if (item.preco !== null && item.preco !== undefined) {
            let valor = parseFloat(item.preco);
            if (!isNaN(valor)) {
                // toFixed(0) remove os centavos (,00) para ficar mais limpo se quiser
                precoDisplay = `Média: R$ ${valor.toFixed(2).replace('.', ',')}`;
            }
        }

        const precoHtml = `<div class="price-tag">
            <strong>${precoDisplay}</strong>
        </div>`;

        // --- MODALIDADES NO RODAPÉ ---
        let modalidadesHtml = '<span class="last-seen">Consulte agenda</span>';
        if (item.modalidades && item.modalidades.length > 0) {
            const mods = item.modalidades.map(m => {
                let icone = '';
                if (m === 'Telemedicina') icone = '<i class="fa-solid fa-video"></i>';
                else if (m === 'Domiciliar') icone = '<i class="fa-solid fa-house-medical"></i>';
                else icone = '<i class="fa-solid fa-hospital-user"></i>';

                return `<span title="${m}" style="margin-right:8px; font-size: 0.85rem; color: #555; display:inline-flex; align-items:center; gap:4px;">${icone} ${m}</span>`;
            }).join('');

            modalidadesHtml = `<div style="display:flex; flex-wrap:wrap; margin-top:10px; width:100%; border-top:1px solid #eee; padding-top:8px;">${mods}</div>`;
        }

        card.innerHTML = `
            <div class="card-logo ${item.tipo === 'clinica' ? 'logo-clinic' : ''}">
                ${fotoUrl
                ? `<img src="${fotoUrl}" alt="${item.nome}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%;">`
                : `<i class="fa-solid ${iconClass}"></i>`
            }
            </div>
            <div class="card-info">
                <div class="card-header-info">
                    <h4>${item.nome}</h4>
                    <span class="badge ${badgeClass}">${badgeText}</span>
                </div>
                
                ${item.especialidade ? `<p class="specialty" style="color:var(--azul-escuro); font-weight:500; margin-bottom:5px;">${item.especialidade}</p>` : ''}
                
                <div class="card-bottom-info">
                    <div class="location-info">
                        <i class="fa-solid fa-map-pin"></i> ${item.localizacao || 'Localização não informada'}
                    </div>
                </div>
            </div>
            
            <div class="card-action">
                ${precoHtml}
                <a href="${linkUrl}" class="btn-view">${linkText} <i class="fa-solid fa-arrow-right"></i></a>
                
                ${modalidadesHtml}
            </div>
        `;

        return card;
    }

    // --- 4. EVENT LISTENERS (Escutar os cliques) ---

    // Inicialização
    carregarContagens();
    carregarCards();

    // Botão de Pesquisa (Topo)
    if (btnPesquisar) {
        btnPesquisar.addEventListener('click', (e) => {
            e.preventDefault(); // Evita recarregar a página
            carregarCards();
            carregarContagens(); // Atualizar contagens após pesquisa
        });
    }

    // Troca de Tipo (Profissional/Clínica)
    const typeRadios = document.querySelectorAll('input[name="type"]');
    typeRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            tipoAtual = e.target.id === 'type-pro' ? 'profissional' : 'clinica';
            // Cancelar timeouts pendentes antes de trocar
            pendingTimeouts.forEach(id => clearTimeout(id));
            pendingTimeouts = [];
            carregarContagens(); // Atualizar contagens quando trocar tipo
            carregarCards();
        });
    });

    // Checkboxes (Modalidade) e Toggles
    const todosInputsFiltro = document.querySelectorAll('input[type="checkbox"]');
    todosInputsFiltro.forEach(input => {
        input.addEventListener('change', () => {
            carregarCards();
        });
    });

    // --- LÓGICA DOS SELECTS CUSTOMIZADOS (Especialidade) ---
    const allCustomSelects = document.querySelectorAll('.custom-select-wrapper');

    allCustomSelects.forEach(wrapper => {
        const customSelect = wrapper.querySelector('.custom-select');
        const realSelect = wrapper.querySelector('select');
        const selectedSpan = customSelect.querySelector('.selected-option');
        const options = customSelect.querySelectorAll('.custom-options li');

        // Abrir/Fechar
        customSelect.addEventListener('click', (e) => {
            document.querySelectorAll('.custom-select').forEach(other => {
                if (other !== customSelect) other.classList.remove('open');
            });
            customSelect.classList.toggle('open');
            e.stopPropagation();
        });

        // Selecionar Opção
        options.forEach(option => {
            option.addEventListener('click', (e) => {
                e.stopPropagation();

                selectedSpan.textContent = option.textContent;
                selectedSpan.style.color = "#333";

                // Atualiza o select escondido
                const value = option.getAttribute('data-value');
                realSelect.value = value;

                customSelect.classList.remove('open');

                // IMPORTANTE: Disparar recarregamento ao mudar especialidade
                carregarCards();
                carregarContagens(); // Atualizar contagens quando especialidade muda
            });
        });
    });

    // Fechar ao clicar fora
    document.addEventListener('click', () => {
        document.querySelectorAll('.custom-select').forEach(select => {
            select.classList.remove('open');
        });
    });
});