import numpy as np
import pandas as pd

import utils
from check_errors import check_errors
from moving_averages import sma, ema, wma, hma, wilders_ma, kama
from helper_loops import psar_loop, supertrend_loop


def returns(df, column='close', ret_method='simple',
            add_col=False, return_struct='numpy'):            
    """ Calculate Returns
    
    Parameters
    ----------
    df : Pandas DataFrame
        A Dataframe containing the columns open/high/low/close/volume
        with the index being a date. open/high/low/close should all
        be floats. volume should be an int. The date index should be
        a Datetime.
    column : String, optional. The default is 'close'
        This is the name of the column you want to operate on.
    ret_method : String, optional. The default is 'simple'
        The kind of returns you want returned: 'simple' or 'log'
    add_col : Boolean, optional. The default is False
        By default the function will return a numpy array. If set to
        True, the function will add a column to the dataframe that was
        passed in to it instead or returning a numpy array.
    return_struct : String, optional. The default is 'numpy'
        Only two values accepted: 'numpy' and 'pandas'. If set to
        'pandas', a new dataframe will be returned.

    Returns
    -------
    There are 3 ways to return values from this function:
    1. add_col=False, return_struct='numpy' returns a numpy array (default)
    2. add_col=False, return_struct='pandas' returns a new dataframe
    3. add_col=True, adds a column to the dataframe that was passed in
    
    Note: If add_col=True the function exits and does not execute the
    return_struct parameter.
    """
    
    check_errors(df=df, column=column, ret_method=ret_method,
                 add_col=add_col, return_struct=return_struct)

    if ret_method == 'simple':
        returns = df[column].pct_change()
    elif ret_method == 'log':
        returns = np.log(df[column] / df[column].shift(1))

    if add_col == True:
        df[f'{ret_method}_ret'] = returns
        return df
    elif return_struct == 'pandas':
        return returns.to_frame(name=f'{ret_method}_ret')
    else:
        return returns.to_numpy()


def hvol(df, column='close', n=20, ret_method='simple', ddof=1,
         add_col=False, return_struct='numpy'):
    """ Calculate Annualized Historical Volatility
    
    Parameters
    ----------
    df : Pandas DataFrame
        A Dataframe containing the columns open/high/low/close/volume
        with the index being a date. open/high/low/close should all
        be floats. volume should be an int. The date index should be
        a Datetime.
    column : String, optional. The default is 'close'
        This is the name of the column you want to operate on.
    n : Int, optional. The default is 20
        This is the lookback period for which you want to calculate
        historical volatility.
    ddof : Int, optional. The default is 1
        The degrees of freedom to feed into the standard deviation
        function of pandas: 1 is for sample standard deviation and
        0 is for population standard deviation.
    ret_method : String, optional. The default is 'simple'
        The kind of returns you want returned: 'simple' or 'log'
    add_col : Boolean, optional. The default is False
        By default the function will return a numpy array. If set to
        True, the function will add a column to the dataframe that was
        passed in to it instead or returning a numpy array.
    return_struct : String, optional. The default is 'numpy'
        Only two values accepted: 'numpy' and 'pandas'. If set to
        'pandas', a new dataframe will be returned.

    Returns
    -------
    There are 3 ways to return values from this function:
    1. add_col=False, return_struct='numpy' returns a numpy array (default)
    2. add_col=False, return_struct='pandas' returns a new dataframe
    3. add_col=True, adds a column to the dataframe that was passed in
    
    Note: If add_col=True the function exits and does not execute the
    return_struct parameter.
    """
    
    check_errors(df=df, column=column, n=n, ret_method=ret_method, ddof=ddof,
                  add_col=add_col, return_struct=return_struct)

    rets = returns(df, column=column, ret_method=ret_method)
    _df = pd.DataFrame(rets, columns=[column])
    hvol = _df.rolling(window=n).std(ddof=ddof) * 252 ** 0.5
    hvol.columns = [f'hvol({n})']

    if add_col == True:
        df[f'hvol({n})'] = hvol.to_numpy()
        return df
    elif return_struct == 'pandas':
        return hvol
    else:
        return hvol.to_numpy()


def momentum(df, column='close', n=20, add_col=False, return_struct='numpy'):
    """ Momentum
    
    Parameters
    ----------
    df : Pandas DataFrame
        A Dataframe containing the columns open/high/low/close/volume
        with the index being a date. open/high/low/close should all
        be floats. volume should be an int. The date index should be
        a Datetime.
    column : String, optional. The default is 'close'
        This is the name of the column you want to operate on.
    n : Int, optional. The default is 20
        The lookback period.
    add_col : Boolean, optional. The default is False
        By default the function will return a numpy array. If set to True,
        the function will add a column to the dataframe that was passed
        in to it instead or returning a numpy array.
    return_struct : String, optional. The default is 'numpy'
        Only two values accepted: 'numpy' and 'pandas'. If set to
        'pandas', a new dataframe will be returned.

    Returns
    -------
    There are 3 ways to return values from this function:
    1. add_col=False, return_struct='numpy' returns a numpy array (default)
    2. add_col=False, return_struct='pandas' returns a new dataframe
    3. add_col=True, adds a column to the dataframe that was passed in
    
    Note: If add_col=True the function exits and does not execute the
    return_struct parameter.
    """
    
    check_errors(df=df, column=column, n=n,
                 add_col=add_col, return_struct=return_struct)

    mom = df[column].diff(n)

    if add_col == True:
        df[f'mom({n})'] = mom
        return df
    elif return_struct == 'pandas':
        return mom.to_frame(name=f'mom({n})')
    else:
        return mom.to_numpy()


def rate_of_change(df, column='close', n=20,
                   add_col=False, return_struct='numpy'):
    """ Rate of Change
    
    Parameters
    ----------
    df : Pandas DataFrame
        A Dataframe containing the columns open/high/low/close/volume
        with the index being a date. open/high/low/close should all
        be floats. volume should be an int.  The date index should be
        a Datetime.
    column : String, optional. The default is 'close'
        This is the name of the column you want to operate on.
    n : Int, optional. The default is 20
        The lookback period.
    add_col : Boolean, optional. The default is False
        By default the function will return a numpy array. If set to True,
        the function will add a column to the dataframe that was passed
        in to it instead or returning a numpy array.
    return_struct : String, optional. The default is 'numpy'
        Only two values accepted: 'numpy' and 'pandas'. If set to
        'pandas', a new dataframe will be returned.

    Returns
    -------
    There are 3 ways to return values from this function:
    1. add_col=False, return_struct='numpy' returns a numpy array (default)
    2. add_col=False, return_struct='pandas' returns a new dataframe
    3. add_col=True, adds a column to the dataframe that was passed in
    
    Note: If add_col=True the function exits and does not execute the
    return_struct parameter.
    """
    
    check_errors(df=df, column=column, n=n,
                 add_col=add_col, return_struct=return_struct)

    roc = df[column].diff(n) / df[column].shift(n) * 100

    if add_col == True:
        df[f'roc({n})'] = roc
        return df
    elif return_struct == 'pandas':
        return roc.to_frame(name=f'roc({n})')
    else:
        return roc.to_numpy()


