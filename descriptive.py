import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import numpy as np
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
    fig.set_size_inches(6.4, 3)
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

    data = pd.concat((rmort30, t10), axis=1)

    plt.rc('font', size=15)

    # Interest rates
    yy = [2021, 2024]
    ylim = [0, 8]
    rates_plot(data, yy, ylim)
    plt.savefig('output/interest_rates.png')

    # Home prices

    return None

def rates_plot(data, yy, ylim):
    dates = [pd.to_datetime(x) for x in [f'1/1/{yy[0]}', f'1/1/{yy[1]}']]
    data = data.reset_index().rename(columns={'index': 'date'})
    data = data[data.date.between(*dates)]
    data = data.set_index('date')

    years = range(yy[0], yy[0]+1)

    ax = plt.axes()
    ax.set_ylabel(r'$\%$', rotation='horizontal', fontsize=14, labelpad=15)
    for i in range(0, 2):
        ax.plot(*splitSerToArr(data.iloc[:, i].dropna()))

    ax.set_ylim(ylim)
    ax.set_xlim(dates)

    events = [pd.to_datetime(x) for x in ['3/9/2023', '5/1/2023']]
    ymin, ymax = ax.get_ylim()

    ax.legend(['30y Mortgage Rate', '10y Treasury Yield'], edgecolor='w',
              framealpha=0.2)
    ax.set_xticks([pd.to_datetime(f'1/1/{y}') for y in range(yy[0], yy[1]+1)],
                  [f'Jan-{y}' for y in range(yy[0], yy[1]+1)])

    ax.vlines(events, ymin, ymax, colors='0.6', linestyles='dashed')
    plt.tight_layout()
    # plt.figlegend(handles=ax.lines, loc='upper left', fancybox=True, framealpha=1,
    #               shadow=True, borderpad=1)


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

def wloc_capacity_plot(fpath):
    plt.rc('font', size=15)
    data = pd.read_csv(fpath)
    data['date'] = pd.to_datetime(data.ddate)

    ax = plt.axes()
    ax.plot(data['date'], data.capacity * 100)
    # ax.tick_params(axis='x', labelrotation=30)

    n = data['date'].values.shape[0]
    xticks = data['date'].iloc[3:n+1:4].tolist()
    xticks.insert(0, pd.to_datetime('12/31/2018'))
    # xticks.append(pd.to_datetime('12/31/2024'))
    ax.set_xticks(xticks, list(range(2019, 2025)))
    ax.set_xlim([pd.to_datetime('12/31/2018'), pd.to_datetime('1/1/2024')])
    # ax.set_ylabel(r'$\%$', rotation='horizontal', fontsize=14, labelpad=15)
    ax.set_ylabel(r'$\%$ credit limit remaining')
    plt.tight_layout()

    plt.savefig('output/wloc_capacity_time_series.png')

    return ax

def splitSerToArr(ser):
    return [ser.index, ser.values]

def nb_balance_sheets():
    data = pd.read_excel('data/mcr/liabilities.xlsx')
    dates = pd.date_range('01-01-2012', '10-01-2022', freq='QS')
    dates = dates.drop(pd.to_datetime('10-01-2018'))

    assets = data['Assets']
    order = ['Debt_Facilities', 'Other_ST', 'LT', 'Equity']
    data = data[order]
    for var in order:
        data[var] = data[var] / assets
    data = data.set_index(dates)

    # Plot
    plt.rc('font', size=11)

    fig = plt.figure(figsize=(5.5, 3))
    ax = fig.add_subplot(111)

    # Modify colormap with an alpha value of 0.3
    new_cmap = modify_colormap_alpha(plt.get_cmap('jet'), 0.76)

    ax = data.plot.area(ax=ax, colormap=new_cmap)

    leg = plt.legend(ax.lines[4::-1],
              ['Equity', 'Long Term Debt',
               'Other Short Term Debt', 'Debt Facilities'],
              framealpha=1)
    for legobj in leg.legendHandles:
        legobj.set_linewidth(4.0)

    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y'))
    plt.gca().xaxis.set_major_locator(plt.matplotlib.dates.YearLocator(2, 1, 1))
    plt.xticks(rotation=0, ha='center')
    ax.tick_params('x', pad=5)
    # ax.set_xticks()
    # plt.gcf().autofmt_xdate()
    ax.set_xlim([dates[0], dates[-1]])
    ax.set_ylim([0, 1])
    ax.set_ylabel('Share of assets')
    plt.tight_layout()
    fig = plt.gcf()
    plt.savefig('output/balance_sheet_time_series.png')

    return ax

# Create a function to modify the alpha of a colormap
def modify_colormap_alpha(cmap, alpha):
    # Create a new colormap by modifying the alpha channel
    colors = cmap(np.arange(cmap.N))
    # Modify the alpha channel (last column)
    colors[:, -1] = alpha
    new_cmap = mcolors.ListedColormap(colors)
    return new_cmap

def bank_lines_histogram():
    data = pd.read_excel('data/bank_numlines_2022q4.xlsx')

    plt.rc('font', size=11)
    fig = plt.figure(figsize=(5, 3))
    ax = fig.add_subplot(111)
    ax.hist(data, bins=25, rwidth=0.75)
    ax.set_ylabel('Frequency (# banks)')
    ax.set_xlabel('Number of credit lines provided')
    ax.set_yticks(range(0, 21, 5))
    ax.set_xlim((0, 70))
    plt.tight_layout()
    plt.savefig('output/bank_lines_histogram.png')

    return data

if __name__ == "__main__":
    etf_path = "data/bank_and_sp500_returns_501.csv"
    eventnum = 'all'
    # stocks = event_stock_returns(etf_path, eventnum)

    # fred_plots()
    # ax = wloc_capacity_plot('output/mcr_wloc_capacity_series.csv')

    # ax = nb_balance_sheets()
    data = bank_lines_histogram()

    plt.show()
    # plt.close('all')