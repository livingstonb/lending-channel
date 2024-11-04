import pandas as pd
from matplotlib import pyplot as plt
from fredapi import Fred

def fredkey():
    return '304287798bfe06df71176401cb843da6'

def event_stock_returns(fpath, eventnum):
    stocks = pd.read_csv("data/bank_and_sp500_returns_501.csv")
    stocks.loc[stocks.dividend.isnull(), 'dividend'] = 0
    stocks.price += stocks.dividend
    stocks = stocks[['date', 'ticker', 'price']]
    stocks.date = pd.to_datetime(stocks.date)

    # Dates for normalization and sample
    if eventnum == 1:
        event_date = [pd.to_datetime("3/9/23")]
        dates = [pd.to_datetime("1/1/23"), pd.to_datetime("5/1/23")]
        months = [1, 2, 3, 4]
        plot_ylims = [80, 120]
    elif eventnum == 2:
        event_date = [pd.to_datetime("5/1/23")]
        dates = [pd.to_datetime("4/1/23"), pd.to_datetime("7/1/23")]
        months = [4, 5, 6]
        plot_ylims = [85, 110]
    elif eventnum == 'all':
        event_date = [pd.to_datetime("3/9/23"), pd.to_datetime("5/1/23")]
        dates = [pd.to_datetime("1/1/23"), pd.to_datetime("6/1/23")]
        months = [1, 2, 3, 4, 5]
        plot_ylims = [70, 115]

    stocks_pre_event = stocks[stocks.date == pd.to_datetime("1/3/23")]
    for tick in ['SPY', 'KBE']:
        pnorm = stocks_pre_event[stocks_pre_event.ticker == tick].price.values
        prices = stocks[stocks.ticker == tick]['price'].values
        stocks.loc[stocks.ticker == tick, 'price'] = (prices / pnorm * 100)

    # Date range for plots
    daterange = (stocks.date >= dates[0]) & (stocks.date <= dates[1])

    # Plot
    fig, axes = plt.subplots(nrows=1, ncols=2)
    tick_daterange = [pd.to_datetime(f"{k}/1/23") for k in months]
    tick_labels = [f"{k}/1" for k in months]
    for i, tick in enumerate(['SPY', 'KBE']):
        sample = (stocks.ticker == tick) & daterange
        axes[i].plot(stocks[sample].date, stocks[sample].price)
        for el in event_date:
            axes[i].axvline(x=el, color='0.5', linestyle='--')
        axes[i].set_xticks(tick_daterange, tick_labels)
        axes[i].set_ylim(plot_ylims)

    axes[0].set_title('S&P 500')
    axes[1].set_title('SPDR Banking ETF')

    plt.tight_layout()
    fig.set_size_inches(6.4, 4)
    fig.savefig(f'temp/index_stock_prices_event{eventnum}.png', dpi=100)

    return stocks

def fred_plots():
    fred = Fred(api_key=fredkey())
    rmort30 = fred.get_series(series_id='MORTGAGE30US', observation_start='2000-01-01', frequency='weth')
    rmort30.name = '30y Mortgage Rate'
    t10 = fred.get_series(series_id='DGS10', observation_start='2000-01-01', frequency='d')
    t10.name = '10y Treasury Yield'
    ffr = fred.get_series(series_id='DFF', observation_start='2000-01-01', frequency='d')
    ffr.name = 'Federal Funds Rate'
    hprice = fred.get_series(series_id='CSUSHPINSA', observation_start='2000-01-01', frequency='m')
    hprice.name = 'Home Price Index'

    data = pd.concat((rmort30, t10, ffr), axis=1)

    # Zoomed in, no home prices
    yy = [2022, 2024]
    ylim = [0, 8]
    one_plot(data, yy, ylim)
    plt.savefig('output/macro_rates.png')

    # Longer period, with home prices
    # yy = [2015, 2024]
    # ylim = [0, 8]
    # one_plot(data, yy, ylim, hprice)
    # plt.savefig('output/macro_rates_extended.png')

    return None

def one_plot(data, yy, ylim, hprices=None):
    dates = [pd.to_datetime(x) for x in [f'1/1/{yy[0]}', f'1/1/{yy[1]}']]
    data = data.reset_index().rename(columns={'index': 'date'})
    data = data[data.date.between(*dates)]
    data = data.set_index('date')

    years = range(yy[0], yy[0]+1)

    ax = plt.axes()
    ax.set_ylabel(r'$\%$', rotation='horizontal', fontsize=14, labelpad=15)
    for i in range(0, 3):
        ax.plot(data.index.values, data.iloc[:, i].values)

    ax.set_ylim(ylim)
    ax.set_xlim(dates)

    events = [pd.to_datetime(x) for x in ['3/9/2023', '5/1/2023']]
    ymin, ymax = ax.get_ylim()


    # if hprices is not None:
    #     ax2 = ax.twinx()
    #     ax2.plot(hprices, color='red')
    #     ax2.set_ylim([150, 350])
    #     # ax2.legend(["Case-Shiller Nat'l Home Price Idx"], edgecolor='w')
    #     # ax.legend(['30y Mortgage', '10y Treasury', 'Federal Funds Rate', 'C-S Home Price Idx'],
    #     #           edgecolor='w')
    #     plt.figlegend(handles=ax.lines+ax2.lines,
    #                   loc='upper left', fancybox=True, framealpha=1,
    #                   shadow=True, borderpad=1)
    # else:
    #     # ax.legend(['30y Mortgage', '10y Treasury', 'Federal Funds Rate'], edgecolor='w')
    #     plt.figlegend(handles=ax.lines,
    #                   loc='upper left', fancybox=True, framealpha=1,
    #                   shadow=True, borderpad=1)

    ax.vlines(events, ymin, ymax, colors='0.8')
    plt.tight_layout()

if __name__ == "__main__":
    # etf_path = "data/bank_and_sp500_returns_501.csv"
    # eventnum = 'all'
    # stocks = event_stock_returns(etf_path, eventnum)

    fred_plots()

    plt.show()
    plt.close('all')