"""
Script de teste para verificar funcionamento do backtester
"""
import pandas as pd
from backtest_engine import load_data, Strategy, Backtester, resample_data

# Configurações
data_source = "data/"
ticker = "1000PEPEUSDT"
initial_balance = 100.0
leverage = 10
entry_pct = 1.0  # 100%

# Carregar dados
print("📊 Carregando dados...")
df = load_data(data_source, ticker_filter=ticker)
print(f"✓ Carregados {len(df)} candles")

# Resample para 15m (para teste rápido)
df_resampled = resample_data(df, '15min')
print(f"✓ Resampled para 15min: {len(df_resampled)} candles")

# Aplicar estratégia
print("\n🎯 Aplicando estratégia...")
strategy = Strategy(df_resampled)
df_strategy = strategy.ema_crossover_variation(fast_length=5, slow_length=200)

# Contar sinais
buy_signals = (df_strategy['signal'] == 1).sum()
sell_signals = (df_strategy['signal'] == -1).sum()
print(f"✓ Sinais de COMPRA: {buy_signals}")
print(f"✓ Sinais de VENDA: {sell_signals}")

# Executar backtest
print("\n🔄 Executando backtest...")
backtester = Backtester(
    df_strategy,
    initial_balance=initial_balance,
    leverage=leverage,
    entry_pct=entry_pct
)

trades = backtester.run(
    stop_loss_pct=0.05,  # 5%
    take_profit_pcts=[0.005, 0.01, 0.05],  # 0.5%, 1%, 5%
    tp_quantities=[0.3, 0.3, 0.4],  # 30%, 30%, 40%
    use_breakeven=False,
    use_breakgain=False
)

# Resultados
print("\n" + "="*60)
print("RESULTADOS DO BACKTEST")
print("="*60)

if trades.empty:
    print("❌ NENHUMA OPERAÇÃO EXECUTADA!")
else:
    print(f"✓ Total de trades: {len(trades)}")
    print(f"✓ Total de operações: {len(trades.groupby('entry_time'))}")

    # Agrupar por operação
    grouped = trades.groupby('entry_time')

    print("\n📋 DETALHES POR OPERAÇÃO:")
    print("-" * 60)

    for idx, (entry_time, group) in enumerate(grouped, 1):
        total_pnl = group['pnl'].sum()
        total_size = group['size'].sum()
        entry_price = group.iloc[0]['entry_price']

        print(f"\n{idx}. {group.iloc[0]['type'].upper()} @ {entry_price:.6f}")
        print(f"   Tamanho: {total_size:.4f} unidades")
        print(f"   PnL: ${total_pnl:.2f}")

        for _, trade in group.iterrows():
            print(f"   - {trade['reason']}: {trade['pnl']:.2f}$ @ {trade['exit_price']:.6f}")

    # Resumo final
    print("\n" + "="*60)
    print(f"BANCA INICIAL: ${initial_balance:.2f}")
    print(f"BANCA FINAL:   ${backtester.balance:.2f}")
    print(f"GANHO/PERDA:   ${backtester.balance - initial_balance:.2f}")
    print(f"RETORNO:       {((backtester.balance - initial_balance) / initial_balance * 100):.2f}%")
    print("="*60)

    # Verificar se há problema com tamanhos zero
    zero_size_trades = trades[trades['size'] == 0]
    if len(zero_size_trades) > 0:
        print(f"\n⚠️  AVISO: {len(zero_size_trades)} trades com tamanho ZERO detectados!")
        print("Isso pode indicar problema com alavancagem ou % entrada.")
