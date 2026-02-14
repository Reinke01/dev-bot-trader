import pandas as pd
import numpy as np
from scipy.signal import find_peaks
import pandas_ta as ta

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from corretoras.funcoes_bybit import busca_velas

def prepare_market_data(
        df: pd.DataFrame,
        use_emas: bool = False,
        emas_periods: list[int] = [9, 21, 50, 200],
        use_volume_sma: bool = False,
        volume_sma_period: int = 20,
        use_rsi: bool = False,
        rsi_period: int = 14,
        use_stoch: bool = False,
        stoch_config: list[int] = [14, 3, 3],
        use_macd: bool = False,
        macd_config: list[int] = [12, 26, 9],
        use_atr: bool = False,
        atr_period: int = 14,
        use_adx: bool = False,
        adx_period: int = 14,
        use_bb: bool = False,
        bb_period: int = 20,
        use_peak_type: bool = False,
        use_peaks: bool = False,
        peaks_distance: int = 21,
    ) -> pd.DataFrame:
    if use_emas:
        for ema in emas_periods:
            df[f'EMA_{ema}'] = df['fechamento'].ewm(span=ema, adjust=False).mean().round(4)

    if use_volume_sma:
        df['volume_sma'] = df['volume'].rolling(window=volume_sma_period).mean().round(4)

    if use_rsi:
        rsi = ta.rsi(close=df['fechamento'], length=rsi_period).round(2)
        df = df.join(rsi)

    if use_stoch:
        stoch = ta.stoch(high=df['maxima'], low=df['minima'], close=df['fechamento'], k=stoch_config[0], d=stoch_config[1], smooth_k=stoch_config[2]).round(2)
        df = df.join(stoch)

    if use_macd:
        df['MACD'] = ta.macd(close=df['fechamento'], fast=macd_config[0], slow=macd_config[1], signal=macd_config[2])[f'MACD_{macd_config[0]}_{macd_config[1]}_{macd_config[2]}'].round(4)
        df['MACD_signal'] = ta.macd(close=df['fechamento'], fast=macd_config[0], slow=macd_config[1], signal=macd_config[2])[f'MACDs_{macd_config[0]}_{macd_config[1]}_{macd_config[2]}'].round(4)
        df['MACD_hist'] = ta.macd(close=df['fechamento'], fast=macd_config[0], slow=macd_config[1], signal=macd_config[2])[f'MACDh_{macd_config[0]}_{macd_config[1]}_{macd_config[2]}'].round(4)

    if use_atr: 
        atr = ta.atr(high=df['maxima'], low=df['minima'], close=df['fechamento'], length=atr_period).round(4)
        df = df.join(atr)

    if use_adx:
        adx = ta.adx(high=df['maxima'], low=df['minima'], close=df['fechamento'], length=adx_period)
        df = df.join(adx)

    if use_bb:
        bbands = ta.bbands(close=df['fechamento'], length=bb_period, std=1)
        df = df.join(bbands)
        
        bbands_2std = ta.bbands(close=df['fechamento'], length=bb_period, std=2)
        df = df.join(bbands_2std)

        bbands_3std = ta.bbands(close=df['fechamento'], length=bb_period, std=3)
        df = df.join(bbands_3std)

    if use_peak_type:
        df['peak_type'] = 0
        try:
            fundos, _ = find_peaks(-df['fechamento'], distance=peaks_distance)
            topos, _ = find_peaks(df['fechamento'], distance=peaks_distance)
        except:
            fundos = np.array([])
            topos = np.array([])
        
        peak_type = np.zeros(len(df), dtype=int)
        if len(fundos) > 0:
            peak_type[fundos] = 1
        if len(topos) > 0:
            peak_type[topos] = -1
        df['peak_type'] = peak_type

    if use_peaks:
        df['peaks'] = 0
        try:
            fundos, _ = find_peaks(-df['fechamento'], distance=peaks_distance)
            topos, _ = find_peaks(df['fechamento'], distance=peaks_distance)
        except:
            fundos = np.array([])
            topos = np.array([])

        df['top_high'] = np.nan
        df['top_close'] = np.nan
        df['bottom_low'] = np.nan
        df['bottom_close'] = np.nan

        if len(topos) > 0:
            # Para cada topo, verifica a máxima de 2 antes, atual e 2 depois e marca o índice da maior
            for idx in topos:
                prev2_idx = idx - 2 if idx - 2 >= 0 else idx
                prev_idx = idx - 1 if idx - 1 >= 0 else idx
                next_idx = idx + 1 if idx + 1 < len(df) else idx
                next2_idx = idx + 2 if idx + 2 < len(df) else idx
                sub_idxs = [prev2_idx, prev_idx, idx, next_idx, next2_idx]
                max_idx = sub_idxs[np.argmax(df['maxima'].iloc[sub_idxs].values)]
                close_idx_top = sub_idxs[np.argmax(df['fechamento'].iloc[sub_idxs].values)]
                df.loc[df.index[max_idx], 'top_high'] = df['maxima'].iloc[max_idx]
                df.loc[df.index[close_idx_top], 'top_close'] = df['fechamento'].iloc[close_idx_top]
        if len(fundos) > 0:
            # Para cada fundo, verifica a mínima de 2 antes, atual e 2 depois e marca o índice da menor
            for idx in fundos:
                prev2_idx = idx - 2 if idx - 2 >= 0 else idx
                prev_idx = idx - 1 if idx - 1 >= 0 else idx
                next_idx = idx + 1 if idx + 1 < len(df) else idx
                next2_idx = idx + 2 if idx + 2 < len(df) else idx
                sub_idxs = [prev2_idx, prev_idx, idx, next_idx, next2_idx]
                min_idx = sub_idxs[np.argmin(df['minima'].iloc[sub_idxs].values)]
                close_idx_bottom = sub_idxs[np.argmin(df['fechamento'].iloc[sub_idxs].values)]
                df.loc[df.index[min_idx], 'bottom_low'] = df['minima'].iloc[min_idx]
                df.loc[df.index[close_idx_bottom], 'bottom_close'] = df['fechamento'].iloc[close_idx_bottom]

    return df

def prepare_multi_timeframe_technical_data(df: pd.DataFrame, cripto: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df_1w = busca_velas(cripto, 'W', [9, 21])
    if len(df_1w) >= 50:
        df_1w = prepare_market_data(df_1w, use_emas=True, emas_periods=[200], use_macd=True)

    df_1d = busca_velas(cripto, 'D', [9, 21])
    if len(df_1d) >= 20:
        df_1d = prepare_market_data(df_1d, use_emas=True, emas_periods=[200], use_atr=True, atr_period=3, use_stoch=True, stoch_config=[5, 3, 3])

    df = prepare_market_data(df, use_emas=True, emas_periods=[200], use_volume_sma=True, use_rsi=True)

    return df_1w, df_1d, df