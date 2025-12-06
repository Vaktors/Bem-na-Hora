document.addEventListener('DOMContentLoaded', () => {
    
    // --- ESTADO DA DATA ---
    let dataAtual = new Date(2025, 11, 5); // 05 Dez 2025
    let dataMiniCalendario = new Date(dataAtual); 
    let modoVisualizacao = 'dia'; 

    // --- SELETORES ---
    const displayData = document.querySelector('.date-display h2');
    const navButtons = document.querySelectorAll('.date-display .icon-btn');
    const btnAnterior = navButtons[0];
    const btnProximo = navButtons[1];
    const btnHoje = document.querySelector('.today-badge');
    const btnModoDia = document.querySelector('.view-mode .mode-btn:nth-child(1)');
    const btnModoSemana = document.querySelector('.view-mode .mode-btn:nth-child(2)');
    
    const timelineHeaderEvents = document.querySelector('.timeline-header .events-column');
    const timelineHeader = document.querySelector('.timeline-header');
    const timelineBody = document.getElementById('timeline-body');
    const checkboxesMedicos = document.querySelectorAll('.doc-filter');
    const checkAll = document.getElementById('filter-all');

    const miniMonthDisplay = document.querySelector('.current-month');
    const miniGrid = document.querySelector('.mini-calendar-grid');
    const miniNavPrev = document.querySelector('.nav-arrows .fa-chevron-left');
    const miniNavNext = document.querySelector('.nav-arrows .fa-chevron-right');

    // --- DADOS MOCKADOS (CONSULTAS) ---
    // Adicionei mais dados para popular a semana
    const consultasBase = [
        { id: 1, dia: 5, hora: '08:00', duracao: 60, paciente: 'Mariana Souza', procedimento: 'Consulta Rotina', medico: 'Dr. Carlos', tipo: 'doc1' },
        { id: 2, dia: 5, hora: '09:00', duracao: 30, paciente: 'João Pereira', procedimento: 'Retorno', medico: 'Dra. Ana', tipo: 'doc2' },
        { id: 3, dia: 5, hora: '09:30', duracao: 60, paciente: 'Fernanda Lima', procedimento: 'Estética', medico: 'Dra. Ana', tipo: 'doc2' },
        { id: 4, dia: 5, hora: '10:00', duracao: 60, paciente: 'Roberto Campos', procedimento: 'Ortopedia', medico: 'Dr. Roberto', tipo: 'doc3' },
        { id: 5, dia: 5, hora: '14:00', duracao: 45, paciente: 'Lucia Santos', procedimento: 'ECG', medico: 'Dr. Carlos', tipo: 'doc1' },
        // Consultas para outros dias da semana
        { id: 6, dia: 1, hora: '08:00', duracao: 60, paciente: 'Ana Paula', procedimento: 'Consulta', medico: 'Dr. Carlos', tipo: 'doc1' }, // Segunda
        { id: 7, dia: 3, hora: '10:00', duracao: 60, paciente: 'Bruno Lima', procedimento: 'Ortopedia', medico: 'Dr. Roberto', tipo: 'doc3' }, // Quarta
        { id: 8, dia: 6, hora: '09:00', duracao: 120, paciente: 'Pedro Alves', procedimento: 'Cirurgia', medico: 'Dr. Roberto', tipo: 'doc3' } // Sábado
    ];

    // --- HELPER FUNCTIONS ---
    function getInicioFimSemana(data) {
        const inicio = new Date(data);
        inicio.setDate(data.getDate() - data.getDay()); // Domingo
        const fim = new Date(inicio);
        fim.setDate(inicio.getDate() + 6); // Sábado
        return { inicio, fim };
    }

    // --- 1. FUNÇÕES DE DATA E HEADER ---
    function atualizarHeader() {
        if (modoVisualizacao === 'dia') {
            const opcoes = { weekday: 'long', day: 'numeric', month: 'long' };
            let texto = dataAtual.toLocaleDateString('pt-BR', opcoes);
            displayData.textContent = texto.charAt(0).toUpperCase() + texto.slice(1);
        } else {
            const { inicio, fim } = getInicioFimSemana(dataAtual);
            const fmt = d => d.toLocaleDateString('pt-BR', { day: 'numeric', month: 'short' });
            displayData.textContent = `${fmt(inicio)} - ${fmt(fim)}`;
        }
    }

    // --- 2. LÓGICA DO MINI CALENDÁRIO ---
    function renderizarMiniCalendario() {
        miniGrid.innerHTML = '';
        
        // Cabeçalho Dias
        ['D','S','T','Q','Q','S','S'].forEach(d => {
            const el = document.createElement('div');
            el.className = 'weekday';
            el.textContent = d;
            miniGrid.appendChild(el);
        });

        // Título Mês
        const ano = dataMiniCalendario.getFullYear();
        const mes = dataMiniCalendario.getMonth();
        const nomeMes = new Date(ano, mes, 1).toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' });
        miniMonthDisplay.textContent = nomeMes.charAt(0).toUpperCase() + nomeMes.slice(1);

        // Lógica de Dias
        const primeiroDiaMes = new Date(ano, mes, 1).getDay();
        const ultimoDiaMes = new Date(ano, mes + 1, 0).getDate();
        const ultimoDiaMesAnterior = new Date(ano, mes, 0).getDate();

        // Semana Selecionada (para highlight)
        const { inicio: semInicio, fim: semFim } = getInicioFimSemana(dataAtual);

        // Dias mês anterior
        for (let i = 0; i < primeiroDiaMes; i++) {
            const dia = ultimoDiaMesAnterior - (primeiroDiaMes - 1) + i;
            criarDiaMini(dia, 'prev-month', null); // Sem evento de clique por enquanto
        }

        // Dias mês atual
        for (let i = 1; i <= ultimoDiaMes; i++) {
            let classes = ['day'];
            const dataDoDia = new Date(ano, mes, i);

            if (modoVisualizacao === 'dia') {
                if (i === dataAtual.getDate() && mes === dataAtual.getMonth() && ano === dataAtual.getFullYear()) {
                    classes.push('active');
                }
            } else {
                // Modo Semana: Verifica intervalo
                // Zera horas para comparação justa
                const dTime = dataDoDia.setHours(0,0,0,0);
                const sTime = semInicio.setHours(0,0,0,0);
                const fTime = semFim.setHours(0,0,0,0);

                if (dTime >= sTime && dTime <= fTime) {
                    classes.push('week-range');
                    if (dTime === sTime) classes.push('week-start');
                    if (dTime === fTime) classes.push('week-end');
                }
            }

            criarDiaMini(i, classes.join(' '), dataDoDia);
        }
    }

    function criarDiaMini(numero, classeString, dataCompleta) {
        const el = document.createElement('div');
        el.className = classeString;
        el.textContent = numero;
        
        if (dataCompleta) {
            el.onclick = () => {
                dataAtual = new Date(dataCompleta);
                atualizarHeader();
                renderizarTimeline();
                renderizarMiniCalendario();
            };
        }
        miniGrid.appendChild(el);
    }

    // --- 3. TIMELINE E CONSULTAS ---
    function renderizarTimeline() {
        timelineBody.innerHTML = '';
        
        if (modoVisualizacao === 'dia') {
            // --- MODO DIA: Configuração Original ---
            timelineHeader.classList.remove('week-mode');
            timelineHeaderEvents.innerHTML = 'Agenda do Dia'; // Reset header text

            for (let i = 7; i <= 19; i++) {
                const hourString = i.toString().padStart(2, '0') + ':00';
                const row = document.createElement('div');
                row.className = 'time-slot';
                row.id = `slot-${i}`;
                
                row.innerHTML = `
                    <div class="slot-time">${hourString}</div>
                    <div class="slot-events"></div>
                `;
                timelineBody.appendChild(row);
            }
            inserirConsultasDia();

        } else {
            // --- MODO SEMANA: Configuração de Grid ---
            timelineHeader.classList.add('week-mode');
            
            // Gerar Cabeçalho dos Dias (Dom - Sáb)
            timelineHeaderEvents.innerHTML = '';
            const { inicio } = getInicioFimSemana(dataAtual);
            const diaIterador = new Date(inicio);
            const diasSemanaNomes = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];

            for (let i = 0; i < 7; i++) {
                const div = document.createElement('div');
                div.className = 'day-header-cell';
                
                // Highlight se for hoje
                const hojeReal = new Date();
                if (diaIterador.getDate() === hojeReal.getDate() && diaIterador.getMonth() === hojeReal.getMonth()) {
                    div.classList.add('today');
                }

                div.textContent = `${diasSemanaNomes[i]} ${diaIterador.getDate()}`;
                timelineHeaderEvents.appendChild(div);
                
                // Avança dia
                diaIterador.setDate(diaIterador.getDate() + 1);
            }

            // Gerar Linhas de Horário com 7 Colunas
            for (let i = 7; i <= 19; i++) {
                const hourString = i.toString().padStart(2, '0') + ':00';
                const row = document.createElement('div');
                row.className = 'time-slot week-mode';
                
                let cellsHTML = '';
                // 0 = Dom, 1 = Seg ... 6 = Sab
                for (let d = 0; d < 7; d++) {
                    cellsHTML += `<div class="day-cell" id="slot-${d}-${i}"></div>`;
                }

                row.innerHTML = `
                    <div class="slot-time">${hourString}</div>
                    <div class="slot-events">${cellsHTML}</div>
                `;
                timelineBody.appendChild(row);
            }
            inserirConsultasSemana();
        }
    }

    function inserirConsultasDia() {
        const medicosAtivos = getMedicosAtivos();
        
        // Filtra pelo dia específico (simulado pelo dia do mês no objeto)
        const consultas = consultasBase.filter(c => 
            c.dia === dataAtual.getDate() && 
            (checkAll.checked || medicosAtivos.includes(c.medico))
        );

        consultas.forEach(consulta => {
            const hora = parseInt(consulta.hora.split(':')[0]);
            const slot = document.querySelector(`#slot-${hora} .slot-events`);
            if (slot) criarCard(consulta, slot, false);
        });
    }

    function inserirConsultasSemana() {
        const medicosAtivos = getMedicosAtivos();
        const { inicio, fim } = getInicioFimSemana(dataAtual);

        // No exemplo real, filtrariamos por data completa. Aqui usamos o 'dia' (1-31)
        // Precisamos saber qual dia da semana (0-6) aquele dia do mês cai
        // Para simplificar o mock, vamos assumir que o 'dia' no objeto é dia do mês atual
        
        consultasBase.forEach(consulta => {
            // Filtro médico
            if (!checkAll.checked && !medicosAtivos.includes(consulta.medico)) return;

            // Simula data da consulta
            const dataConsulta = new Date(2025, 11, consulta.dia); // Dez 2025
            
            // Verifica se está na semana visualizada
            if (dataConsulta >= inicio && dataConsulta <= fim) {
                const diaSemanaIndex = dataConsulta.getDay(); // 0 a 6
                const hora = parseInt(consulta.hora.split(':')[0]);
                
                const slotId = `slot-${diaSemanaIndex}-${hora}`;
                const slot = document.getElementById(slotId);
                
                if (slot) criarCard(consulta, slot, true);
            }
        });
    }

    function criarCard(consulta, container, isCompact) {
        const card = document.createElement('div');
        const classeCompacta = isCompact ? 'compact' : '';
        card.className = `appointment-card app-card-${consulta.tipoMedico} ${classeCompacta}`;
        
        if (isCompact) {
            // Layout Compacto (Semana)
            card.innerHTML = `
                <div style="display:flex; justify-content:space-between;">
                    <span class="app-time">${consulta.hora}</span>
                </div>
                <span class="app-patient">${consulta.paciente}</span>
            `;
        } else {
            // Layout Completo (Dia)
            card.innerHTML = `
                <div class="card-header">
                    <span class="app-time">${consulta.hora}</span>
                    <span class="app-patient">${consulta.paciente}</span>
                </div>
                <span class="app-details">${consulta.procedimento}</span>
                <span class="app-doctor"><i class="fa-solid fa-user-doctor"></i> ${consulta.medico}</span>
            `;
        }
        container.appendChild(card);
    }

    function getMedicosAtivos() {
        return Array.from(checkboxesMedicos)
            .filter(cb => cb.checked)
            .map(cb => cb.value);
    }

    // --- EVENT LISTENERS ---

    btnAnterior.addEventListener('click', () => {
        const dias = modoVisualizacao === 'dia' ? 1 : 7;
        dataAtual.setDate(dataAtual.getDate() - dias);
        atualizarHeader();
        renderizarTimeline();
        renderizarMiniCalendario(); 
    });

    btnProximo.addEventListener('click', () => {
        const dias = modoVisualizacao === 'dia' ? 1 : 7;
        dataAtual.setDate(dataAtual.getDate() + dias);
        atualizarHeader();
        renderizarTimeline();
        renderizarMiniCalendario();
    });

    btnHoje.addEventListener('click', () => {
        dataAtual = new Date(2025, 11, 5); 
        dataMiniCalendario = new Date(dataAtual);
        atualizarHeader();
        renderizarTimeline();
        renderizarMiniCalendario();
    });

    // Navegação Mini Calendário (Mês)
    miniNavPrev.addEventListener('click', () => {
        dataMiniCalendario.setMonth(dataMiniCalendario.getMonth() - 1);
        renderizarMiniCalendario();
    });

    miniNavNext.addEventListener('click', () => {
        dataMiniCalendario.setMonth(dataMiniCalendario.getMonth() + 1);
        renderizarMiniCalendario();
    });

    // Filtros
    checkboxesMedicos.forEach(cb => {
        cb.addEventListener('change', () => {
            if (!cb.checked) checkAll.checked = false;
            renderizarTimeline();
        });
    });

    checkAll.addEventListener('change', (e) => {
        checkboxesMedicos.forEach(cb => cb.checked = e.target.checked);
        renderizarTimeline();
    });

    // Modos de Visualização
    btnModoDia.addEventListener('click', () => {
        if(modoVisualizacao !== 'dia') {
            modoVisualizacao = 'dia';
            btnModoDia.classList.add('active');
            btnModoSemana.classList.remove('active');
            atualizarHeader();
            renderizarTimeline();
            renderizarMiniCalendario(); // Atualiza highlight
        }
    });

    btnModoSemana.addEventListener('click', () => {
        if(modoVisualizacao !== 'semana') {
            modoVisualizacao = 'semana';
            btnModoSemana.classList.add('active');
            btnModoDia.classList.remove('active');
            atualizarHeader();
            renderizarTimeline();
            renderizarMiniCalendario(); // Atualiza highlight
        }
    });

    // --- INICIALIZAÇÃO ---
    atualizarHeader();
    renderizarMiniCalendario();
    renderizarTimeline();
});