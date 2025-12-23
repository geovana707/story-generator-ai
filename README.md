GERADOR DE HISTÓRIAS COM INTELIGÊNCIA ARTIFICIAL
Trabalho desenvolvido para a disciplina de Programação Web
 Professor: Charleno
Participantes:
 Geovana Vitória Gomes Rodrigues,
 Thyago Lima Negreiro,
 Kauan Gomes Soares,
 Iasmyn Cristyne Castro Lima,
 Luis Gabriel Rodrigues de Sousa
Turma:
 2º ano B – Informática

 CONTEÚDO DO DOCUMENTO 
1. Introdução
Este documento tem como objetivo apresentar e explicar o funcionamento do projeto desenvolvido na disciplina de Programação Web. A documentação fornece uma visão geral do sistema, suas funcionalidades e as tecnologias utilizadas, permitindo a compreensão do projeto antes mesmo da análise do código-fonte.
2. Descrição do Projeto
O projeto consiste no desenvolvimento de um site que utiliza a Inteligência Artificial do Google (Gemini) para gerar histórias de forma automática. A cada solicitação do usuário, o sistema cria uma nova história baseada em um tema aleatório, proporcionando uma experiência interativa e dinâmica.

4. Tecnologias Utilizadas
Python
FastAPI
HTML, CSS e JavaScript
Jinja2
Google Gemini (gemini-2.5-flash)
Uvicorn

5. Estrutura do Projeto
O sistema é organizado de forma simples:
index.html: responsável pela interface visual e interação com o usuário.
main.py: contém a lógica do sistema, as rotas da aplicação e a integração com a IA do Google.
Templates: pasta utilizada para renderização das páginas HTML.



5. Funcionamento do Sistema
O usuário acessa o site e solicita a geração de uma história. O front-end envia uma requisição ao back-end, que seleciona um tema aleatório e cria um prompt estruturado. Esse prompt é enviado à IA do Google Gemini, que gera a história completa. Em seguida, o resultado é retornado ao front-end e exibido na tela.
6. Execução do Projeto
Por se tratar de um trabalho realizado em casa, o funcionamento do projeto pode ser verificado por meio da execução local do sistema. Após iniciar o servidor, o site pode ser acessado pelo navegador, permitindo testar a geração das histórias.
7. Considerações Finais
A documentação apresentada permite compreender o objetivo, a estrutura e o funcionamento do projeto de forma clara e objetiva, servindo como base para avaliação e entendimento do sistema.
