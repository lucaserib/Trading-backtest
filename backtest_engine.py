import pandas as pd
import ta
import numpy as np

import glob
import os

def load_data(source_dir, ticker_filter=None):
    """
    Loads CSV data from a directory.
    If ticker_filter is provided (e.g. '1000PEPEUSDT'), loads all CSVs matching that ticker.
    Expected columns: open_time, open, high, low, close, volume, etc.
    """
    if not os.path.exists(source_dir):
        return pd.DataFrame()
        
    pattern = "*.csv"
    if ticker_filter:
        pattern = f"*{ticker_filter}*.csv"
        
    files = glob.glob(os.path.join(source_dir, pattern))
    if not files:
        return pd.DataFrame()
        
    dfs = []
    for f in sorted(files):
        try:
            df_temp = pd.read_csv(f)
            dfs.append(df_temp)
        except Exception as e:
            print(f"Error reading {f}: {e}")
            
    if not dfs:
        return pd.DataFrame()
        
    df = pd.concat(dfs, ignore_index=True)
    
    # Clean and Convert
    if 'open_time' in df.columns:
        df['timestamp'] = pd.to_datetime(df['open_time'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df.sort_index(inplace=True)
        # Drop duplicates just in case files overlap
        df = df[~df.index.duplicated(keep='first')]
        
    return df

def resample_data(df, timeframe):
    """
    Resamples dataframe to a new timeframe.
    timeframe: str (e.g., '15min', '1H', '4H', '1D')
    """
    # Fix for 'm' deprecation -> Pandas prefers 'min' or 'T'
    if timeframe.endswith('m'):
        timeframe = timeframe.replace('m', 'min')
        
    if timeframe == '5min': # Base timeframe
        return df
        
    agg_dict = {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        # 'volume': 'sum' # key might not exist if simple ohlc
    }
    if 'volume' in df.columns:
        agg_dict['volume'] = 'sum'
    
    # Resample
    df_resampled = df.resample(timeframe).agg(agg_dict)
    df_resampled.dropna(inplace=True)
    return df_resampled

class Strategy:
    def __init__(self, df):
        self.df = df.copy()

    def ema_crossover_variation(self, fast_length=5, slow_length=200):
        """
        Implements the 'Cruzamento EMA + Variação %' strategy.
        Tracks variations (Max Favorable Excursion) between signals.
        """
        # 1. Calculate EMAs
        self.df['ema_fast'] = ta.trend.ema_indicator(self.df['close'], window=fast_length)
        self.df['ema_slow'] = ta.trend.ema_indicator(self.df['close'], window=slow_length)
        
        # 2. Vectorized Signals
        self.df['signal'] = 0
        
        # Buy: Fast crosses above Slow
        self.df.loc[(self.df['ema_fast'] > self.df['ema_slow']) & (self.df['ema_fast'].shift(1) <= self.df['ema_slow'].shift(1)), 'signal'] = 1
        
        # Sell: Fast crosses below Slow
        self.df.loc[(self.df['ema_fast'] < self.df['ema_slow']) & (self.df['ema_fast'].shift(1) >= self.df['ema_slow'].shift(1)), 'signal'] = -1

        # 3. Simulate "Var" Logic (Row by Row usually needed for state, or strictly vectorized with groups)
        # We need to track 'extreme_price' between signals to calculate the variation labels.
        # Efficient iterrows approach for state tracking (fast enough for 1-5min bars usually)
        
        extreme_price = None
        entry_price = None
        trade_direction = 0 # 0, 1 (Long), -1 (Short)
        
        # Columns for visualization
        self.df['var_label'] = None # Stores string like "Máx: +5.00%"
        self.df['var_value'] = 0.0
        
        # We iterate to simulate the "Pine Script var" behavior
        # Using numpy arrays for speed if needed, but simple iteration for clarity first
        
        signal_col = self.df.columns.get_loc('signal')
        high_col = self.df.columns.get_loc('high')
        low_col = self.df.columns.get_loc('low')
        close_col = self.df.columns.get_loc('close')
        var_label_col = self.df.columns.get_loc('var_label')
        
        # Convert to numpy for iteration (faster)
        values = self.df.values
        
        for i in range(1, len(values)):
            sig = values[i, signal_col]
            h = values[i, high_col]
            l = values[i, low_col]
            c = values[i, close_col]
            
            # Logic from Pine Script
            # if sell_signal
            if sig == -1:
                if trade_direction == 1:
                    # Close previous Long
                    if entry_price and extreme_price:
                        variation_up = ((extreme_price - entry_price) / entry_price) * 100
                        values[i, var_label_col] = f"Máx: +{variation_up:.2f}%"
                
                # New Short
                trade_direction = -1
                entry_price = c
                extreme_price = l # Start extreme at low
                
            # if buy_signal
            elif sig == 1:
                if trade_direction == -1:
                    # Close previous Short
                    if entry_price and extreme_price:
                        # Variation Down (Negative usually, showing drop)
                        # Script says: ((extreme - entry) / entry) * 100. For short, extreme is Low (lower than enty). 
                        # Result is negative, which is correct for price drop magnitude.
                        variation_down = ((extreme_price - entry_price) / entry_price) * 100
                        values[i, var_label_col] = f"Mín: {variation_down:.2f}%"
                
                # New Long
                trade_direction = 1
                entry_price = c
                extreme_price = h
            
            # Track Extremes
            if trade_direction == 1 and h > extreme_price:
                extreme_price = h
            elif trade_direction == -1 and l < extreme_price:
                extreme_price = l
                
        # Write back to DF
        self.df['var_label'] = values[:, var_label_col]
        
        return self.df

class Backtester:
    def __init__(self, df, initial_balance=1000, leverage=1, entry_pct=1.0):
        self.df = df
        self.balance = initial_balance
        self.initial_balance = initial_balance
        self.leverage = leverage
        self.entry_pct = entry_pct  # % da banca a usar por operação
        self.trades = []
        self.equity_curve = [initial_balance]

    def run(self, stop_loss_pct, take_profit_pcts, tp_quantities, use_breakeven=False, use_breakgain=False):
        """
        Runs the backtest.
        take_profit_pcts: list of TP percentages (e.g., [0.005, 0.01, 0.02, 0.05]) - até 4 TPs
        tp_quantities: list of TP quantities (e.g., [0.3, 0.3, 0.2, 0.2]) - até 4 TPs
        use_breakeven: bool - Move SL para entrada após primeiro TP
        use_breakgain: bool - Move SL para TP anterior após acionar próximo TP
        """
        position = None

        for i in range(1, len(self.df)):
            current_bar = self.df.iloc[i]
            prev_bar = self.df.iloc[i-1]
            timestamp = self.df.index[i]

            # Check for exits if in position
            if position:
                self._check_exit(position, current_bar, timestamp, use_breakeven, use_breakgain)
                if position['status'] == 'closed':
                    position = None

            # Check for entries if no position
            if not position:
                if prev_bar['signal'] == 1:
                    position = self._open_position('long', current_bar['open'], timestamp, stop_loss_pct, take_profit_pcts, tp_quantities)
                elif prev_bar['signal'] == -1:
                    position = self._open_position('short', current_bar['open'], timestamp, stop_loss_pct, take_profit_pcts, tp_quantities)

        # Close any open position at the end
        if position:
            self._close_position(position, self.df.iloc[-1]['close'], self.df.index[-1], 'End of Data')

        trades_df = pd.DataFrame(self.trades)
        return trades_df

    def _open_position(self, side, price, timestamp, sl_pct, tp_pcts, tp_quantities):
        # Usar % ENTRADA corretamente
        capital_to_use = self.balance * self.entry_pct
        size = (capital_to_use * self.leverage) / price
        
        if side == 'long':
            sl_price = price * (1 - sl_pct)
            tps = []
            for tp in tp_pcts:
                tps.append({'price': price * (1 + tp), 'hit': False})
        else:
            sl_price = price * (1 + sl_pct)
            tps = []
            for tp in tp_pcts:
                tps.append({'price': price * (1 - tp), 'hit': False})

        return {
            'status': 'open',
            'type': side,
            'entry_price': price,
            'entry_time': timestamp,
            'size': size,
            'original_size': size,
            'sl': sl_price,
            'original_sl': sl_price,
            'tps': tps,
            'tp_quantities': tp_quantities,
            'pnl': 0,
            'max_favorable_excursion': 0,  # Máximo floating favorável
            'max_adverse_excursion': 0,     # Máximo floating adverso
            'tps_hit_info': []  # Rastreia quais TPs foram acionados e como
        }

    def _check_exit(self, position, bar, timestamp, use_breakeven, use_breakgain):
        # Rastrear floating máximo/mínimo
        if position['type'] == 'long':
            current_pnl_pct = ((bar['high'] - position['entry_price']) / position['entry_price']) * 100
            position['max_favorable_excursion'] = max(position['max_favorable_excursion'], current_pnl_pct)
            adverse_pnl_pct = ((bar['low'] - position['entry_price']) / position['entry_price']) * 100
            position['max_adverse_excursion'] = min(position['max_adverse_excursion'], adverse_pnl_pct)
        else:
            current_pnl_pct = ((position['entry_price'] - bar['low']) / position['entry_price']) * 100
            position['max_favorable_excursion'] = max(position['max_favorable_excursion'], current_pnl_pct)
            adverse_pnl_pct = ((position['entry_price'] - bar['high']) / position['entry_price']) * 100
            position['max_adverse_excursion'] = min(position['max_adverse_excursion'], adverse_pnl_pct)

        # 1. Check SL
        if position['type'] == 'long':
            if bar['low'] <= position['sl']:
                self._close_position(position, position['sl'], timestamp, 'Stop Loss')
                return
        else:
            if bar['high'] >= position['sl']:
                self._close_position(position, position['sl'], timestamp, 'Stop Loss')
                return

        # 2. Check TPs
        for i, tp in enumerate(position['tps']):
            if not tp['hit']:
                hit = False
                if position['type'] == 'long' and bar['high'] >= tp['price']:
                    hit = True
                elif position['type'] == 'short' and bar['low'] <= tp['price']:
                    hit = True

                if hit:
                    tp['hit'] = True
                    qty_pct = position['tp_quantities'][i] if i < len(position['tp_quantities']) else 0

                    # Aplicar BREAKEVEN após primeiro TP
                    if use_breakeven and i == 0:
                        position['sl'] = position['entry_price']
                        position['tps_hit_info'].append({'tp': i+1, 'type': 'BREAKEVEN'})

                    # Aplicar BREAKGAIN - Move SL para TP anterior
                    elif use_breakgain and i > 0:
                        prev_tp_price = position['tps'][i-1]['price']
                        position['sl'] = prev_tp_price
                        position['tps_hit_info'].append({'tp': i+1, 'type': 'BREAKGAIN'})
                    else:
                        position['tps_hit_info'].append({'tp': i+1, 'type': 'ACIONADO'})

                    # Se é o último TP ou 100%, fecha tudo
                    remaining_tps = [t for t in position['tps'] if not t['hit']]
                    if not remaining_tps or qty_pct >= 1.0:
                        self._close_position(position, tp['price'], timestamp, f'Take Profit {i+1} (Final)')
                        return
                    else:
                        # Fechamento Parcial
                        close_size = position['original_size'] * qty_pct
                        self._register_trade(position, tp['price'], timestamp, f'Take Profit {i+1} (Partial)', size_to_close=close_size)
                        position['size'] -= close_size

    def _close_position(self, position, price, timestamp, reason):
        self._register_trade(position, price, timestamp, reason, size_to_close=position['size'])
        position['status'] = 'closed'
        position['size'] = 0

    def _register_trade(self, position, price, timestamp, reason, size_to_close):
        # Calculate PnL
        if position['type'] == 'long':
            pnl = (price - position['entry_price']) * size_to_close
        else:
            pnl = (position['entry_price'] - price) * size_to_close

        self.balance += pnl

        # Informações de TPs acionados para esta saída específica
        tps_status = {}
        for i in range(len(position['tps'])):
            tp_info = next((info for info in position['tps_hit_info'] if info['tp'] == i+1), None)
            if tp_info:
                tps_status[f'tp{i+1}_status'] = tp_info['type']
            else:
                tps_status[f'tp{i+1}_status'] = 'PENDENTE' if not position['tps'][i]['hit'] else 'ACIONADO'

        self.trades.append({
            'entry_time': position['entry_time'],
            'exit_time': timestamp,
            'type': position['type'],
            'entry_price': position['entry_price'],
            'exit_price': price,
            'size': size_to_close,
            'pnl': pnl,
            'reason': reason,
            'balance': self.balance,
            'max_floating': position['max_favorable_excursion'],
            'min_floating': position['max_adverse_excursion'],
            **tps_status
        })
