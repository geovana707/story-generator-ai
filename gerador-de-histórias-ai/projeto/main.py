from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
import random
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Gerador de Histórias Aleatórias")

# Montar pasta static para servir CSS e JS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar templates
templates = Jinja2Templates(directory="templates")

# Chave da API do Google Gemini
GOOGLE_API_KEY = "AIzaSyBfLZmDqbNHo6LaO2-Eu6JvVe__5I9NAA0"

# Lista de modelos em ordem de prioridade
MODELOS = [
    "gemini-2.0-flash",
    "gemini-flash-latest",
    "gemini-2.5-flash-lite",
    "gemini-flash-lite-latest"
]

# Temas aleatórios
TEMAS = [
    "um astronauta perdido em um planeta desconhecido",
    "uma bruxa que perdeu seus poderes mágicos",
    "um robô que aprende a sentir emoções",
    "um dragão vegetariano em um mundo de carnívoros",
    "uma cidade flutuante nas nuvens",
    "um detetive que pode ver fantasmas",
    "uma biblioteca onde os livros ganham vida à noite",
    "um gato que se transforma em humano durante a lua cheia",
    "uma floresta encantada que muda de lugar",
    "um cientista que descobre uma dimensão paralela",
    "um pirata que tem medo do oceano",
    "uma bailarina de circo com poderes telecinéticos",
    "um chef de cozinha que pode falar com os alimentos",
    "uma nave espacial abandonada cheia de mistérios",
    "um pintor cujas obras se tornam realidade",
    "uma escola para super-heróis aposentados",
    "um relojoeiro que pode voltar no tempo",
    "uma sereia que sonha em explorar o deserto",
    "um vampiro que trabalha como dentista",
    "uma máquina do tempo quebrada em uma feira de antiguidades"
]

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Página inicial"""
    return templates.TemplateResponse("index.html", {"request": request})

async def tentar_gerar_com_modelo(modelo: str, prompt: str, client: httpx.AsyncClient):
    """Tenta gerar história com um modelo específico"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
    
    try:
        response = await client.post(
            f"{url}?key={GOOGLE_API_KEY}",
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.8,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 3000,
                    "stopSequences": []
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            }
        )
        return response, modelo
    except Exception as e:
        logger.error(f"Erro com {modelo}: {str(e)}")
        return None, modelo

@app.post("/gerar-historia")
async def gerar_historia():
    """Gerar história aleatória"""
    try:
        tema = random.choice(TEMAS)
        num_paragrafos = random.randint(3, 7)
        
        logger.info(f"Gerando história: {num_paragrafos} parágrafos sobre {tema}")
        
        prompt = f"""Você é um excelente escritor de histórias criativas e envolventes. 

Crie uma história COMPLETA E FINALIZADA sobre: {tema}

REGRAS OBRIGATÓRIAS:
1. A história DEVE ter EXATAMENTE {num_paragrafos} parágrafos
2. O ÚLTIMO parágrafo DEVE ser a conclusão e finalização da história
3. A história DEVE estar completa do início ao fim
4. NÃO deixe a história em aberto ou sem conclusão

Estrutura:
- Parágrafo 1: Apresentação do personagem e contexto inicial
- Parágrafos intermediários: Desenvolvimento do conflito/aventura
- Parágrafo {num_paragrafos} (FINAL): Resolução COMPLETA do conflito e conclusão satisfatória

Cada parágrafo deve ter 4-6 frases. Separe os parágrafos com linha em branco.

IMPORTANTE: Termine a história de forma definitiva no último parágrafo. O leitor deve sentir que a história teve um encerramento claro."""

        async with httpx.AsyncClient(timeout=45.0) as client:
            response = None
            modelo_usado = None
            
            for modelo in MODELOS:
                logger.info(f"Tentando modelo: {modelo}")
                response, modelo_usado = await tentar_gerar_com_modelo(modelo, prompt, client)
                
                if response and response.status_code == 200:
                    logger.info(f"✅ Sucesso com modelo: {modelo}")
                    break
                elif response and response.status_code == 429:
                    logger.warning(f"⚠️ Quota excedida para {modelo}, tentando próximo...")
                    continue
            
            if not response or response.status_code != 200:
                return {
                    "success": False,
                    "error": "Todos os modelos atingiram o limite de quota",
                    "details": "Por favor, tente novamente mais tarde."
                }
            
            data = response.json()
            
            if "candidates" not in data or len(data["candidates"]) == 0:
                return {
                    "success": False,
                    "error": "Conteúdo bloqueado por filtros de segurança",
                    "details": "Tente gerar novamente."
                }
            
            candidate = data["candidates"][0]
            finish_reason = candidate.get("finishReason", "UNKNOWN")
            
            if finish_reason == "SAFETY":
                return {
                    "success": False,
                    "error": "História bloqueada por filtros de segurança",
                    "details": "Tente outro tema."
                }
            
            historia = candidate["content"]["parts"][0]["text"]
            paragrafos = [p.strip() for p in historia.split('\n\n') if p.strip()]
            total_paragrafos = len(paragrafos)
            
            logger.info(f"História gerada com {total_paragrafos} parágrafos usando {modelo_usado}")
            
            return {
                "success": True,
                "historia": historia,
                "tema": tema,
                "paragrafos": total_paragrafos,
                "mostrar_continuar": total_paragrafos >= 7,
                "modelo_usado": modelo_usado
            }
                
    except httpx.TimeoutException:
        logger.error("Timeout na requisição")
        return {
            "success": False,
            "error": "Timeout na conexão",
            "details": "A API demorou muito para responder."
        }
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde"""
    return {"status": "ok", "message": "Servidor funcionando!"}

@app.get("/temas-disponiveis")
async def listar_temas():
    """Retorna a lista de temas disponíveis"""
    return {"temas": TEMAS, "total": len(TEMAS)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)