def true_range(df, add_col=False, return_struct='numpy'):
    """ True Range
    
    Parameters
    ----------
    df : Pandas DataFrame
        A Dataframe containing the columns open/high/low/close/volume
        with the index being a date. open/high/low/close should all
        be floats. volume should be an int. The date index should be
        a Datetime.
    add_col : Boolean, optional. The default is False
        By default the function will return a numpy array. If set to True,
        the function will add a column to the dataframe that was passed
        in to it instead or returning a numpy array.
    return_struct : String, optional. The default is 'numpy'
        Only two values accepted: 'numpy' and 'pandas'. If set to
        'pandas', a new dataframe will be returned.

    Returns
    -------
    There are 3 ways to return values from this function:
    1. add_col=False, return_struct='numpy' returns a numpy array (default)
    2. add_col=False, return_struct='pandas' returns a new dataframe
    3. add_col=True, adds a column to the dataframe that was passed in
    
    Note: If add_col=True the function exits and does not execute the
    return_struct parameter.
    """

    check_errors(df=df, add_col=add_col, return_struct=return_struct)

    hl = df['high'] - df['low']
    hc = abs(df['high'] - df['close'].shift(1))
    lc = abs(df['low'] - df['close'].shift(1))
    tr = np.nanmax([hl, hc, lc], axis=0)

    if add_col == True:
        df['true_range'] = tr
        return df
    elif return_struct == 'pandas':
        return pd.DataFrame(tr, columns=['true_range'], index=df.index)
    else:
        return tr


def atr(df, n=20, ma_method='sma', add_col=False, return_struct='numpy'):
    """ Average True Range
    
    Parameters
    ----------
    df : Pandas DataFrame
        A Dataframe containing the columns open/high/low/close/volume
        with the index being a date. open/high/low/close should all
        be floats. volume should be an int. The date index should be
        a Datetime.
    n : Int, optional. The default is 20
        The lookback period.
    ma_method : String, optional. The default is 'sma'
        The method of smoothing the True Range.  Available smoothing
        methods: {'sma', 'ema', 'wma', 'hma', 'wilders'}
    add_col : Boolean, optional. The default is False
        By default the function will return a numpy array. If set to True,
        the function will add a column to the dataframe that was passed
        in to it instead or returning a numpy array.
    return_struct : String, optional. The default is 'numpy'
        Only two values accepted: 'numpy' and 'pandas'. If set to
        'pandas', a new dataframe will be returned.

    Returns
    -------
    There are 3 ways to return values from this function:
    1. add_col=False, return_struct='numpy' returns a numpy array (default)
    2. add_col=False, return_struct='pandas' returns a new dataframe
    3. add_col=True, adds a column to the dataframe that was passed in
    
    Note: If add_col=True the function exits and does not execute the
    return_struct parameter.
    """

    check_errors(df=df, n=n, ma_method=ma_method,
                 add_col=add_col, return_struct=return_struct)

    tr = true_range(df, add_col=False, return_struct='pandas')
    tr.columns = ['close']
    
    _ma = utils.moving_average_mapper(ma_method)
    atr = _ma(tr, n=n)            

    if add_col == True:
        df[f'{ma_method}_atr({n})'] = atr
        return df
    elif return_struct == 'pandas':
        return pd.DataFrame(atr,
                            columns=[f'{ma_method}_atr({n})'],
                            index=df.index)
    else:
        return atr


def atr_percent(df, column='close', n=20, ma_method='sma',
                add_col=False, return_struct='numpy'):
    """ Average True Range Percent
    
    Parameters
    ----------
    df : Pandas DataFrame
        A Dataframe containing the columns open/high/low/close/volume
        with the index being a date. open/high/low/close should all
        be floats. volume should be an int. The date index should be
        a Datetime.
    column : String, optional. The default is 'close'
        This is the name of the column you want to use as the denominator
        of the percentage calculation.
    n : Int, optional. The default is 20
        The lookback period.
    ma_method : String, optional.  The default is 'sma'
        The method of smoothing the True Range. Available smoothing
        methods: {'sma', 'ema', 'wma', 'hma', 'wilders'}
    add_col : Boolean, optional. The default is False
        By default the function will return a numpy array. If set to True,
        the function will add a column to the dataframe that was passed
        in to it instead or returning a numpy array.
    return_struct : String, optional. The default is 'numpy'
        Only two values accepted: 'numpy' and 'pandas'. If set to
        'pandas', a new dataframe will be returned.

    Returns
    -------
    There are 3 ways to return values from this function:
    1. add_col=False, return_struct='numpy' returns a numpy array (default)
    2. add_col=False, return_struct='pandas' returns a new dataframe
    3. add_col=True, adds a column to the dataframe that was passed in
    
    Note: If add_col=True the function exits and does not execute the
    return_struct parameter.
    """

    check_errors(df=df, column=column, n=n, ma_method=ma_method,
                 add_col=add_col, return_struct=return_struct)

    _atr = atr(df, n=n, ma_method=ma_method)
    atr_prcnt = (_atr / df[column]) * 100

    if add_col == True:
        df[f'atr_%({n})'] = atr_prcnt
        return df
    elif return_struct == 'pandas':
        return atr_prcnt.to_frame(name=f'atr_%({n})')
    else:
        return atr_prcnt.to_numpy()

    
def keltner_channel(df, column='close', n=20, ma_method='sma',
                    upper_factor=2.0, lower_factor=2.0,
                    add_col=False, return_struct='numpy'):
    """ Keltner Channels
    
    Parameters
    ----------
    df : Pandas DataFrame
        A Dataframe containing the columns open/high/low/close/volume
        with the index being a date. open/high/low/close should all
        be floats. volume should be an int. The date index should be
        a Datetime.
    column : String, optional. The default is 'close'
        This is the name of the column you want to operate on.
    n : Int, optional. The default is 20
        The lookback period.
    ma_method : String, optional. The default is 'sma'
        The method of smoothing the True Range. Available smoothing
        methods: {'sma', 'ema', 'wma', 'hma', 'wilders'}
    upper_factor : Float, optional. The default is 2.0
        The amount by which to multiply the ATR to create the upper channel.
    lower_factor : Float, optional. The default is 2.0
        The amount by which to multiply the ATR to create the lower channel.
    add_col : Boolean, optional. The default is False
        By default the function will return a numpy array. If set to True,
        the function will add a column to the dataframe that was passed
        in to it instead or returning a numpy array.
    return_struct : String, optional. The default is 'numpy'
        Only two values accepted: 'numpy' and 'pandas'. If set to
        'pandas', a new dataframe will be returned.

    Returns
    -------
    There are 3 ways to return values from this function:
    1. add_col=False, return_struct='numpy' returns a numpy array (default)
    2. add_col=False, return_struct='pandas' returns a new dataframe
    3. add_col=True, adds a column to the dataframe that was passed in
    
    Note: If add_col=True the function exits and does not execute the
    return_struct parameter.
    """
    
    check_errors(df=df, column=column, n=n, ma_method=ma_method,
                 upper_factor=upper_factor, lower_factor=lower_factor,
                 add_col=add_col, return_struct=return_struct)

    _ma_func = utils.moving_average_mapper(ma_method)
    
    _ma = _ma_func(df, column=column, n=n)
    _atr = atr(df, n=n, ma_method=ma_method)

    keltner_upper = _ma + (_atr * upper_factor)
    keltner_lower = _ma - (_atr * lower_factor)
    keltner = np.vstack((keltner_lower, keltner_upper)).transpose()

    if add_col == True:
        df[f'kelt({n})_lower'] = keltner_lower
        df[f'kelt({n})_upper'] = keltner_upper
        return df
    elif return_struct == 'pandas':
        return pd.DataFrame(keltner,
                            columns=[f'kelt({n})_lower', f'kelt({n})_upper'],
                            index=df.index)
    else:
        return keltner


