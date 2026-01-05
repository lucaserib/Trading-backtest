import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from backtest_engine import load_data, Strategy, Backtester, resample_data
from strategy_manager import save_strategy, load_strategies, get_strategy, list_strategy_names
import os
import glob

# --- Page Config ---
st.set_page_config(page_title="Backtest Pro", layout="wide", initial_sidebar_state="collapsed")

# --- Load CSS ---
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

if os.path.exists("styles.css"):
    local_css("styles.css")

# --- Session State ---
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'
if 'strategy_code' not in st.session_state:
    st.session_state.strategy_code = """//@version=5
indicator("Cruzamento EMA + Variação %", overlay=true)
// ... (Código padrão)
"""
if 'active_strategy' not in st.session_state:
    st.session_state.active_strategy = "Nenhuma"

def navigate_to(page):
    st.session_state.page = page

data_source = "data/"

# ==============================================================================
# SCREEN 1: STRATEGIES (Editor)
# ==============================================================================
if st.session_state.page == 'strategies':
    # Custom Header for Strategy Screen
    st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 20px;">
            <h2 style='margin: 0;'>GERENCIAR ESTRATÉGIAS</h2>
        </div>
    """, unsafe_allow_html=True)

    if st.button("< VOLTAR", key='btn_back'):
        navigate_to('dashboard')
        st.rerun()

    # Inicializar estado de edição
    if 'editing_strategy' not in st.session_state:
        st.session_state.editing_strategy = False
    if 'editing_strategy_name' not in st.session_state:
        st.session_state.editing_strategy_name = ""

    # Botão de Nova Estratégia no topo - SEMPRE VISÍVEL
    col_nova_btn, col_spacer = st.columns([1, 3])
    with col_nova_btn:
        if st.button("➕ NOVA ESTRATÉGIA", type="primary", use_container_width=True, key="btn_nova_top"):
            st.session_state.editing_strategy = True
            st.session_state.editing_strategy_name = ""
            st.session_state.strategy_code = """//@version=5
