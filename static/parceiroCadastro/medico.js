document.addEventListener('DOMContentLoaded', function() {
    
    /* ==========================================================================
       1. LÓGICA DO MODAL (TERMOS DE USO)
       ========================================================================== */
    const openModalBtn = document.getElementById('open-terms-modal');
    const modalOverlay = document.getElementById('terms-modal');
    const closeModalBtn = document.getElementById('close-modal-btn');

    if (openModalBtn && modalOverlay && closeModalBtn) {
        // Abrir
        openModalBtn.addEventListener('click', (e) => {
            e.preventDefault(); // Impede a tela de pular para o topo
            modalOverlay.classList.add('show');
        });

        // Fechar no X
        closeModalBtn.addEventListener('click', () => {
            modalOverlay.classList.remove('show');
        });

        // Fechar clicando fora
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) {
                modalOverlay.classList.remove('show');
            }
        });
    } else {
        console.warn('Elementos do modal não encontrados. Verifique os IDs no HTML.');
    }

    /* ==========================================================================
       2. LÓGICA DO TOGGLE (PROFISSIONAL vs CLÍNICA)
       ========================================================================== */
    const radioPro = document.getElementById('type-pro');
    const radioClinic = document.getElementById('type-clinic');
    const formTitle = document.getElementById('form-title');
    const royalDesc = document.getElementById('royal-desc');
    const registroInput = document.getElementById('registro-input');
    
    const fieldsProf = document.querySelectorAll('.field-prof');
    const fieldsClinic = document.querySelectorAll('.field-clinic');

    function setProfessional() {
        if(!formTitle) return;
        formTitle.innerText = "Cadastro Profissional";
        if(royalDesc) royalDesc.innerText = "Gerencie seus atendimentos e aumente sua visibilidade.";
        if(registroInput) registroInput.placeholder = "CRM / CRO / CRF";
        
        fieldsProf.forEach(el => {
            el.style.display = 'block';
            el.disabled = false;
            el.required = true;
        });
        fieldsClinic.forEach(el => {
            el.style.display = 'none';
            el.disabled = true;
            el.required = false;
        });
    }

    function setClinic() {
        if(!formTitle) return;
        formTitle.innerText = "Cadastro de Clínica";
        if(royalDesc) royalDesc.innerText = "Cadastre sua empresa e gerencie sua equipe técnica.";
        if(registroInput) registroInput.placeholder = "Registro Técnico (RT)";
        
        fieldsClinic.forEach(el => {
            el.style.display = 'block';
            el.disabled = false;
            el.required = true;
        });
        fieldsProf.forEach(el => {
            el.style.display = 'none';
            el.disabled = true;
            el.required = false;
        });
    }

    if (radioPro && radioClinic) {
        radioPro.addEventListener('change', setProfessional);
        radioClinic.addEventListener('change', setClinic);

        // Checagem inicial
        if (radioClinic.checked) {
            setClinic();
        } else {
            setProfessional();
        }
    }

    /* ==========================================================================
       3. MÁSCARAS (CPF, CNPJ, TELEFONE)
       ========================================================================== */
    function applyMask(input, maskFunction) {
        if (input) {
            input.addEventListener('input', (e) => {
                e.target.value = maskFunction(e.target.value);
            });
        }
    }

    const maskCPF = (v) => v.replace(/\D/g, "").replace(/(\d{3})(\d)/, "$1.$2").replace(/(\d{3})(\d)/, "$1.$2").replace(/(\d{3})(\d{1,2})$/, "$1-$2").substring(0, 14);
    const maskCNPJ = (v) => v.replace(/\D/g, "").replace(/^(\d{2})(\d)/, "$1.$2").replace(/^(\d{2})\.(\d{3})(\d)/, "$1.$2.$3").replace(/\.(\d{3})(\d)/, ".$1/$2").replace(/(\d{4})(\d)/, "$1-$2").substring(0, 18);
    const maskPhone = (v) => v.replace(/\D/g, "").replace(/^(\d{2})(\d)/g, "($1) $2").replace(/(\d)(\d{4})$/, "$1-$2").substring(0, 15);

    // Seleciona inputs pelos atributos para garantir que pegue o certo
    const inputCPF = document.querySelector('input[placeholder="CPF"]');
    const inputCNPJ = document.querySelector('input[placeholder="CNPJ"]');
    const inputPhone = document.querySelector('input[type="tel"]');

    if(inputCPF) applyMask(inputCPF, maskCPF);
    if(inputCNPJ) applyMask(inputCNPJ, maskCNPJ);
    if(inputPhone) applyMask(inputPhone, maskPhone);

});