def bollinger_bands(df, column='close', n=20, ma_method='sma', ddof=1,
                    upper_num_sd=2.0, lower_num_sd=2.0,
                    add_col=False, return_struct='numpy'):
    """ Bollinger Bands
    
    Parameters
    ----------
    df : Pandas DataFrame
        A Dataframe containing the columns open/high/low/close/volume
        with the index being a date. open/high/low/close should all
        be floats. volume should be an int. The date index should be
        a Datetime.
    column : String, optional. The default is 'close'
        This is the name of the column you want to operate on.
    n : Int, optional. The default is 20
        The lookback period.
    ma_method : String, optional. The default is 'sma'
        The method of smoothing the column to obtain the middle band.
        Available smoothing methods: {'sma', 'ema', 'wma', 'hma', 'wilders'}
    ddof : Int, optional. The default is 1
        The degrees of freedom to feed into the standard deviation
        function of pandas: 1 is for sample standard deviation and
        0 is for population standard deviation.
    upper_num_sd : Float, optional. The default is 2.0
        The amount by which to the standard deviation is multiplied and then
        added to the middle band to create the upper band.
    lower_num_sd : Float, optional. The default is 2.0
        The amount by which to the standard deviation is multiplied and then
        subtracted from the middle band to create the lower band.
    add_col : Boolean, optional. The default is False
        By default the function will return a numpy array. If set to True,
        the function will add a column to the dataframe that was passed
        in to it instead or returning a numpy array.
    return_struct : String, optional. The default is 'numpy'
        Only two values accepted: 'numpy' and 'pandas'. If set to
        'pandas', a new dataframe will be returned.

    Returns
    -------
    There are 3 ways to return values from this function:
    1. add_col=False, return_struct='numpy' returns a numpy array (default)
    2. add_col=False, return_struct='pandas' returns a new dataframe
    3. add_col=True, adds a column to the dataframe that was passed in
    
    Note: If add_col=True the function exits and does not execute the
    return_struct parameter.
    """
 
    check_errors(df=df, column=column, n=n, ma_method=ma_method,
                  upper_num_sd=upper_num_sd, lower_num_sd=lower_num_sd,
                  add_col=add_col, return_struct=return_struct)

    _ma_func = utils.moving_average_mapper(ma_method)

    price_std = (df[column].rolling(window=n).std(ddof=ddof)).to_numpy()
    mid_bb = _ma_func(df, column=column, n=n)
    lower_bb = mid_bb - (price_std * lower_num_sd)
    upper_bb = mid_bb + (price_std * upper_num_sd)
    bollinger = np.vstack((lower_bb, upper_bb)).transpose()

    if add_col == True:
        df[f'bb({n})_lower'] = lower_bb
        df[f'bb({n})_upper'] = upper_bb
        return df
    elif return_struct == 'pandas':
        return pd.DataFrame(bollinger,
                            columns=[f'bb({n})_lower', f'bb({n})_upper'],
                            index=df.index)
    else:
        return bollinger


def rsi(df, column='close', n=20, ma_method='sma',
        add_col=False, return_struct='numpy'):
    """ Relative Strength Index
    
    Parameters
    ----------
    df : Pandas DataFrame
        A Dataframe containing the columns open/high/low/close/volume
        with the index being a date. open/high/low/close should all
        be floats. volume should be an int. The date index should be
        a Datetime.
    column : String, optional. The default is 'close'
        This is the name of the column you want to operate on.
    n : Int, optional. The default is 20
        The lookback period.
    ma_method : String, optional. The default is 'sma'
        The method of smoothing the average up and average down variables.
        Available smoothing methods: {'sma', 'ema', 'wma', 'hma', 'wilders'}
    add_col : Boolean, optional. The default is False
        By default the function will return a numpy array. If set to True,
        the function will add a column to the dataframe that was passed
        in to it instead or returning a numpy array.
    return_struct : String, optional. The default is 'numpy'
        Only two values accepted: 'numpy' and 'pandas'. If set to
        'pandas', a new dataframe will be returned.

    Returns
    -------
    There are 3 ways to return values from this function:
    1. add_col=False, return_struct='numpy' returns a numpy array (default)
    2. add_col=False, return_struct='pandas' returns a new dataframe
    3. add_col=True, adds a column to the dataframe that was passed in
    
    Note: If add_col=True the function exits and does not execute the
    return_struct parameter.
    """
 
    check_errors(df=df, column=column, n=n, ma_method=ma_method,
                  add_col=add_col, return_struct=return_struct)

    change = pd.DataFrame(df[column].diff()).fillna(0)
    up, dn = change.copy(), change.copy()
    up[up < 0] = 0
    dn[dn > 0] = 0

    _ma_func = utils.moving_average_mapper(ma_method)

    avg_up = _ma_func(up, column=column, n=n)
    avg_dn = -_ma_func(dn, column=column, n=n)

    rsi = np.where(avg_dn == 0.0, 100, 100.0 - 100.0 / (1 + avg_up / avg_dn))

    if add_col == True:
        df[f'rsi({n})'] = rsi
        return df
    elif return_struct == 'pandas':
        return pd.DataFrame(rsi, columns=[f'rsi({n})'], index=df.index)
    else:
        return rsi


def tsi(df, column='close', n=1, slow=25, fast=13, sig=7,
        ma_method='sma', add_col=False, return_struct='numpy'):
    """ True Strength Index
    
    Parameters
    ----------
    df : Pandas DataFrame
        A Dataframe containing the columns open/high/low/close/volume
        with the index being a date. open/high/low/close should all
        be floats. volume should be an int. The date index should be
        a Datetime.
    column : String, optional. The default is 'close'
        This is the name of the column you want to operate on.
    n : Int, optional. The default is 1
        The lookback period for the initial momentum calculation.
    slow : Int, optional. The default is 25
        The lookback period for smoothing the momentum calculations.
    fast : Int, optional. The default is 13
        The lookback period for smoothing the slow calculations.
    sig : Int, optional. The default is 7
        The lookback period for smoothing the true strength calculations.
    ma_method : String, optional. The default is 'sma'
        The method of smoothing the average up and average down variables.
        Available smoothing methods: {'sma', 'ema', 'wma', 'hma', 'wilders'}
    add_col : Boolean, optional. The default is False
        By default the function will return a numpy array. If set to True,
        the function will add a column to the dataframe that was passed
        in to it instead or returning a numpy array.
    return_struct : String, optional. The default is 'numpy'
        Only two values accepted: 'numpy' and 'pandas'. If set to
        'pandas', a new dataframe will be returned.

    Returns
    -------
    There are 3 ways to return values from this function:
    1. add_col=False, return_struct='numpy' returns a numpy array (default)
    2. add_col=False, return_struct='pandas' returns a new dataframe
    3. add_col=True, adds a column to the dataframe that was passed in
    
    Note: If add_col=True the function exits and does not execute the
    return_struct parameter.
    """
 
    check_errors(df=df, column=column, n=n, slow=slow, fast=fast,
                  sig=sig, ma_method=ma_method,
                  add_col=add_col, return_struct=return_struct)

    mom = momentum(df, column=column, n=n, return_struct='pandas')
    abs_mom = abs(mom)

    _ma_func = utils.moving_average_mapper(ma_method)

    _slow = _ma_func(mom, column=f'mom({n})',
                     n=slow, return_struct='pandas')
    _abs_slow = _ma_func(abs_mom, column=f'mom({n})',
                         n=slow, return_struct='pandas')
    _fast = _ma_func(_slow, column=f'{ma_method}({slow})',
                     n=fast, return_struct='pandas')
    _abs_fast = _ma_func(_abs_slow, column=f'{ma_method}({slow})',
                         n=fast, return_struct='pandas')

    tsi = _fast / _abs_fast * 100
    signal = _ma_func(tsi, column=f'{ma_method}({fast})', n=sig)

    tsi_signal = np.vstack((tsi[f'{ma_method}({fast})'], signal)).transpose()

    if add_col == True:
        df[f'tsi({slow},{fast},{sig})'] = tsi_signal[:, 0]
        df['tsi_signal'] = tsi_signal[:, 1]
        return df
    elif return_struct == 'pandas':
        return pd.DataFrame(tsi_signal,
                            columns=[f'tsi({slow},{fast},{sig})', 'tsi_signal'],
                            index=df.index)
    else:
        return tsi_signal


