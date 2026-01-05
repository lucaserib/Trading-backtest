# 🚀 GUIA RÁPIDO DE USO

## ⚡ INICIAR APLICAÇÃO

```bash
streamlit run app.py
```

A aplicação abrirá automaticamente no navegador em `http://localhost:8501`

---

## 📋 PASSO A PASSO

### 1️⃣ **CONFIGURAR ESTRATÉGIA**
1. Clique no botão **"ESTRATÉGIA"**
2. Digite um nome para sua estratégia
3. Clique em **"SALVAR"**
4. Clique em **"< VOLTAR"**

✅ Estratégia ativa aparecerá em **verde** no topo

---

### 2️⃣ **CONFIGURAR PARÂMETROS**

#### **Básico:**
- **TEMPO GRÁFICO:** 5m, 15m, 1H, 4H, 1D
- **ATIVO:** Selecione da lista (ex: 1000PEPEUSDT)
- **VALOR BANCA:** Capital inicial (ex: 100$)
- **% ENTRADA:** Percentual da banca por operação (ex: 100%)
- **ALAVANCAGEM:** Multiplicador (ex: 10x)

#### **Take Profits:**
| TP  | ALVO % | POSIÇÃO % |
|-----|--------|-----------|
| TP1 | 0.5%   | 30%       |
| TP2 | 1.0%   | 30%       |
| TP3 | 5.0%   | 40%       |

#### **Proteções:**
- **STOPLOSS:** Percentual de perda máxima (ex: 5.0%)
- **BREAKEVEN:** ✅ Move SL para entrada após TP1
- **BREAKGAIN:** ✅ Move SL para TP anterior

#### **Período:**
- Use filtros rápidos: **7D, 30D, 60D, 120D, 180D, 365D**
- Ou selecione datas customizadas

---

### 3️⃣ **EXECUTAR BACKTEST**

1. Clique no botão verde **"START"**
2. Aguarde mensagem: ✅ **Backtest concluído!**
3. Visualize resultados:
   - **Gráfico interativo** com marcadores coloridos
   - **Métricas de desempenho**
   - **Logs detalhados** de cada operação

---

## 🎯 INTERPRETANDO RESULTADOS

### **GRÁFICO:**

#### **Marcadores:**
- **▲ Verde** = Entrada LONG
- **▼ Vermelho** = Entrada SHORT
- **◆ Laranja** = TP1 (primeiro take profit parcial)
- **◆ Verde Claro** = TP2 (segundo take profit parcial)
- **★ Verde Forte** = TP3 (take profit final)
- **✖ Vermelho** = Stop Loss

#### **Linhas Pontilhadas:**
- **Verde** = Operação lucrativa
- **Vermelho** = Operação com prejuízo

#### **Hover (Passar Mouse):**
```
ENTRADA LONG
Preço: 0.01220$
Tamanho: 81944.38 un
PnL Total: +24.50$
Tempo: 2025-08-13 01:00:00
```

```
TP1
Tipo: Take Profit 1 (Partial)
Preço: 0.01214$
Tamanho: 24583.31 un
PnL: +1.50$
Tempo: 2025-08-13 02:30:00
```

---

### **MÉTRICAS DE DESEMPENHO:**

```
BANCA FINAL: 124.50$
GANHO/PREJUIZO: +24.50$ (24.5%)
WINRATE: 75%
TOTAL OP: 20
OP LUCRO: 15
OP PREJUIZO: 5
```

---

### **LOGS DE OPERAÇÕES:**

#### **Cabeçalho:**
```
1° OPERAÇÃO: LONG                    2025-08-13 01:00:00
```

#### **Métricas:**
- 💰 **Entrada:** 0.01220$
- 🎯 **Saída Final:** 0.01159$
- 📊 **Resultado:** +24.50$ (+24.5%)
- 📏 **Tamanho Total:** 81944.3762 un
- 📈 **Máx Floating:** +2.15%

#### **Status TPs:**
- **TP1:** ✅ (acionado)
- **TP2:** ✅ (acionado)
- **TP3:** ✅ (acionado)

