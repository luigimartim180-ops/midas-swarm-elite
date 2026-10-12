# Análise da conversa original (Qwen + Kimi)

Duas conversas foram analisadas: a do Qwen (`chat.qwen.ai/s/fd7f4759-...`) e a do Kimi
(`kimi.ai/share/1a12d802-...`). Ambas tratam do mesmo objetivo: reabilitação auditiva
de um idoso de 90 anos, com "swarm de 5 agentes" e "resultado rápido real".

## O que foi recuperado

- **Qwen:** 6 mensagens (3 do usuário, 3 do assistente). Título "Reabilitação Auditiva
  Fase 2". Contém duas páginas HTML funcionais (Fase 2 com ruído embarcado; depois com
  ruído "de TV" e texto em pt-BR) e o protocolo SWARM v1 com 5 agentes.
- **Kimi:** a conversa que originou o pedido; construiu um widget de teste auditivo com
  Web Audio + voz sintética, e o protocolo SWARM v2 com pesquisa em papers.

O acesso funcionou assim: as páginas de compartilhamento são SPAs. A do Qwen responde no
endpoint `GET https://chat.qwen.ai/api/v2/chats/share/<id>` (JSON com todo o histórico).
A do Kimi foi lida pelo navegador (o conteúdo é renderizado no cliente).

## O que estava bom

- A direção clínica estava certa: treino auditivo adaptativo, fala em ruído, gap
  detection, participação da família.
- O código HTML era funcional e acessível (botões grandes, pt-BR).
- A v2 já citava evidência real (Humes, LACE, tDCS, microfone remoto).

## O que não era de elite (e foi corrigido)

1. **Validação fictícia.** Havia um "checklist de validação antes do uso clínico" que o
   modelo não executou. Corrigido: nada afirma ter sido validado; o que é orientativo
   está rotulado como orientativo.
2. **Agentes sem contrato.** "5 agentes" eram personas, sem gatilho, entrada, saída ou
   critério de parada. Corrigido em `docs/SWARM_V3.md` (tabela de contratos).
3. **Medição sem norma.** O teste do navegador não é calibrado. Corrigido: o resultado é
   expresso como estimativa de SNR loss (mesma escala do QuickSIN, com faixas normativas)
   e gap threshold, sempre com aviso de que não é exame clínico.
4. **Ordem errada das alavancas.** Treino e exercício apareciam juntos; o ganho mais
   rápido e barato (transmitir o áudio da TV para o aparelho) não era o passo número 1.
   Corrigido: A1 roda primeiro.
5. **Promessa de exercício como reabilitação auditiva.** A relação exercício↔audição é
   de coorte, não causal. Corrigido: exercício entra como saúde geral, com grau C.
6. **Sem testes.** Corrigido: 16 testes (motor, entrada inválida, resolução de citações,
   paridade Python↔JS).

## Sobre o pedido de "pensar em chinês"

Idioma do raciocínio interno não é uma técnica que melhore o resultado. O que melhora é
contexto, restrição e verificação — que é o que este repositório implementa. A resposta
sai em português, como pedido.

## Sobre "menos de 1% da elite mundial"

Isso é marketing. Engenharia de agentes de alto nível, de forma concreta, é: orquestração
determinística, contratos explícitos por agente, evidência rastreável, evals contínuas,
tratamento de erro explícito e ausência de decisão clínica no LLM. É exatamente o que
está implementado aqui, e é verificável rodando `make test`.