def adx(df, column='close', n=20, ma_method='sma',
        add_col=False, return_struct='numpy'):
    """ Average Directional Index
    
    Parameters
    ----------
    df : Pandas DataFrame
        A Dataframe containing the columns open/high/low/close/volume
        with the index being a date. open/high/low/close should all
        be floats. volume should be an int. The date index should be
        a Datetime.
    column : String, optional. The default is 'close'
        This is just a place holder for this function so that dataframes that
        pass to other functions don't encounter errors. It shouldn't be changed.
    n : Int, optional. The default is 20
        The lookback period for the all internal calculations of the ADX.
    ma_method : String, optional. The default is 'sma'
        The method of smoothing the internal calculation of the ADX.
        Available smoothing methods: {'sma', 'ema', 'wma', 'hma', 'wilders'}
    add_col : Boolean, optional. The default is False
        By default the function will return a numpy array. If set to True,
        the function will add a column to the dataframe that was passed
        in to it instead or returning a numpy array.
    return_struct : String, optional. The default is 'numpy'
        Only two values accepted: 'numpy' and 'pandas'. If set to
        'pandas', a new dataframe will be returned.

    Returns
    -------
    There are 3 ways to return values from this function:
    1. add_col=False, return_struct='numpy' returns a numpy array (default)
    2. add_col=False, return_struct='pandas' returns a new dataframe
    3. add_col=True, adds a column to the dataframe that was passed in
    
    Note: If add_col=True the function exits and does not execute the
    return_struct parameter.
    """

    check_errors(df=df, column=column, n=n, ma_method=ma_method,
                  add_col=add_col, return_struct=return_struct)

    _atr = atr(df, n=n, ma_method=ma_method)

    up = (df['high'] - df['high'].shift(1)).fillna(0)
    dn = (df['low'].shift(1) - df['low']).fillna(0)
    up[up < 0] = 0
    dn[dn < 0] = 0
    pos = pd.DataFrame(((up > dn) & (up > 0)) * up, columns=[column])
    neg = pd.DataFrame(((dn > up) & (dn > 0)) * dn, columns=[column])

    _ma_func = utils.moving_average_mapper(ma_method)

    dm_pos = _ma_func(pos, column=column, n=n)
    dm_neg = _ma_func(neg, column=column, n=n)
    di_pos = 100 * (dm_pos / _atr)
    di_neg = 100 * (dm_neg / _atr)
    di_diff = abs(di_pos - di_neg)
    di_sum = di_pos + di_neg
    dx = pd.DataFrame(100 * (di_diff / di_sum), columns=[column]).fillna(0)
    _adx = _ma_func(dx, column=column, n=n)

    adx = np.vstack((_adx, di_pos, di_neg)).transpose()

    if add_col == True:
        df[f'ADX({n})'] = adx[:, 0]
        df['DI+'] = adx[:, 1]
        df['DI-'] = adx[:, 2]
        return df
    elif return_struct == 'pandas':
        return pd.DataFrame(adx,
                            columns=['adx', 'di+', 'di-'],
                            index=df.index)
    else:
        return adx


def parabolic_sar(df, af_step=0.02, max_af=0.2,
                  add_col=False, return_struct='numpy'):
    """ Parabolic Stop-and-Reverse
    
    Parameters
    ----------
    df : Pandas DataFrame
        A Dataframe containing the columns open/high/low/close/volume
        with the index being a date. open/high/low/close should all
        be floats. volume should be an int. The date index should be
        a Datetime.
    af_step : Float, optional. The default is 0.02
        The acceleration factor.
    max_af : Float, optional. The default is 0.2
        The maximum value the accleration factor can have.
    add_col : Boolean, optional. The default is False
        By default the function will return a numpy array. If set to True,
        the function will add a column to the dataframe that was passed
        in to it instead or returning a numpy array.
    return_struct : String, optional. The default is 'numpy'
        Only two values accepted: 'numpy' and 'pandas'. If set to
        'pandas', a new dataframe will be returned.

    Returns
    -------
    There are 3 ways to return values from this function:
    1. add_col=False, return_struct='numpy' returns a numpy array (default)
    2. add_col=False, return_struct='pandas' returns a new dataframe
    3. add_col=True, adds a column to the dataframe that was passed in
    
    Note: If add_col=True the function exits and does not execute the
    return_struct parameter.
    """

    check_errors(df=df, af_step=af_step, max_af=max_af,
                  add_col=add_col, return_struct=return_struct)

    _psar = df['close'].copy().to_numpy()
    high = df['high'].copy().to_numpy()
    low = df['low'].copy().to_numpy()

    psar = psar_loop(_psar, high, low, af_step, max_af)

    if add_col == True:
        df['psar'] = psar
        return df
    elif return_struct == 'pandas':
        return pd.DataFrame(psar,
                            columns=['psar'],
                            index=df.index)
    else:
        return psar