#### **Eventos de Saída:**
```
1. TP1 (Parcial)
   Preço: 0.01214$ | PnL: +1.50$ 🟢

2. TP2 (Parcial)
   Preço: 0.01208$ | PnL: +3.00$ 🟢

3. TP3 (Final)
   Preço: 0.01159$ | PnL: +20.00$ 🟢
```

---

## ⚙️ FUNCIONALIDADES AVANÇADAS

### **ZOOM NO GRÁFICO:**
- Use a ferramenta de **lupa** no canto superior direito
- Arraste para selecionar área
- ✅ Marcadores permanecerão visíveis durante zoom

### **BREAKEVEN:**
- Ativado após **TP1**
- Move Stop Loss para **preço de entrada**
- Garante que operação não vire prejuízo

### **BREAKGAIN:**
- Ativado após cada TP
- Move Stop Loss para **TP anterior**
- Protege lucros já realizados

### **FLOATING MÁXIMO:**
- Mostra o **maior lucro** atingido durante a operação
- Útil para otimizar níveis de TP

---

## ⚠️ GERENCIAMENTO DE RISCO

### **Recomendações:**

#### **Conservador:**
```
VALOR BANCA: $100
% ENTRADA: 5-10%
ALAVANCAGEM: 2-3x
```

#### **Moderado:**
```
VALOR BANCA: $100
% ENTRADA: 20-30%
ALAVANCAGEM: 5-10x
```

#### **Agressivo:**
```
VALOR BANCA: $100
% ENTRADA: 50-100%
ALAVANCAGEM: 10-20x
```

⚠️ **ATENÇÃO:** Alavancagem alta + % Entrada alta = **RISCO EXTREMO**

---

## 🐛 SOLUÇÃO DE PROBLEMAS

### **Problema:** Nenhuma operação executada
**Solução:**
- Verifique se há sinais no período selecionado
- Experimente período maior (ex: 180D ou 365D)
- Verifique se estratégia foi salva corretamente

### **Problema:** Gráfico não mostra marcadores
**Solução:**
- Clique em **START** para executar backtest
- Verifique se estratégia está **ativa** (verde no topo)

### **Problema:** Erro de alavancagem
**Solução:**
- Alavancagem mínima é **1x**
- Use valores entre 1 e 125

---

## 📊 EXEMPLO PRÁTICO

```
1. Configure:
   - ATIVO: 1000PEPEUSDT
   - BANCA: 100$
   - % ENTRADA: 100%
   - ALAVANCAGEM: 10x
   - PERÍODO: 30D

2. Execute START

3. Analise:
   - Gráfico com todas as operações
   - Winrate e total de operações
   - Logs detalhados de cada trade
   - Floating máximo atingido

4. Otimize:
   - Ajuste TPs baseado no floating máximo
   - Ative BREAKEVEN para proteger capital
   - Teste diferentes períodos
```

---

## 🎓 DICAS PROFISSIONAIS

1. **Teste primeiro com BANCA PEQUENA** ($10-$50)
2. **Use % ENTRADA conservador** (5-20%)
3. **Ative BREAKEVEN** para proteger capital
4. **Analise FLOATING MÁXIMO** para otimizar TPs
5. **Teste diferentes PERÍODOS** para validar estratégia
6. **Compare WINRATE** entre diferentes configurações

---

## 📁 ARQUIVOS DO PROJETO

```
/Backtest-trading/
├── app.py                           # Interface principal
├── backtest_engine.py               # Motor de backtesting
├── strategy_manager.py              # Gerenciador de estratégias
├── styles.css                       # Estilos customizados
├── data/                            # Dados OHLC (CSV)
├── saved_strategies.json            # Estratégias salvas
├── CORRECOES_FINAIS_COMPLETAS.md   # Documentação técnica
├── RESUMO_CORRECOES.md             # Resumo das correções
└── GUIA_RAPIDO.md                  # Este arquivo
```

---

**✨ BOA SORTE COM SEUS BACKTESTS! ✨**

Para suporte técnico, consulte:
- [CORRECOES_FINAIS_COMPLETAS.md](CORRECOES_FINAIS_COMPLETAS.md) - Documentação detalhada
- [RESUMO_CORRECOES.md](RESUMO_CORRECOES.md) - Resumo das correções aplicadas
