# Reabilitação Auditiva — SWARM v3

Sistema de reabilitação auditiva para um idoso de 90 anos, reconstruído a partir das
conversas originais (Qwen + Kimi) para um padrão auditável.

O que muda em relação ao material original:

- **Motor determinístico.** A decisão clínica vive em `swarm/engine.py`, função pura do
  perfil. O LLM não decide nada; no máximo narra o JSON.
- **Evidência rastreável.** Cada recomendação aponta para uma chave de `swarm/evidence.py`
  com citação, URL e grau (A–D).
- **Cinco agentes com contrato.** Gatilho, entrada, saída e critério de parada explícitos
  (`docs/SWARM_V3.md`).
- **App funcional em pt-BR.** Treino de fala em ruído e resolução temporal com áudio real
  (Web Audio + voz pt-BR), e geração do protocolo offline no próprio aparelho.
- **Testes.** 16 casos: motor, entrada inválida, resolução de citações e paridade Python↔JS.

## Estrutura

```
swarm/            motor determinístico (Python)
  evidence.py     registro de evidências (claim, efeito, citação, URL, grau)
  schema.py       perfil validado (campos obrigatórios e opcionais)
  engine.py       os 5 agentes + plano de 8 semanas + perguntas de calibragem
app/
  index.html      estação de treino e triagem (pt-BR, áudio real)
  protocol.js     espelho do motor para rodar offline no navegador
tests/            16 testes (pytest) incluindo paridade Python↔JS
docs/             análise, arquitetura, evidências, protocolo, segurança
```

## Como rodar

### App de treino

```bash
make serve        # http://localhost:12000
```

Abra, calibre o volume, faça os dois testes e gere o protocolo. Para pré-visualizar sem
completar os testes: `http://localhost:12000/?demo=1` (resultados) ou `?demo=2`
(resultados + formulário de protocolo).

### Protocolo em Python

```bash
make demo
```

ou:

```bash
python -m swarm.cli examples/profile.json
```

## Testes

```bash
make test
```

## Fluxo do motor

```
perfil validado -> A1 sinal -> A2 dosagem -> A3 transferência -> A4 família -> A5 segurança
                                |
                                v
                   protocolo JSON + referências + plano de 8 semanas
```

A ordem não é estética: A1 (sinal) entrega ganho no dia 1; A2–A4 consolidam em 2–8 semanas.

## Limites, sem marketing

- Perda coclear não se reverte (`presbycusis_irreversible`).
- O teste do app é orientativo, não clínico.
- tDCS e protocolos experimentais não entram no plano domiciliar.
- Red flags escalam para avaliação médica antes de qualquer treino.

Ver `docs/SAFETY.md`.