def supertrend(df, column='close', n=20, ma_method='sma', factor=2.0,
                add_col=False, return_struct='numpy'):
    """ Supertrend
    
    Parameters
    ----------
    df : Pandas DataFrame
        A Dataframe containing the columns open/high/low/close/volume
        with the index being a date. open/high/low/close should all
        be floats. volume should be an int. The date index should be
        a Datetime.
    column : String, optional. The default is 'close'
        This is the column that is sent to the loop to use for calculations.
        While uncommon, using 'open' instead of 'close' could be done.
    n : Int, optional. The default is 20
        This is the lookback period for the ATR that is used in the
        calculation and the beginning value for the loop.
    ma_method : String, optional. The default is 'sma'
        The method of smoothing the ATR.
    factor : Float, optional. The default is 2.0
        The value added and subtracted to the basic upper and basic
        lower bands.
    add_col : Boolean, optional. The default is False
        By default the function will return a numpy array. If set to True,
        the function will add a column to the dataframe that was passed
        in to it instead or returning a numpy array.
    return_struct : String, optional. The default is 'numpy'
        Only two values accepted: 'numpy' and 'pandas'. If set to
        'pandas', a new dataframe will be returned.

    Returns
    -------
    There are 3 ways to return values from this function:
    1. add_col=False, return_struct='numpy' returns a numpy array (default)
    2. add_col=False, return_struct='pandas' returns a new dataframe
    3. add_col=True, adds a column to the dataframe that was passed in
    
    Note: If add_col=True the function exits and does not execute the
    return_struct parameter.
    """

    check_errors(df=df, column=column, n=n, ma_method=ma_method,
                  factor=factor, add_col=add_col, return_struct=return_struct)

    _atr = atr(df, n=n, ma_method=ma_method)
    hl_avg = (df['high'] + df['low']) / 2
    close = df[column].to_numpy()
    basic_ub = (hl_avg + factor * _atr).to_numpy()
    basic_lb = (hl_avg - factor * _atr).to_numpy()
    supertrend = supertrend_loop(close, basic_ub, basic_lb, n)

    if add_col == True:
        df[f'supertrend({n})'] = supertrend
        return df
    elif return_struct == 'pandas':
        return pd.DataFrame(supertrend,
                            columns=[f'supertrend({n})'],
                            index=df.index)
    else:
        return supertrend


def acc_dist(df, add_col=False, return_struct='numpy'):
    """ Accumulation/Distribution
    
    Parameters
    ----------
    df : Pandas DataFrame
        A Dataframe containing the columns open/high/low/close/volume
        with the index being a date. open/high/low/close should all
        be floats. volume should be an int. The date index should be
        a Datetime.
    add_col : Boolean, optional. The default is False
        By default the function will return a numpy array. If set to True,
        the function will add a column to the dataframe that was passed
        in to it instead or returning a numpy array.
    return_struct : String, optional. The default is 'numpy'
        Only two values accepted: 'numpy' and 'pandas'. If set to
        'pandas', a new dataframe will be returned.

    Returns
    -------
    There are 3 ways to return values from this function:
    1. add_col=False, return_struct='numpy' returns a numpy array (default)
    2. add_col=False, return_struct='pandas' returns a new dataframe
    3. add_col=True, adds a column to the dataframe that was passed in
    
    Note: If add_col=True the function exits and does not execute the
    return_struct parameter.
    """

    check_errors(df=df, add_col=add_col, return_struct=return_struct)

    clv = ((2 * df['close'] - df['high'] - df['low']) /
            (df['high'] - df['low']) * df['volume'])
    ad = clv.cumsum()

    if add_col == True:
        df['acc_dist'] = ad
        return df
    elif return_struct == 'pandas':
        return ad.to_frame(name='acc_dist')
    else:
        return ad.to_numpy()


def obv(df, add_col=False, return_struct='numpy'):
    """ On-Balance Volume
    
    Parameters
    ----------
    df : Pandas DataFrame
        A Dataframe containing the columns open/high/low/close/volume
        with the index being a date. open/high/low/close should all
        be floats. volume should be an int. The date index should be
        a Datetime.
    add_col : Boolean, optional. The default is False
        By default the function will return a numpy array. If set to True,
        the function will add a column to the dataframe that was passed
        in to it instead or returning a numpy array.
    return_struct : String, optional. The default is 'numpy'
        Only two values accepted: 'numpy' and 'pandas'. If set to
        'pandas', a new dataframe will be returned.

    Returns
    -------
    There are 3 ways to return values from this function:
    1. add_col=False, return_struct='numpy' returns a numpy array (default)
    2. add_col=False, return_struct='pandas' returns a new dataframe
    3. add_col=True, adds a column to the dataframe that was passed in
    
    Note: If add_col=True the function exits and does not execute the
    return_struct parameter.
    """

    check_errors(df=df, add_col=add_col, return_struct=return_struct)

    _mask = df['close'].mask(df['close'] >= df['close'].shift(1), other = 1)
    mask = _mask.where(_mask == 1, other = -1)
    obv = (df['volume'] * mask).cumsum()

    if add_col == True:
        df['obv'] = obv
        return df
    elif return_struct == 'pandas':
        return obv.to_frame(name='obv')
    else:
        return obv.to_numpy()


def pivot_points(df, add_col=False, return_struct='numpy'):
    """ Traditional Pivot Points
    
    Parameters
    ----------
    df : Pandas DataFrame
        A Dataframe containing the columns open/high/low/close/volume
        with the index being a date. open/high/low/close should all
        be floats. volume should be an int. The date index should be
        a Datetime.
    add_col : Boolean, optional. The default is False
        By default the function will return a numpy array. If set to True,
        the function will add a column to the dataframe that was passed
        in to it instead or returning a numpy array.
    return_struct : String, optional. The default is 'numpy'
        Only two values accepted: 'numpy' and 'pandas'. If set to
        'pandas', a new dataframe will be returned.

    Returns
    -------
    There are 3 ways to return values from this function:
    1. add_col=False, return_struct='numpy' returns a numpy array (default)
    2. add_col=False, return_struct='pandas' returns a new dataframe
    3. add_col=True, adds a column to the dataframe that was passed in
    
    Note: If add_col=True the function exits and does not execute the
    return_struct parameter.
    """

    check_errors(df=df, add_col=add_col, return_struct=return_struct)

    _df = df.shift(1, axis=0)  # Use yesterday's HLC

    pp = (_df['high'] + _df['low'] + _df['close']) / 3
    r1 = 2 * pp - _df['low']
    s1 = 2 * pp - _df['high']
    r2 = pp + _df['high'] - _df['low']
    s2 = pp - _df['high'] + _df['low']
    r3 = 2 * pp + (_df['high'] - 2 * _df['low'])
    s3 = 2 * pp - (_df['high'] * 2 - _df['low'])

    pps = np.vstack((s3, s2, s1, pp, r1, r2, r3)).transpose()

    if add_col == True:
        df['s3'] = pps[:, 0]
        df['s2'] = pps[:, 1]
        df['s1'] = pps[:, 2]
        df['pp'] = pps[:, 3]
        df['r1'] = pps[:, 4]
        df['r2'] = pps[:, 5]
        df['r3'] = pps[:, 6]
        return df
    elif return_struct == 'pandas':
        return pd.DataFrame(pps,
                            columns=['s3', 's2', 's1', 'pp', 'r1', 'r2', 'r3'],
                            index=df.index)
    else:
        return pps