indicator("Cruzamento EMA + Variação %", overlay=true)
// ... (Código padrão)
"""
            st.rerun()

    st.markdown("---")

    col_list, col_editor = st.columns([1, 1])

    # COLUNA ESQUERDA: Lista de Estratégias Salvas
    with col_list:
        st.markdown("### 📋 ESTRATÉGIAS SALVAS")

        saved_strategies = list_strategy_names()

        if saved_strategies:
            for strategy_name in saved_strategies:
                strategy_data = get_strategy(strategy_name)
                is_active = st.session_state.get('active_strategy', 'Nenhuma') == strategy_name

                # Card para cada estratégia
                card_color = "#00e676" if is_active else "#2b2b2b"
                status_text = "✅ ATIVA" if is_active else ""

                st.markdown(f"""
                <div style="background:{card_color if is_active else '#2b2b2b'};
                     border:2px solid {card_color};
                     padding:15px; border-radius:6px; margin-bottom:10px;">
                    <strong style="font-size:16px;">{strategy_name}</strong>
                    <span style="color:#00e676; float:right;">{status_text}</span>
                </div>
                """, unsafe_allow_html=True)

                # Botões de ação
                col_activate, col_edit, col_delete = st.columns(3)
                with col_activate:
                    if not is_active:
                        if st.button("ATIVAR", key=f"activate_{strategy_name}"):
                            st.session_state.active_strategy = strategy_name
                            st.success(f"✅ Estratégia '{strategy_name}' ativada!")
                            st.rerun()
                with col_edit:
                    if st.button("EDITAR", key=f"edit_{strategy_name}"):
                        st.session_state.editing_strategy = True
                        st.session_state.editing_strategy_name = strategy_name
                        st.session_state.strategy_code = strategy_data['code']
                        st.rerun()
                with col_delete:
                    if st.button("❌", key=f"delete_{strategy_name}", help="Excluir estratégia"):
                        from strategy_manager import delete_strategy
                        delete_strategy(strategy_name)
                        if st.session_state.get('active_strategy') == strategy_name:
                            st.session_state.active_strategy = "Nenhuma"
                        st.success(f"🗑️ Estratégia '{strategy_name}' excluída!")
                        st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.warning("📝 Nenhuma estratégia salva ainda.")
            st.markdown("""
            <div style='background:#1a1a1a; padding:20px; border-radius:8px; border:2px dashed #00e676; text-align:center;'>
                <p style='font-size:16px; color:#00e676; margin:0;'>
                    👆 Clique no botão <strong>"➕ NOVA ESTRATÉGIA"</strong> acima para começar!
                </p>
            </div>
            """, unsafe_allow_html=True)

    # COLUNA DIREITA: Editor
    with col_editor:
        if st.session_state.editing_strategy:
            st.markdown("### ✏️ EDITOR")

            is_new = st.session_state.editing_strategy_name == ""
            strategy_name = st.text_input(
                "NOME DA ESTRATÉGIA *",
                value=st.session_state.editing_strategy_name,
                placeholder="Digite o nome da estratégia",
                key="strategy_name_edit"
            )

            st.markdown("**ENTRAR LONG > (SINAL COMPRA)**")
            st.markdown("**ENTRAR SHORT > (SINAL VENDA)**")

            # Code Editor
            strategy_code = st.text_area(
                "CÓDIGO DA ESTRATÉGIA",
                value=st.session_state.strategy_code,
                height=300,
                key="code_editor"
            )

            st.markdown("---")

            # Botões de ação
            col_save, col_cancel = st.columns(2)
            with col_save:
                if st.button("💾 SALVAR", type="primary", use_container_width=True):
                    if strategy_name.strip() == "":
                        st.error("❌ Digite um nome para a estratégia!")
                    else:
                        save_strategy(strategy_name, strategy_code)
                        st.session_state.active_strategy = strategy_name
                        st.session_state.editing_strategy = False
                        st.success(f"✅ Estratégia '{strategy_name}' salva com sucesso!")
                        st.rerun()
            with col_cancel:
                if st.button("❌ CANCELAR", use_container_width=True):
                    st.session_state.editing_strategy = False
                    st.rerun()
        else:
            st.markdown("### 📖 INFORMAÇÕES")
            st.info("""
            **Como usar:**
            1. Crie uma **NOVA ESTRATÉGIA** ou edite uma existente
            2. **ATIVE** a estratégia que deseja testar
            3. Volte ao **DASHBOARD** para executar o backtest

            **Dica:** Apenas uma estratégia pode estar ativa por vez.
            """)


# ==============================================================================
# SCREEN 2: DASHBOARD (Main)
# ==============================================================================
elif st.session_state.page == 'dashboard':
    
    # --- Top Bar ---
    c_header_title, c_header_filters = st.columns([1, 2])
    with c_header_title:
        st.markdown("<h1 style='margin:0;'>GRÁFICO</h1>", unsafe_allow_html=True)
    with c_header_filters:
         # Active Strategy Display
         active_strat = st.session_state.get('active_strategy', 'Nenhuma')
         color_strat = '#00e676' if active_strat != 'Nenhuma' else '#ff5252'
         st.markdown(f"<div style='text-align: right; color: #888; font-size: 18px;'>Estratégia Ativa: <span style='color: {color_strat}; font-weight: bold;'>{active_strat}</span></div>", unsafe_allow_html=True)

    # --- Main Split ---
    col_chart_area, col_right_sidebar = st.columns([3, 1])

    # --- Right Sidebar (Params) ---
    with col_right_sidebar:
        if st.button("PROXIMO > PARAMETROS"):
            pass 
        
        st.markdown("### PARAMETROS")
        
        # Timeframe
        timeframe = st.selectbox("TEMPO GRÁFICO", ["5m", "15m", "1H", "4H", "1D"], index=0)
        
        # Assets (Dynamic Ticker Detection)
        assets = []
        if os.path.exists(data_source):
             files = sorted([f for f in os.listdir(data_source) if f.endswith(".csv")])
             # Extract simple ticker from filename (assuming format 'TICKER-...')
             # Example: '1000PEPEUSDT-5m-...' -> '1000PEPEUSDT'
             tickers = set()
             for f in files:
                 try:
                     ticker = f.split('-')[0]
                     tickers.add(ticker)
                 except:
                     tickers.add(f)
             assets = sorted(list(tickers))
        
        if not assets:
            st.error("Sem CSVs na pasta data/")
            asset = None
        else:
            asset = st.selectbox("ATIVO", assets)

        # Bank
        initial_balance = st.number_input("VALOR BANCA", value=100.0, min_value=1.0, step=10.0)

        # Entry %
        entry_pct = st.number_input("% ENTRADA", value=100.0, min_value=1.0, max_value=100.0, step=1.0)

        # Leverage
        leverage = st.number_input("ALAVANCAGEM", value=10, min_value=1, max_value=125, step=1)
        
        # Strategy Select
        st.button("ESTRATÉGIA", on_click=lambda: navigate_to('strategies'))
        
        st.markdown("---")
        
        # Take Profit Table
        st.markdown("#### TAKE PROFIT")
        c_tp_head1, c_tp_head2 = st.columns(2)
        with c_tp_head1: st.markdown("<small>ALVO</small>", unsafe_allow_html=True)
        with c_tp_head2: st.markdown("<small>POSIÇÃO</small>", unsafe_allow_html=True)
        
        c_tp1_a, c_tp1_p = st.columns(2)
        with c_tp1_a: tp1_t = st.text_input("TP1 (%)", value="0.5%", key="tp1t")
        with c_tp1_p: tp1_q = st.text_input("TP1Q (%)", value="30%", key="tp1q")
        
        c_tp2_a, c_tp2_p = st.columns(2)
        with c_tp2_a: tp2_t = st.text_input("TP2 (%)", value="1.0%", key="tp2t")
        with c_tp2_p: tp2_q = st.text_input("TP2Q (%)", value="30%", key="tp2q")
        
        c_tp3_a, c_tp3_p = st.columns(2)
        with c_tp3_a: tp3_t = st.text_input("TP3 (%)", value="5.0%", key="tp3t")
        with c_tp3_p: tp3_q = st.text_input("TP3Q (%)", value="40%", key="tp3q")
        
        # Technical Params
        st.markdown("#### PARAMETROS TÉCNICOS")
        c_sl_label, c_sl_input = st.columns([1, 1])
        with c_sl_label: st.markdown("**STOPLOSS**", unsafe_allow_html=True)
        with c_sl_input: sl_val = st.text_input("sl", value="5.0%", label_visibility="collapsed")

        # Breakeven
        c_be_label, c_be_input = st.columns([1, 1])
        with c_be_label: st.markdown("**BREAKEVEN**", unsafe_allow_html=True)
        with c_be_input:
            use_breakeven = st.checkbox("ATIVADO", value=False, key="breakeven_toggle")

        # Breakgain
        c_bg_label, c_bg_input = st.columns([1, 1])
        with c_bg_label: st.markdown("**BREAKGAIN**", unsafe_allow_html=True)
        with c_bg_input:
            use_breakgain = st.checkbox("ATIVADO", value=False, key="breakgain_toggle")

        # Taxa de Corretagem
        c_comm_label, c_comm_input = st.columns([1, 1])
        with c_comm_label: st.markdown("**TAXA CORRETAGEM**", unsafe_allow_html=True)
        with c_comm_input:
            commission_val = st.text_input("commission", value="0.1%", label_visibility="collapsed", help="Taxa de corretagem por operação (entrada + saída)")

        st.markdown("---")
        # Date Filter
        st.markdown("#### PERÍODO")

        # Load min/max dates if asset selected (Scan ALL files for this asset)
        min_date, max_date = None, None
        df_full_range = pd.DataFrame()

        if asset:
            try:
                # Load LIGHTWEIGHT version to get dates (or just cached)
                # We use our new load_data which merges all files
                df_full_range = load_data(data_source, ticker_filter=asset)
                if not df_full_range.empty:
                    min_date = df_full_range.index.min().date()
                    max_date = df_full_range.index.max().date()
            except Exception as e:
                st.error(f"Erro ao ler datas: {e}")

        # Filtros rápidos de período
        if min_date and max_date:
            st.markdown("<small>FILTROS RÁPIDOS:</small>", unsafe_allow_html=True)
            period_cols = st.columns(6)
            from datetime import timedelta

            quick_periods = {
                '7D': 7,
                '30D': 30,
                '60D': 60,
                '120D': 120,
                '180D': 180,
                '365D': 365
            }

            selected_period = None
            for idx, (label, days) in enumerate(quick_periods.items()):
                with period_cols[idx]:
                    if st.button(label, key=f"period_{label}"):
                        selected_period = days

            if selected_period:
                from datetime import datetime
                end_date = max_date
                start_date = end_date - timedelta(days=selected_period)
                date_range = (max(start_date, min_date), end_date)
            else:
                date_range = st.date_input("Selecionar:", value=(min_date, max_date), min_value=min_date, max_value=max_date)
        else:
            st.warning("Gere arquivos CSV para o ativo.")
            date_range = None

        # Start
        start_btn = st.button("START")

        # Parse inputs
        try:
            sl_pct = float(sl_val.strip('%')) / 100
            tp_targets = [float(tp1_t.strip('%'))/100, float(tp2_t.strip('%'))/100, float(tp3_t.strip('%'))/100]
            tp_qtys = [float(tp1_q.strip('%'))/100, float(tp2_q.strip('%'))/100, float(tp3_q.strip('%'))/100]
            commission_rate = float(commission_val.strip('%')) / 100
        except:
            sl_pct = 0.05
            tp_targets = [0.01]
            tp_qtys = [1.0]
            commission_rate = 0.001  # 0.1% padrão

    # --- Chart Area (Left) ---
    with col_chart_area:
        
        if asset and date_range:
            # We already loaded df_full_range to check dates, optimize by reusing if small, 
            # but safer to reload or use it if already in memory.
            # df_full_range is available from above context.
            df = df_full_range 
            
            # Filter Date
            if isinstance(date_range, tuple) and len(date_range) == 2:
                start_d, end_d = date_range
                df = df.loc[str(start_d):str(end_d)]

            if not df.empty:
                # Resample
                df_resampled = resample_data(df, timeframe)
                
                # Run Strategy
                strategy = Strategy(df_resampled)
                df_resampled = strategy.ema_crossover_variation(fast_length=5, slow_length=200)

                # View Slice - Mostrar TODOS os candles do período selecionado
                df_view = df_resampled

                # Informar quantidade de candles sendo exibida
                if len(df_view) > 5000:
                    st.info(f"📊 Exibindo {len(df_view):,} candles. Para melhor performance, considere reduzir o período ou usar timeframe maior.")
                elif len(df_view) > 2000:
                    st.info(f"📊 Exibindo {len(df_view):,} candles no gráfico.")
                else:
                    st.success(f"📊 Carregados {len(df_view):,} candles.")
                
                # Backtest
                trades = pd.DataFrame()
                backtester = None
                
                # Logic: We ONLY run backtest if START is clicked AND Strategy is Active
                if start_btn:
                    if st.session_state.active_strategy != "Nenhuma":
                        # Validações antes de executar
                        if leverage < 1:
                            st.error("❌ ERRO: Alavancagem deve ser pelo menos 1x!")
                        elif entry_pct < 1:
                            st.error("❌ ERRO: % Entrada deve ser pelo menos 1%!")
                        elif initial_balance < 1:
                            st.error("❌ ERRO: Valor da banca deve ser pelo menos $1!")
                        else:
                            with st.spinner('🔄 Executando backtest...'):
                                backtester = Backtester(
                                    df_resampled,
                                    initial_balance=initial_balance,
                                    leverage=leverage,
                                    entry_pct=entry_pct/100,  # Converter de % para decimal
                                    commission_rate=commission_rate  # Taxa de corretagem
                                )
                                trades = backtester.run(
                                    stop_loss_pct=sl_pct,
                                    take_profit_pcts=tp_targets,
                                    tp_quantities=tp_qtys,
                                    use_breakeven=use_breakeven,
                                    use_breakgain=use_breakgain
                                )

                                # Debug info
                                if trades.empty:
                                    st.warning("⚠️ Nenhuma operação foi executada. Verifique se há sinais de entrada no período selecionado.")
                                else:
                                    st.success(f"✅ Backtest concluído! {len(trades.groupby('entry_time'))} operações executadas.")
                    else:
                        st.error("ERRO: Nenhuma estratégia salva! Vá em 'ESTRATÉGIA' e clique em SALVAR.")

                # --- Chart ---
                fig = go.Figure()
                
                # Candles
                fig.add_trace(go.Candlestick(
                    x=df_view.index, open=df_view['open'], high=df_view['high'], low=df_view['low'], close=df_view['close'],
                    increasing_line_color='#00e676', decreasing_line_color='#ff5252', name='Price'
                ))
                
                # EMAs
                fig.add_trace(go.Scatter(x=df_view.index, y=df_view['ema_fast'], line=dict(color='blue', width=1), name='EMA 5'))
                fig.add_trace(go.Scatter(x=df_view.index, y=df_view['ema_slow'], line=dict(color='orange', width=2), name='EMA 200'))
                
                # Variation Labels (Annotations)
                labels_view = df_view[df_view['var_label'].notnull()]
                if not labels_view.empty:
                    for idx, row in labels_view.iterrows():
                        y_pos = row['high'] * 1.001 if "Máx" in str(row['var_label']) else row['low'] * 0.999
                        color_txt = "#00e676" if "Máx" in str(row['var_label']) else "#ff5252"
                        fig.add_annotation(x=idx, y=y_pos, text=row['var_label'], showarrow=False, font=dict(color=color_txt, size=10))

                # Trade Markers - Versão LIMPA E MODERNA
                if not trades.empty:
                    # Agrupar por operação para desenhar linhas conectando entrada→saída
                    grouped_ops = trades.groupby('entry_time')

                    for entry_t, group in grouped_ops:
                        first_trade = group.iloc[0]
                        op_type = first_trade['type']
                        entry_price = first_trade['entry_price']

                        # Cor da operação
                        op_color = 'rgba(0, 230, 118, 0.3)' if op_type == 'long' else 'rgba(255, 82, 82, 0.3)'
                        marker_color = '#00e676' if op_type == 'long' else '#ff5252'

                        # Calcular tamanho total da operação
                        total_position_size = group['size'].sum()
                        total_operation_pnl = group['pnl'].sum()

                        # ENTRADA - Triângulo grande com informações completas
                        fig.add_trace(go.Scatter(
                            x=[entry_t],
                            y=[entry_price],
                            mode='markers',
                            marker=dict(
                                symbol='triangle-up' if op_type == 'long' else 'triangle-down',
                                color=marker_color,
                                size=16,
                                line=dict(color='white', width=2)
                            ),
                            name=f'Entrada {op_type.upper()}',
                            showlegend=False,
                            hovertemplate=(
                                f'<b>ENTRADA {op_type.upper()}</b><br>'
                                f'Preço: {entry_price:.5f}$<br>'
                                f'Tamanho: {total_position_size:.2f} un<br>'
                                f'PnL Total: <b>{total_operation_pnl:+.2f}$</b><br>'
                                f'Tempo: {entry_t}'
                                '<extra></extra>'
                            )
                        ))

                        # SAÍDAS - Para cada evento
                        for idx, trade in group.iterrows():
                            reason = trade['reason']
                            exit_time = trade['exit_time']
                            exit_price = trade['exit_price']
                            pnl = trade['pnl']
                            trade_size = trade['size']

                            # Determinar cor e símbolo
                            if 'Stop Loss' in reason:
                                exit_color = '#ff5252'
                                exit_symbol = 'x'
                                exit_size = 14
                                exit_name = 'STOP LOSS'
                            elif 'Take Profit 1' in reason:
                                exit_color = '#ffa726'  # Laranja
                                exit_symbol = 'diamond'
                                exit_size = 10
                                exit_name = 'TP1'
                            elif 'Take Profit 2' in reason:
                                exit_color = '#66bb6a'  # Verde claro
                                exit_symbol = 'diamond'
                                exit_size = 10
                                exit_name = 'TP2'
                            elif 'Take Profit 3' in reason:
                                exit_color = '#00e676'  # Verde forte
                                exit_symbol = 'star'
                                exit_size = 14
                                exit_name = 'TP3'
                            else:
                                exit_color = '#ffffff'
                                exit_symbol = 'circle'
                                exit_size = 8
                                exit_name = 'SAÍDA'

                            # Marcador de saída com hover detalhado
                            fig.add_trace(go.Scatter(
                                x=[exit_time],
                                y=[exit_price],
                                mode='markers',
                                marker=dict(
                                    symbol=exit_symbol,
                                    color=exit_color,
                                    size=exit_size,
                                    line=dict(color='white', width=1)
                                ),
                                name=exit_name,
                                showlegend=False,
                                hovertemplate=(
                                    f'<b>{exit_name}</b><br>'
                                    f'Tipo: {reason}<br>'
                                    f'Preço: {exit_price:.5f}$<br>'
                                    f'Tamanho: {trade_size:.2f} un<br>'
                                    f'PnL: <b>{pnl:+.2f}$</b><br>'
                                    f'Tempo: {exit_time}'
                                    '<extra></extra>'
                                )
                            ))

                        # Linha conectando ENTRADA → ÚLTIMA SAÍDA
                        last_trade = group.iloc[-1]
                        last_exit_time = last_trade['exit_time']
                        last_exit_price = last_trade['exit_price']
                        total_pnl = group['pnl'].sum()

                        line_color = 'rgba(0, 230, 118, 0.4)' if total_pnl > 0 else 'rgba(255, 82, 82, 0.4)'

                        fig.add_trace(go.Scatter(
                            x=[entry_t, last_exit_time],
                            y=[entry_price, last_exit_price],
                            mode='lines',
                            line=dict(color=line_color, width=1, dash='dot'),
                            showlegend=False,
                            hoverinfo='skip'
                        ))

                fig.update_layout(
                    template='plotly_dark',
                    paper_bgcolor='#0a0a0a',
                    plot_bgcolor='#1a1a1a',
                    margin=dict(l=10, r=60, t=40, b=10),
                    height=700,  # Aumentado de 600 para 700px
                    xaxis_rangeslider_visible=False,
                    showlegend=False,
                    hovermode='closest',
                    title=dict(
                        text='',
                        x=0.5,
                        xanchor='center'
                    ),
                    xaxis=dict(
                        gridcolor='#2a2a2a',
                        showgrid=True,
                        zeroline=False,
                        type='date',  # Melhor formatação de datas
                        rangeslider=dict(visible=False)
                    ),
                    yaxis=dict(
                        gridcolor='#2a2a2a',
                        showgrid=True,
                        zeroline=False,
                        side='right',
                        fixedrange=False  # Permite zoom no eixo Y
                    ),
                    dragmode='zoom'  # Modo padrão de drag como zoom
                )

                # Adicionar legenda customizada sempre
                st.markdown("""
                <div style='background:#1a1a1a; padding:12px; border-radius:6px; margin-bottom:10px; border:1px solid #333;'>
                    <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;'>
                        <strong style='color:#fff; margin-right:20px;'>📌 LEGENDA DO GRÁFICO:</strong>
                        <div style='display:flex; gap:15px; flex-wrap:wrap;'>
                            <span><span style='color:#00e676; font-size:16px;'>▲</span> <small>Long</small></span>
                            <span><span style='color:#ff5252; font-size:16px;'>▼</span> <small>Short</small></span>
                            <span><span style='color:#ffa726; font-size:16px;'>◆</span> <small>TP1</small></span>
                            <span><span style='color:#66bb6a; font-size:16px;'>◆</span> <small>TP2</small></span>
                            <span><span style='color:#00e676; font-size:16px;'>★</span> <small>TP3</small></span>
                            <span><span style='color:#ff5252; font-size:16px;'>✖</span> <small>SL</small></span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.plotly_chart(fig, use_container_width=True)
                
                # --- Results ---
                st.markdown("### DESEMPENHO DE TRADING")
                col_perf_left, col_perf_right = st.columns([1, 1])
                
                with col_perf_left:
                    banca_final = backtester.balance if backtester else initial_balance
                    profit = banca_final - initial_balance

                    # Winrate & Total Ops (Based on grouped positions, not individual partials)
                    total_ops_count = 0
                    win_ops_count = 0
                    loss_ops_count = 0

                    if not trades.empty:
                        grouped = trades.groupby('entry_time')
                        total_ops_count = len(grouped)
                        for _, group in grouped:
                            total_pnl = group['pnl'].sum()
                            if total_pnl > 0:
                                win_ops_count += 1
                            elif total_pnl < 0:
                                loss_ops_count += 1
                            # PnL = 0 não conta como win nem loss

                    winrate = (win_ops_count / total_ops_count * 100) if total_ops_count > 0 else 0

                    # Calcular comissão total paga
                    total_commission = backtester.total_commission_paid if backtester else 0

                    st.markdown(f"""
                    <div class="result-box">
                        <div style="margin-bottom: 5px;">
                            <span class="result-label">BANCA FINAL:</span> <span class="result-value">{banca_final:.2f}$</span>
                        </div>
                        <div style="margin-bottom: 5px;">
                            <span class="result-label">GANHO/PREJUIZO:</span> <span class="result-value {'result-value-pos' if profit >=0 else 'result-value-neg'}">{profit:.2f}$ ({(profit/initial_balance)*100:.1f}%)</span>
                        </div>
                        <div style="margin-bottom: 5px;">
                            <span class="result-label">COMISSÃO TOTAL:</span> <span class="result-value" style="color: #ffa726;">-{total_commission:.2f}$</span>
                        </div>
                        <div style="margin-bottom: 5px;">
                            <span class="result-label">WINRATE:</span> <span class="result-value result-value-pos">{winrate:.0f}%</span>
                        </div>
                        <div style="margin-bottom: 5px;">
                            <span class="result-label">TOTAL OP:</span> <span class="result-value">{total_ops_count}</span>
                        </div>
                        <div style="margin-bottom: 5px;">
                            <span class="result-label">OP LUCRO:</span> <span class="result-value result-value-pos">{win_ops_count}</span>
                        </div>
                        <div>
                            <span class="result-label">OP PREJUIZO:</span> <span class="result-value result-value-neg">{loss_ops_count}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Detailed Logs (Cards)
                    st.markdown("#### LOGS / REGISTROS")
                    if not trades.empty:
                        # Calcular FLOATING MÁXIMO GERAL com proteção
                        try:
                            max_floating_geral = trades['max_floating'].max() if 'max_floating' in trades.columns and not trades['max_floating'].isna().all() else 0
                            min_floating_geral = trades['min_floating'].min() if 'min_floating' in trades.columns and not trades['min_floating'].isna().all() else 0
                        except:
                            max_floating_geral = 0
                            min_floating_geral = 0

                        # Group by Entry Time to create "Operation" cards
                        # Sort by Entry Time descending (newest first)
                        grouped_trades = trades.groupby('entry_time')
                        ops = []
                        for entry_t, group in grouped_trades:
                            ops.append({
                                'entry_time': entry_t,
                                'group': group
                            })
                        ops.sort(key=lambda x: x['entry_time'], reverse=True)

                        log_container = st.container()
                        with log_container:
                            for i, op in enumerate(ops):
                                group = op['group']
                                first_row = group.iloc[0]
                                op_type = first_row['type'].upper()
                                op_color = "#00e676" if op_type == 'LONG' else "#ff5252"
                                entry_price = first_row['entry_price']
                                exit_price = first_row['exit_price']
                                total_pnl = group['pnl'].sum()
                                max_floating = first_row.get('max_floating', 0)

                                # Preparar informações dos eventos de forma mais simples
                                eventos_list = []
                                tps_status = {'tp1': '✗', 'tp2': '✗', 'tp3': '✗'}

                                for _, row in group.iterrows():
                                    reason = row['reason']

                                    # Atualizar status dos TPs
                                    if "Take Profit 1" in reason:
                                        tps_status['tp1'] = '✓'
                                        evento_nome = "TP1 (Parcial)" if "Partial" in reason else "TP1 (Final)"
                                    elif "Take Profit 2" in reason:
                                        tps_status['tp2'] = '✓'
                                        evento_nome = "TP2 (Parcial)" if "Partial" in reason else "TP2 (Final)"
                                    elif "Take Profit 3" in reason:
                                        tps_status['tp3'] = '✓'
                                        evento_nome = "TP3 (Final)"
                                    elif "Stop Loss" in reason:
                                        evento_nome = "STOP LOSS"
                                    else:
                                        evento_nome = reason

                                    eventos_list.append({
                                        'nome': evento_nome,
                                        'preco': row['exit_price'],
                                        'pnl': row['pnl'],
                                        'cor': '#00e676' if row['pnl'] > 0 else '#ff5252'
                                    })

                                # Calcular tamanho total da posição
                                total_size = group['size'].sum()

                                # Pegar última saída para mostrar preço final
                                last_exit = group.iloc[-1]
                                final_exit_price = last_exit['exit_price']

                                # Renderizar card usando componentes do Streamlit (mais seguro)
                                with st.container():
                                    # Cabeçalho do card
                                    st.markdown(f"""
                                    <div style="background:#262626; border-left:4px solid {op_color}; padding:15px; border-radius:6px; margin-bottom:20px; box-shadow: 0 2px 8px rgba(0,0,0,0.3);">
                                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                                            <strong style="color:{op_color}; font-size:18px; font-weight:900;">{i+1}° OPERAÇÃO: {op_type}</strong>
                                            <span style="color:#888; font-size:13px;">{str(op['entry_time'])[:19]}</span>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)

                                    # Métricas principais em 3 colunas
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("💰 Entrada", f"{entry_price:.5f}$", help="Preço de abertura da posição")
                                    with col2:
                                        st.metric("🎯 Saída Final", f"{final_exit_price:.5f}$", help="Preço da última saída")
                                    with col3:
                                        st.metric("📊 Resultado", f"{total_pnl:+.2f}$",
                                                 delta=f"{(total_pnl/initial_balance)*100:+.2f}%",
                                                 help="PnL total da operação")

                                    # Informações adicionais em 2 colunas
                                    col_a, col_b = st.columns(2)
                                    with col_a:
                                        st.metric("📏 Tamanho Total", f"{total_size:.4f} un", help="Quantidade total negociada")
                                    with col_b:
                                        st.metric("📈 Máx Floating", f"{max_floating:+.2f}%",
                                                 help="Máximo floating atingido")

                                    st.markdown("---")

                                    # Status dos TPs com cores
                                    st.markdown("**🎯 STATUS TAKE PROFITS:**")
                                    cols_tp = st.columns(3)
                                    with cols_tp[0]:
                                        tp1_icon = "✅" if tps_status['tp1'] == '✓' else "❌"
                                        tp1_color = "green" if tps_status['tp1'] == '✓' else "red"
                                        st.markdown(f"**TP1:** :{tp1_color}[{tp1_icon}]")
                                    with cols_tp[1]:
                                        tp2_icon = "✅" if tps_status['tp2'] == '✓' else "❌"
                                        tp2_color = "green" if tps_status['tp2'] == '✓' else "red"
                                        st.markdown(f"**TP2:** :{tp2_color}[{tp2_icon}]")
                                    with cols_tp[2]:
                                        tp3_icon = "✅" if tps_status['tp3'] == '✓' else "❌"
                                        tp3_color = "green" if tps_status['tp3'] == '✓' else "red"
                                        st.markdown(f"**TP3:** :{tp3_color}[{tp3_icon}]")

                                    st.markdown("---")

                                    # Eventos de saída com detalhes
                                    st.markdown("**🔔 EVENTOS DE SAÍDA:**")
                                    for idx, evento in enumerate(eventos_list, 1):
                                        pnl_emoji = "🟢" if evento['pnl'] > 0 else ("🔴" if evento['pnl'] < 0 else "⚪")
                                        st.markdown(f"""
                                        <div style="background:#1a1a1a; padding:8px; margin:5px 0; border-radius:4px; border-left:3px solid {evento['cor']};">
                                            <span style="color:#fff; font-weight:bold;">{idx}. {evento['nome']}</span><br>
                                            <span style="color:#888;">Preço:</span> <span style="color:#00e676; font-family:monospace;">{evento['preco']:.5f}$</span> |
                                            <span style="color:#888;">PnL:</span> <span style="color:{evento['cor']}; font-weight:bold; font-family:monospace;">{evento['pnl']:+.2f}$</span> {pnl_emoji}
                                        </div>
                                        """, unsafe_allow_html=True)

                                    st.markdown("<br>", unsafe_allow_html=True)

                            # FLOATING MÁXIMO GERAL no final
                            st.markdown(f"""
<div style="background-color: #1a1a1a; border: 1px solid #ff5252; padding: 10px; margin-top: 10px; text-align: center; border-radius: 4px;">
    <span style="color: #ff5252; font-weight: bold; font-size: 14px;">FLOATING MÁXIMO GERAL: {max_floating_geral:.2f}%</span>
</div>
""", unsafe_allow_html=True)


                with col_perf_right:
                    # Gráfico de Desempenho de Trading (Barras por operação)
                    st.markdown("#### DESEMPENHO DE TRADING")
                    if not trades.empty:
                        # Agrupar por operação
                        grouped_trades = trades.groupby('entry_time')
                        ops_pnl = []
                        for entry_t, group in grouped_trades:
                            ops_pnl.append(group['pnl'].sum())

                        # Criar gráfico de barras
                        fig_perf = go.Figure()
                        colors = ['#00e676' if pnl >= 0 else '#ff5252' for pnl in ops_pnl]
                        fig_perf.add_trace(go.Bar(
                            x=list(range(1, len(ops_pnl) + 1)),
                            y=ops_pnl,
                            marker=dict(color=colors),
                            showlegend=False
                        ))
                        fig_perf.update_layout(
                            template='plotly_dark',
                            paper_bgcolor='#2b2b2b',
                            plot_bgcolor='#2b2b2b',
                            margin=dict(l=0, r=0, t=0, b=0),
                            height=300,
                            xaxis=dict(showgrid=False, showticklabels=True, title="Operação"),
                            yaxis=dict(showgrid=True, gridcolor='#333', title="PnL ($)")
                        )
                        st.plotly_chart(fig_perf, use_container_width=True)
                    else:
                        st.info("📊 Execute um backtest para ver o gráfico de desempenho por operação")

                    st.markdown("#### GRÁFICO P&L ACUMULADO")
                    if not trades.empty:
                        # Simple PnL Area Chart
                        df_pnl = trades.copy()
                        df_pnl.set_index('exit_time', inplace=True)
                        df_pnl.sort_index(inplace=True)
                        df_pnl['cum_pnl'] = df_pnl['pnl'].cumsum()

                        fig_pnl = go.Figure()
                        fig_pnl.add_trace(go.Scatter(
                            x=df_pnl.index, y=df_pnl['cum_pnl'], fill='tozeroy', mode='lines',
                            line=dict(color='#00e676'), name='PnL'
                        ))
                        fig_pnl.update_layout(
                            template='plotly_dark',
                            paper_bgcolor='#2b2b2b',
                            plot_bgcolor='#2b2b2b',
                            margin=dict(l=0, r=0, t=0, b=0),
                            height=300,
                            showlegend=False,
                            xaxis=dict(showgrid=False, showticklabels=False),
                            yaxis=dict(showgrid=False, showticklabels=False)
                        )
                        st.plotly_chart(fig_pnl, use_container_width=True)
                    else:
                        st.info("📈 Execute um backtest para ver o gráfico de P&L acumulado")

            else:
                st.warning("Sem dados no período selecionado.")
        else:
            st.info("Carregando Dados... Se esta mensagem persistir, verifique a pasta data/.")
