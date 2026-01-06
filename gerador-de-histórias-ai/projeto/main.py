from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Gerador de Histórias Aleatórias")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

GOOGLE_API_KEY = "AIzaSyDAXss-0lpnWq8UR_I-uL8yWJKUZAgmqqw"

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

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

@app.post("/gerar-historia")
async def gerar_historia():
    """Gerar história aleatória usando APENAS gemini-2.5-flash"""
    try:
        tema = random.choice(TEMAS)
        num_paragrafos = random.randint(3, 7)
        
        logger.info(f"🎲 Gerando história: {num_paragrafos} parágrafos sobre '{tema}'")
        
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
            response = await client.post(
                f"{GEMINI_API_URL}?key={GOOGLE_API_KEY}",
                json={
                    "contents": [{
                        "parts": [{
                            "text": prompt
                        }]
                    }],
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
            
            logger.info(f"📡 Status da API: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if "candidates" not in data or len(data["candidates"]) == 0:
                    logger.error("❌ Resposta sem candidatos - possível bloqueio de segurança")
                    return {
                        "success": False,
                        "error": "Conteúdo bloqueado por filtros de segurança",
                        "details": "Tente gerar novamente."
                    }
                
                candidate = data["candidates"][0]
                finish_reason = candidate.get("finishReason", "UNKNOWN")
                
                logger.info(f"✅ Finish reason: {finish_reason}")
                
                if finish_reason == "SAFETY":
                    return {
                        "success": False,
                        "error": "História bloqueada por filtros de segurança",
                        "details": "Tente outro tema clicando novamente."
                    }
                
                historia = candidate["content"]["parts"][0]["text"]
                
                paragrafos = [p.strip() for p in historia.split('\n\n') if p.strip()]
                total_paragrafos = len(paragrafos)
                
                logger.info(f"✨ História gerada com sucesso! {total_paragrafos} parágrafos, {len(historia)} caracteres")
                
                return {
                    "success": True,
                    "historia": historia,
                    "tema": tema,
                    "paragrafos": total_paragrafos,
                    "mostrar_continuar": total_paragrafos >= 7
                }
                
            elif response.status_code == 429:
                logger.error("⚠️ Limite de quota atingido!")
                return {
                    "success": False,
                    "error": "Limite de requisições atingido",
                    "details": "Você atingiu o limite diário da API gratuita. Tente novamente mais tarde (após 21h horário de Brasília) ou amanhã."
                }
            else:
                logger.error(f"❌ Erro na API: {response.status_code}")
                return {
                    "success": False,
                    "error": f"Erro na API: {response.status_code}",
                    "details": response.text
                }
                
    except httpx.TimeoutException:
        logger.error("⏱️ Timeout na requisição para API")
        return {
            "success": False,
            "error": "Tempo esgotado",
            "details": "A API demorou muito para responder. Tente novamente."
        }
    except Exception as e:
        logger.error(f"💥 Erro inesperado: {str(e)}")
        return {
            "success": False,
            "error": "Erro inesperado no servidor",
            "details": str(e)
        }

@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde"""
    return {"status": "ok", "message": "Servidor funcionando!", "modelo": "gemini-2.5-flash"}

@app.get("/temas-disponiveis")
async def listar_temas():
    """Retorna a lista de temas disponíveis"""
    return {"temas": TEMAS, "total": len(TEMAS)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)