def fibonacci_pivots(df, add_col=False, return_struct='numpy'):
    """ Fibonacci Pivot Points
    
    Parameters
    ----------
    df : Pandas DataFrame
        A Dataframe containing the columns open/high/low/close/volume
        with the index being a date. open/high/low/close should all
        be floats. volume should be an int. The date index should be
        a Datetime.
    add_col : Boolean, optional. The default is False
        By default the function will return a numpy array. If set to True,
        the function will add a column to the dataframe that was passed
        in to it instead or returning a numpy array.
    return_struct : String, optional. The default is 'numpy'
        Only two values accepted: 'numpy' and 'pandas'. If set to
        'pandas', a new dataframe will be returned.

    Returns
    -------
    There are 3 ways to return values from this function:
    1. add_col=False, return_struct='numpy' returns a numpy array (default)
    2. add_col=False, return_struct='pandas' returns a new dataframe
    3. add_col=True, adds a column to the dataframe that was passed in
    
    Note: If add_col=True the function exits and does not execute the
    return_struct parameter.
    """

    check_errors(df=df, add_col=add_col, return_struct=return_struct)

    _df = df.shift(1, axis=0)  # Use yesterday's HLC

    pp = (_df['high'] + _df['low'] + _df['close']) / 3
    r1 = pp + 0.382 * (_df['high'] - _df['low'])
    s1 = pp - 0.382 * (_df['high'] - _df['low'])
    r2 = pp + 0.618 * (_df['high'] - _df['low'])
    s2 = pp - 0.618 * (_df['high'] - _df['low'])
    r3 = pp + (_df['high'] - _df['low'])
    s3 = pp - (_df['high'] * _df['low'])

    pps = np.vstack((s3, s2, s1, pp, r1, r2, r3)).transpose()

    if add_col == True:
        df['s3'] = pps[:, 0]
        df['s2'] = pps[:, 1]
        df['s1'] = pps[:, 2]
        df['pp'] = pps[:, 3]
        df['r1'] = pps[:, 4]
        df['r2'] = pps[:, 5]
        df['r3'] = pps[:, 6]
        return df
    elif return_struct == 'pandas':
        return pd.DataFrame(pps,
                            columns=['s3', 's2', 's1', 'pp', 'r1', 'r2', 'r3'],
                            index=df.index)
    else:
        return pps


def woodie_pivots(df, add_col=False, return_struct='numpy'):
    """ Woodie Pivot Points
    
    Parameters
    ----------
    df : Pandas DataFrame
        A Dataframe containing the columns open/high/low/close/volume
        with the index being a date. open/high/low/close should all
        be floats. volume should be an int. The date index should be
        a Datetime.
    add_col : Boolean, optional. The default is False
        By default the function will return a numpy array. If set to True,
        the function will add a column to the dataframe that was passed
        in to it instead or returning a numpy array.
    return_struct : String, optional. The default is 'numpy'
        Only two values accepted: 'numpy' and 'pandas'. If set to
        'pandas', a new dataframe will be returned.

    Returns
    -------
    There are 3 ways to return values from this function:
    1. add_col=False, return_struct='numpy' returns a numpy array (default)
    2. add_col=False, return_struct='pandas' returns a new dataframe
    3. add_col=True, adds a column to the dataframe that was passed in
    
    Note: If add_col=True the function exits and does not execute the
    return_struct parameter.
    """

    check_errors(df=df, add_col=add_col, return_struct=return_struct)

    _df = df.copy()  # Use today's open and yesterday's HL
    _df['prev_high'] = df['high'].shift(1)
    _df['prev_low'] = df['low'].shift(1)

    pp = (_df['prev_high'] + _df['prev_low'] + 2 * _df['open']) / 4
    r1 = pp * 2 - _df['prev_low']
    s1 = pp * 2 - _df['prev_high']
    r2 = pp + (_df['prev_high'] - _df['prev_low'])
    s2 = pp - (_df['prev_high'] - _df['prev_low'])
    r3 = _df['prev_high'] + 2 * (pp - _df['prev_low'])
    s3 = _df['prev_low'] -2 * (_df['prev_high'] - pp)

    pps = np.vstack((s3, s2, s1, pp, r1, r2, r3)).transpose()

    if add_col == True:
        df['s3'] = pps[:, 0]
        df['s2'] = pps[:, 1]
        df['s1'] = pps[:, 2]
        df['pp'] = pps[:, 3]
        df['r1'] = pps[:, 4]
        df['r2'] = pps[:, 5]
        df['r3'] = pps[:, 6]
        return df
    elif return_struct == 'pandas':
        return pd.DataFrame(pps,
                            columns=['s3', 's2', 's1', 'pp', 'r1', 'r2', 'r3'],
                            index=df.index)
    else:
        return pps


def demark_pivots(df, add_col=False, return_struct='numpy'):
    """ Demark Pivot Points
    
    Parameters
    ----------
    df : Pandas DataFrame
        A Dataframe containing the columns open/high/low/close/volume
        with the index being a date. open/high/low/close should all
        be floats. volume should be an int. The date index should be
        a Datetime.
    add_col : Boolean, optional. The default is False
        By default the function will return a numpy array. If set to True,
        the function will add a column to the dataframe that was passed
        in to it instead or returning a numpy array.
    return_struct : String, optional. The default is 'numpy'
        Only two values accepted: 'numpy' and 'pandas'. If set to
        'pandas', a new dataframe will be returned.

    Returns
    -------
    There are 3 ways to return values from this function:
    1. add_col=False, return_struct='numpy' returns a numpy array (default)
    2. add_col=False, return_struct='pandas' returns a new dataframe
    3. add_col=True, adds a column to the dataframe that was passed in
    
    Note: If add_col=True the function exits and does not execute the
    return_struct parameter.
    """

    check_errors(df=df, add_col=add_col, return_struct=return_struct)

    _df = df.shift(1, axis=0)  # Use yesterday's HLC

    if _df['open'] == _df['close']:
        num = 2 * _df['close'] + _df['high'] + _df['low']
    elif _df['close'] > _df['open']:
        num = 2 * _df['high'] + _df['low'] + _df['close']
    else:
        num = 2 * _df['low'] + _df['high'] + _df['close']

    pp = num / 4
    r1 = num / 2 - _df['low']
    s1 = num / 2 - _df['high']

    pps = np.vstack((s1, pp, r1)).transpose()

    if add_col == True:
        df['s1'] = pps[:, 0]
        df['pp'] = pps[:, 1]
        df['r1'] = pps[:, 2]
        return df
    elif return_struct == 'pandas':
        return pd.DataFrame(pps,
                            columns=['s1', 'pp', 'r1'],
                            index=df.index)
    else:
        return pps


