document.addEventListener('DOMContentLoaded', () => {

    const priceRange = document.getElementById('price-range');
    const priceValue = document.getElementById('price-value');

    if (priceRange && priceValue) {

        // Função para pintar o fundo do slider (Turquesa atrás, Cinza na frente)
        function updateSliderColor(input) {
            const min = input.min;
            const max = input.max;
            const val = input.value;

            // Calcula a porcentagem atual (0% a 100%)
            const percentage = ((val - min) / (max - min)) * 100;

            // Atualiza o CSS: Turquesa até X%, Cinza dali pra frente
            // OBS: As cores devem bater com suas variáveis CSS
            // #003459 é o seu --turques
            // #d3d3d3 é o cinza padrão
            input.style.background = `linear-gradient(to right, #003459 ${percentage}%, #d3d3d3 ${percentage}%)`;
        }

        // Função para atualizar o texto e a cor
        function updateUI() {
            // Atualiza a cor
            updateSliderColor(priceRange);

            // Atualiza o Texto
            if (priceRange.value == priceRange.max) {
                // ALTERAÇÃO: Usa o max (999) dinamicamente
                priceValue.textContent = `R$ ${priceRange.max}+`;
            } else {
                priceValue.textContent = `Até R$ ${priceRange.value}`;
            }
        }

        // Evento: Quando arrastar
        priceRange.addEventListener('input', updateUI);

        // Inicializa (para já carregar com a cor certa)
        updateUI();
    }

    // Opcional: Efeito simples nos botões de Card
    const cards = document.querySelectorAll('.card-item');
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            // Lógica visual extra se desejar
        });
    });

    // Aqui você pode adicionar lógica para filtrar os cards 
    // baseado no toggle "Clínica vs Profissional" se desejar fazer via JS puro
    const typeRadios = document.querySelectorAll('input[name="type"]');

    typeRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            console.log(`Filtro alterado para: ${e.target.id === 'type-pro' ? 'Profissional' : 'Clínica'}`);
            // Exemplo: Filtrar visualmente (apenas demo)
            // Se fosse real, chamaria uma API ou filtraria a lista
        });
    });

    // --- LÓGICA DOS SELECTS CUSTOMIZADOS ---

    const allCustomSelects = document.querySelectorAll('.custom-select-wrapper');

    allCustomSelects.forEach(wrapper => {
        const customSelect = wrapper.querySelector('.custom-select');
        const realSelect = wrapper.querySelector('select');
        const selectedSpan = customSelect.querySelector('.selected-option');
        const options = customSelect.querySelectorAll('.custom-options li');

        // Toggle (Abrir/Fechar)
        customSelect.addEventListener('click', (e) => {
            // Fecha outros selects abertos
            document.querySelectorAll('.custom-select').forEach(other => {
                if (other !== customSelect) other.classList.remove('open');
            });

            customSelect.classList.toggle('open');
            e.stopPropagation(); // Impede que o clique feche imediatamente
        });

        // Selecionar Opção
        options.forEach(option => {
            option.addEventListener('click', (e) => {
                e.stopPropagation();

                // Atualiza Texto Visual
                selectedSpan.textContent = option.textContent;
                selectedSpan.style.color = "#333"; // Cor de texto ativo

                // Atualiza Select Real (Oculto)
                const value = option.getAttribute('data-value');
                realSelect.value = value;

                // Fecha
                customSelect.classList.remove('open');

                // Opcional: Dispara evento de mudança para outros scripts ouvirem
                const event = new Event('change');
                realSelect.dispatchEvent(event);

                console.log("Selecionado:", value); // Para teste
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

/* --- JS DO HEADER (Compatível com estrutura original) --- */
function iniciarHeader() {
  // Captura o header para delegação de eventos
  const header = document.querySelector('.header');

  if (header) {
    header.addEventListener('click', (e) => {
      
      // 1. Clicou no botão LOGIN -> Vira FOTO
      if (e.target.classList.contains('btn-login')) {
        e.preventDefault();
        const btn = e.target;
        
        // Cria o elemento da foto (wrapper)
        const profilePic = document.createElement('div');
        profilePic.className = 'profile-pic';
        profilePic.innerHTML = `
          <img src="img/do-utilizador.png" alt="Perfil" onerror="this.src='https://cdn-icons-png.flaticon.com/512/3135/3135715.png'">
          <div class="dropdown-menu">
            <a href="#" class="dropdown-item">Meu Perfil</a>
            <div class="dropdown-divider"></div>
            <a href="#" class="dropdown-item">Sair</a>
          </div>
        `;
        
        // Substitui o botão pela foto dentro do header
        btn.parentNode.replaceChild(profilePic, btn);
      }
      
      // 2. Clicou na FOTO -> Abre Dropdown
      else if (e.target.closest('.profile-pic')) {
        const pic = e.target.closest('.profile-pic');
        const menu = pic.querySelector('.dropdown-menu');
        if (menu) {
          // Fecha outros se tiver
          document.querySelectorAll('.dropdown-menu.show').forEach(m => {
            if (m !== menu) m.classList.remove('show');
          });
          menu.classList.toggle('show');
          e.stopPropagation(); 
        }
      }

      // 3. Clicou em SAIR -> Volta a ser BOTÃO
      else if (e.target.classList.contains('dropdown-item') && e.target.textContent.trim() === 'Sair') {
        e.preventDefault();
        const pic = e.target.closest('.profile-pic');
        if (pic) {
          const btn = document.createElement('button');
          btn.className = 'btn-login';
          btn.textContent = 'Login';
          pic.parentNode.replaceChild(btn, pic);
        }
      }
    });
  }

  // Fecha dropdown ao clicar fora
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.profile-pic')) {
      document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
        menu.classList.remove('show');
      });
    }
  });
}

// Inicializa
document.addEventListener('DOMContentLoaded', iniciarHeader);