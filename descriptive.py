import pandas as pd
from matplotlib import pyplot as plt

def event_stock_returns(fpath, eventnum):
    stocks = pd.read_csv("data/bank_and_sp500_returns_501.csv")
    stocks.loc[stocks.dividend.isnull(), 'dividend'] = 0
    stocks.price += stocks.dividend
    stocks = stocks[['date', 'ticker', 'price']]
    stocks.date = pd.to_datetime(stocks.date)

    # Dates for normalization and sample
    if eventnum == 1:
        event_date = pd.to_datetime("3/9/23")
        dates = [pd.to_datetime("1/1/23"), pd.to_datetime("5/1/23")]
        months = [1, 2, 3, 4]
        plot_ylims = [80, 120]
    elif eventnum == 2:
        event_date = pd.to_datetime("5/1/23")
        dates = [pd.to_datetime("4/1/23"), pd.to_datetime("7/1/23")]
        months = [4, 5, 6]
        plot_ylims = [85, 110]

    stocks_pre_event = stocks[stocks.date == event_date]
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
        axes[i].axvline(x=event_date, color='0.5', linestyle='--')
        axes[i].set_xticks(tick_daterange, tick_labels)
        axes[i].set_ylim(plot_ylims)

    axes[0].set_title('S&P 500')
    axes[1].set_title('SPDR Banking ETF')

    plt.tight_layout()
    fig.set_size_inches(6.4, 4)
    fig.savefig(f'temp/index_stock_prices_event{eventnum}.png', dpi=100)

    return stocks


if __name__ == "__main__":
    etf_path = "data/bank_and_sp500_returns_501.csv"
    eventnum = 1
    stocks = event_stock_returns(etf_path, eventnum)

    plt.show()