# Full Stochastic Oscillator
def stochastic(df, n_k=14, n_d=3, n_slow=1, ma_method='sma',
               add_col=False, return_struct='numpy'):
    """ Stochastic Oscillator
    
    Parameters
    ----------
    df : Pandas DataFrame
        A Dataframe containing the columns open/high/low/close/volume
        with the index being a date. open/high/low/close should all
        be floats. volume should be an int. The date index should be
        a Datetime.
    n_k : Int, optional. The default is 14
        The lookback period over which the highest high and lowest low
        are determined to compute %k.
    n_d : Int, optional. The default is 3
        The number of periods that are used to smooth the full_k.
    n_slow : Int, optional. The default is 1
        The number of periods that are used to smooth %k. If left at the
        default (1) the function returns values that match a "Fast Stochastic".
        If a different value is used, the function return values that match a
        "Slow Stochastic".
    ma_method : String, optional. The default is 'sma'
        The method of smoothing the stochastics.
    add_col : Boolean, optional. The default is False
        By default the function will return a numpy array. If set to True,
        the function will add a column to the dataframe that was passed
        in to it instead or returning a numpy array.
    return_struct : String, optional. The default is 'numpy'
        Only two values accepted: 'numpy' and 'pandas'. If set to
        'pandas', a new dataframe will be returned.

    Returns
    -------
    There are 3 ways to return values from this function:
    1. add_col=False, return_struct='numpy' returns a numpy array (default)
    2. add_col=False, return_struct='pandas' returns a new dataframe
    3. add_col=True, adds a column to the dataframe that was passed in
    
    Note: If add_col=True the function exits and does not execute the
    return_struct parameter.
    """

    check_errors(df=df, n_k=n_k, n_d=n_d, n_slow=n_slow, ma_method=ma_method,
                 add_col=add_col, return_struct=return_struct)

    low = df['low'].rolling(n_k).min()
    high = df['high'].rolling(n_k).max()
    percent_k = ((df['close'] - low) / (high - low) * 100).to_frame(name='%k')

    _ma_func = utils.moving_average_mapper(ma_method)

    full_k = _ma_func(percent_k, column='%k', n=n_slow,
                      return_struct='pandas')
    full_d = _ma_func(full_k, column=f'{ma_method}({n_slow})', n=n_d,
                      return_struct='pandas')

    full_stoch = np.vstack((full_k[f'{ma_method}({n_slow})'],
                            full_d[f'{ma_method}({n_d})'])).transpose()

    if add_col == True:
        df[f'%k({n_k},{n_slow})'] = full_k
        df[f'%d({n_d})'] = full_d
        return df
    elif return_struct == 'pandas':
        return pd.DataFrame(full_stoch,
                            columns=[f'%k({n_k},{n_slow})', f'%d({n_d})'],
                            index=df.index)
    else:
        return full_stoch
    
    
# Stochastic-RSI Oscillator
def stochastic_rsi(df, n_k=14, n_d=3, n_slow=1, ma_method='sma',
                   add_col=False, return_struct='numpy'):
    """ Stochastic-RSI Oscillator -- Using a stochastic oscillator on RSI values
    
    Parameters
    ----------
    df : Pandas DataFrame
        A Dataframe containing the columns open/high/low/close/volume
        with the index being a date. open/high/low/close should all
        be floats. volume should be an int. The date index should be
        a Datetime.
    n_k : Int, optional. The default is 14
        The lookback period over which the highest high and lowest low
        are determined to compute %k.
    n_d : Int, optional. The default is 3
        The number of periods that are used to smooth the full_k.
    n_slow : Int, optional. The default is 1
        The number of periods that are used to smooth %k. If left at the
        default (1) the function returns values that match a "Fast Stochastic".
        If a different value is used, the function return values that match a
        "Slow Stochastic".
    ma_method : String, optional. The default is 'sma'
        The method of smoothing the RSI and stochastics.
    add_col : Boolean, optional. The default is False
        By default the function will return a numpy array. If set to True,
        the function will add a column to the dataframe that was passed
        in to it instead or returning a numpy array.
    return_struct : String, optional. The default is 'numpy'
        Only two values accepted: 'numpy' and 'pandas'. If set to
        'pandas', a new dataframe will be returned.

    Returns
    -------
    There are 3 ways to return values from this function:
    1. add_col=False, return_struct='numpy' returns a numpy array (default)
    2. add_col=False, return_struct='pandas' returns a new dataframe
    3. add_col=True, adds a column to the dataframe that was passed in
    
    Note: If add_col=True the function exits and does not execute the
    return_struct parameter.
    """

    check_errors(df=df, n_k=n_k, n_d=n_d, n_slow=n_slow, ma_method=ma_method,
                 add_col=add_col, return_struct=return_struct)

    rsi_df = rsi(df, n=n_k, ma_method=ma_method, return_struct='pandas')

    low = rsi_df[f'rsi({n_k})'].rolling(n_k).min()
    high = rsi_df[f'rsi({n_k})'].rolling(n_k).max()
    percent_k = ((rsi_df[f'rsi({n_k})'] - low) /
                 (high - low) * 100).to_frame(name='%k')

    _ma_func = utils.moving_average_mapper(ma_method)

    full_k = _ma_func(percent_k, column='%k', n=n_slow,
                      return_struct='pandas')
    full_d = _ma_func(full_k, column=f'{ma_method}({n_slow})', n=n_d,
                      return_struct='pandas')

    stoch_rsi = np.vstack((full_k[f'{ma_method}({n_slow})'],
                           full_d[f'{ma_method}({n_d})'])).transpose()

    if add_col == True:
            df[f'stoch_RSI %k({n_k},{n_slow})'] = full_k
            df[f'stoch_RSI %d({n_d})'] = full_d
            return df
    elif return_struct == 'pandas':
        return pd.DataFrame(stoch_rsi,
                            columns=[f'stoch_RSI %k({n_k},{n_slow})',
                                     f'stoch_RSI %d({n_d})'],
                            index=df.index)
    else:
        return stoch_rsi
      

# RSI-Stochastic Oscillator
def rsi_stochastic(df, n=14, ma_method='sma',
                   add_col=False, return_struct='numpy'):
    """ RSI-Stochastic Oscillator -- Using RSI on stochastic values
    
    Parameters
    ----------
    df : Pandas DataFrame
        A Dataframe containing the columns open/high/low/close/volume
        with the index being a date. open/high/low/close should all
        be floats. volume should be an int. The date index should be
        a Datetime.
    n : Int, optional. The default is 14
        The lookback period over which the highest high and lowest low
        are determined to compute %k.
    ma_method : String, optional. The default is 'sma'
        The method of smoothing the RSI and stochastics.
    add_col : Boolean, optional. The default is False
        By default the function will return a numpy array. If set to True,
        the function will add a column to the dataframe that was passed
        in to it instead or returning a numpy array.
    return_struct : String, optional. The default is 'numpy'
        Only two values accepted: 'numpy' and 'pandas'. If set to
        'pandas', a new dataframe will be returned.

    Returns
    -------
    There are 3 ways to return values from this function:
    1. add_col=False, return_struct='numpy' returns a numpy array (default)
    2. add_col=False, return_struct='pandas' returns a new dataframe
    3. add_col=True, adds a column to the dataframe that was passed in
    
    Note: If add_col=True the function exits and does not execute the
    return_struct parameter.
    """
    
    check_errors(df=df, n=n, ma_method=ma_method,
                 add_col=add_col, return_struct=return_struct)

    low = df['low'].rolling(n).min()
    high = df['high'].rolling(n).max()
    percent_k = ((df['close'] - low) / (high - low) * 100).to_frame(name='%k')

    rsi_stoch = rsi(percent_k, column='%k', n=n, ma_method=ma_method)

    if add_col == True:
        df[f'RSI_stoch({n})'] = rsi_stoch
        return df
    elif return_struct == 'pandas':
        return pd.DataFrame(rsi_stoch,
                            columns=[f'RSI_stoch({n})'],
                            index=df.index)
    else:
        return rsi_stoch


