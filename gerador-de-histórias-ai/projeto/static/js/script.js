const loading = document.getElementById('loading');
const result = document.getElementById('result');
const storyText = document.getElementById('storyText');
const temaBadge = document.getElementById('temaBadge');
const storyContainer = document.getElementById('storyContainer');
const btnGerar = document.getElementById('btnGerar');
const continuarMensagem = document.getElementById('continuarMensagem');

async function gerarHistoria() {
    result.classList.remove('show');
    continuarMensagem.style.display = 'none';
    
    loading.classList.add('show');
    btnGerar.disabled = true;
    
    try {
        const response = await fetch('/gerar-historia', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        loading.classList.remove('show');
        
        result.classList.add('show');
        
        if (data.success) {
            mostrarHistoria(data);
        } else {
            mostrarErro(data);
        }
        
    } catch (error) {
        loading.classList.remove('show');
        result.classList.add('show');
        mostrarErroConexao(error);
    } finally {
        btnGerar.disabled = false;
    }
}

function mostrarHistoria(data) {
    storyContainer.classList.remove('error');
    temaBadge.innerHTML = `<span class="emoji">📚</span>Tema: ${data.tema}`;
    storyText.textContent = data.historia;
    storyText.classList.remove('error-text');
    
    if (data.mostrar_continuar) {
        continuarMensagem.style.display = 'block';
    }
    
    console.log(`✅ História gerada: ${data.paragrafos} parágrafos`);
    if (data.modelo_usado) {
        console.log(`🤖 Modelo usado: ${data.modelo_usado}`);
    }
}

function mostrarErro(data) {
    storyContainer.classList.add('error');
    temaBadge.innerHTML = '<span class="emoji">❌</span>Erro ao gerar história';
    storyText.innerHTML = `<strong>Detalhes do erro:</strong><br><br>${data.error}<br><br>${data.details || ''}`;
    storyText.classList.add('error-text');
    
    console.error('❌ Erro na API:', data.error);
}

function mostrarErroConexao(error) {
    storyContainer.classList.add('error');
    temaBadge.innerHTML = '<span class="emoji">❌</span>Erro de conexão';
    storyText.innerHTML = `<strong>Não foi possível conectar ao servidor:</strong><br><br>${error.message}`;
    storyText.classList.add('error-text');
    
    console.error('❌ Erro de conexão:', error);
}

document.addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !btnGerar.disabled) {
        gerarHistoria();
    }
});

console.log('✨ Gerador de Histórias inicializado!');
console.log('🎯 Pressione o botão ou Enter para gerar uma história');