# Ultimate Oscillator
def ultimate_oscillator(df, n_fast=7, n_med=14, n_slow=28,
                        add_col=False, return_struct='numpy'):
    """ Ultimate Oscillator
    
    Parameters
    ----------
    df : Pandas DataFrame
        A Dataframe containing the columns open/high/low/close/volume
        with the index being a date. open/high/low/close should all
        be floats. volume should be an int. The date index should be
        a Datetime.
    n_fast : Int, optional. The default is 7
        The lookback period over which to compute the fast rolling ratio
    n_med : Int, optional. The default is 14
        The lookback period over which to compute the intermediate rolling ratio
    n_slow : Int, optional. The default is 28
        The lookback period over which to compute the slow rolling ratio
    add_col : Boolean, optional. The default is False
        By default the function will return a numpy array. If set to True,
        the function will add a column to the dataframe that was passed
        in to it instead or returning a numpy array.
    return_struct : String, optional. The default is 'numpy'
        Only two values accepted: 'numpy' and 'pandas'. If set to
        'pandas', a new dataframe will be returned.

    Returns
    -------
    There are 3 ways to return values from this function:
    1. add_col=False, return_struct='numpy' returns a numpy array (default)
    2. add_col=False, return_struct='pandas' returns a new dataframe
    3. add_col=True, adds a column to the dataframe that was passed in
    
    Note: If add_col=True the function exits and does not execute the
    return_struct parameter.
    """
    
    check_errors(df=df, n_fast=n_fast, n_med=n_med, n_slow=n_slow,
                 add_col=add_col, return_struct=return_struct)

    df['prev_clo'] = df['close'].shift(1)
    bp = df['close'] - (df[['low','prev_clo']].min(axis=1))
    tr = true_range(df, return_struct='pandas')

    first_ma = (bp.rolling(n_fast).sum() /
                tr['true_range'].rolling(n_fast).sum())
    second_ma = (bp.rolling(n_med).sum() /
                 tr['true_range'].rolling(n_med).sum())
    third_ma = (bp.rolling(n_slow).sum() /
                tr['true_range'].rolling(n_slow).sum())

    ult_osc = ((first_ma * 4 + second_ma * 2 + third_ma) / 7 * 100).to_numpy()

    if add_col == True:
        df[f'ultimate_oscillator({n_fast},{n_med},{n_slow})'] = ult_osc
        return df
    elif return_struct == 'pandas':
        return pd.DataFrame(ult_osc,
                            columns=[f'ultimate_oscillator({n_fast},{n_med},{n_slow})'],
                            index=df.index)
    else:
        return ult_osc


# Trix
def trix(df, column='close', n=20, ma_method='ema',
         add_col=False, return_struct='numpy'):
    """ TRIX - Triple smoothed exponential moving average
    
    Parameters
    ----------
    df : Pandas DataFrame
        A Dataframe containing the columns open/high/low/close/volume
        with the index being a date. open/high/low/close should all
        be floats. volume should be an int. The date index should be
        a Datetime.
    column : String, optional. The default is 'close'
        This is the column that the moving averages will be calculated on.
    n : Int, optional. The default is 20
        The lookback period over which to compute the moving averages
    ma_method : String, optional. The default is 'ema'
        Traditionally, TRIX is an exponential moving average smoothed
        3 times. This variable enables you to select other moving average
        types such as Simple, Weighted, Hull, or Wilders.
    add_col : Boolean, optional. The default is False
        By default the function will return a numpy array. If set to True,
        the function will add a column to the dataframe that was passed
        in to it instead or returning a numpy array.
    return_struct : String, optional. The default is 'numpy'
        Only two values accepted: 'numpy' and 'pandas'. If set to
        'pandas', a new dataframe will be returned.

    Returns
    -------
    There are 3 ways to return values from this function:
    1. add_col=False, return_struct='numpy' returns a numpy array (default)
    2. add_col=False, return_struct='pandas' returns a new dataframe
    3. add_col=True, adds a column to the dataframe that was passed in
    
    Note: If add_col=True the function exits and does not execute the
    return_struct parameter.
    """
    
    check_errors(df=df, column=column, n=n, ma_method=ma_method,
                 add_col=add_col, return_struct=return_struct)

    _ma_func = utils.moving_average_mapper(ma_method)

    ma_1 = _ma_func(df, column=column, n=n,
                    return_struct='pandas')
    ma_2 = _ma_func(ma_1, column=f'{ma_method}({n})', n=n,
                    return_struct='pandas')
    ma_3 = _ma_func(ma_2, column=f'{ma_method}({n})', n=n,
                    return_struct='pandas')

    ma_3['prev'] = ma_3[f'{ma_method}({n})'].shift(1)
    trix = ((ma_3[f'{ma_method}({n})'] / ma_3['prev'] - 1)).to_numpy()

    if add_col == True:
        df[f'trix {ma_method}({n})'] = trix
        return df
    elif return_struct == 'pandas':
        return pd.DataFrame(trix,
                            columns=[f'trix {ma_method}({n})'],
                            index=df.index)
    else:
        return trix


# MACD
def macd(df, column='close', n_fast=12, n_slow=26, n_macd=9, ma_method='ema',
         add_col=False, return_struct='numpy'):

    """ MACD - Moving average convergence divergence
    
    Parameters
    ----------
    df : Pandas DataFrame
        A Dataframe containing the columns open/high/low/close/volume
        with the index being a date. open/high/low/close should all
        be floats. volume should be an int. The date index should be
        a Datetime.
    column : String, optional. The default is 'close'
        This is the column that the moving averages will be calculated on.
    n_fast : Int, optional. The default is 12
        The lookback period over which to compute the first (fast) moving average.
    n_slow : Int, optional. The default is 26
        The lookback period over which to compute the second (slow) moving average.
    n_macd : Int, optional. The default is 9
        The lookback period over which to compute the moving average of the MACD to
        generate the signal line.
    ma_method : String, optional. The default is 'ema'
        Traditionally, MACD is calculated using exponential moving averages.
        This variable enables you to select other moving average types
        such as Simple, Weighted, Hull, or Wilders.
    add_col : Boolean, optional. The default is False
        By default the function will return a numpy array. If set to True,
        the function will add a column to the dataframe that was passed
        in to it instead or returning a numpy array.
    return_struct : String, optional. The default is 'numpy'
        Only two values accepted: 'numpy' and 'pandas'. If set to
        'pandas', a new dataframe will be returned.

    Returns
    -------
    There are 3 ways to return values from this function:
    1. add_col=False, return_struct='numpy' returns a numpy array (default)
    2. add_col=False, return_struct='pandas' returns a new dataframe
    3. add_col=True, adds a column to the dataframe that was passed in
    
    Note: If add_col=True the function exits and does not execute the
    return_struct parameter.
    """
    
    check_errors(df=df, column=column, n_fast=n_fast, n_slow=n_slow,
                 n_macd=n_macd, ma_method=ma_method, add_col=add_col,
                 return_struct=return_struct)

    _ma_func = utils.moving_average_mapper(ma_method)

    ma_fast = _ma_func(df, column=column, n=n_fast, return_struct='pandas')
    ma_slow = _ma_func(df, column=column, n=n_slow, return_struct='pandas')
    macd = (ma_fast[f'{ma_method}({n_fast})'] -
            ma_slow[f'{ma_method}({n_slow})']).to_frame(name='macd')
    macd['signal'] = _ma_func(macd, column='macd', n=n_macd)

    macd = macd.to_numpy()

    if add_col == True:
        df[f'macd({n_fast},{n_slow})'] = macd[:, 0]
        df[f'signal({n_macd})'] = macd[:, 1]
        return df
    elif return_struct == 'pandas':
        return pd.DataFrame(macd,
                            columns=[f'macd({n_fast},{n_slow})', f'signal({n_macd})'],
                            index=df.index)
    else:
        return macd


