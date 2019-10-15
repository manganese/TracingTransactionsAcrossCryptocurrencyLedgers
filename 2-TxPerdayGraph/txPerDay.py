__author__ = 'haaroony'
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

def main():
    plt.cla()
    plt.clf()
    font = {'family': 'normal',
            'weight':'normal',
            'size': 16}
    matplotlib.rc('font', **font)
    mainCurrencies = ['BTC', 'BCH', 'DOGE', 'ETH',
                      'ETC', 'DASH', 'ZEC', 'LTC']
    print("Creating line graph")
    # read csv
    rows = pd.read_csv('final.csv')
    small = rows[['timestamp', 'curIn']]
    small = small.sort_values(by='timestamp')
    counts = {}
    # compute the totals
    for row in small.itertuples():
        date = datetime.datetime.fromtimestamp(row.timestamp)
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        curin = row.curIn
        if 'Total' in counts:
            if date in counts['Total']:
                counts['Total'][date] += 1
            else:
                counts['Total'][date] = 1
        else:
            counts['Total'] = {}
            counts['Total'][date] = 1
        if curin in mainCurrencies:
            if curin in counts:
                if date in counts[curin]:
                    counts[curin][date] += 1
                else:
                    counts[curin][date] = 1
            else:
                counts[curin] = {}
                counts[curin][date] = 1

    ax = plt.subplot(111)
    ax.set_xlabel("Date")
    ax.set_ylabel("Number of transactions (thousands)")

    # hard coded so i could manually order the legend
    line_total, = ax.plot(counts['Total'].keys(),
                          counts['Total'].values(),
                            label='Total')

    line_BCH, =  ax.plot(counts['BCH'].keys(),
                            counts['BCH'].values(),
                            label='BCH')
    line_BTC, =  ax.plot(counts['BTC'].keys(),
                            counts['BTC'].values(),
                            label='BTC')
    line_DASH, = ax.plot(counts['DASH'].keys(),
                            counts['DASH'].values(),
                            label='DASH')
    line_DOGE, = ax.plot(counts['DOGE'].keys(),
                            counts['DOGE'].values(),
                            label='DOGE')
    line_ETC, = ax.plot(counts['ETC'].keys(),
                            counts['ETC'].values(),
                            label='ETC')
    line_ETH, = ax.plot(counts['ETH'].keys(),
                            counts['ETH'].values(),
                            label='ETH')
    line_LTC, = ax.plot(counts['LTC'].keys(),
                            counts['LTC'].values(),
                            label='LTC')
    line_ZEC, = ax.plot(counts['ZEC'].keys(),
                            counts['ZEC'].values(),
                            label='ZEC')

    ax.get_yaxis().set_major_formatter(
        ticker.FuncFormatter(lambda y, p: int(y/1000)))

    price = pd.read_csv('btcclose-27-11-2017-22-12-2018.csv')
    price = price.reindex(index=price.index[::-1])
    date = list(price.date.to_dict().values())
    dates = [datetime.datetime.strptime(d, '%b %d %Y') for d in date]
    ax2 = ax.twinx()
    color = 'black'
    ax2.set_ylabel('BTC price (USD)', color=color)
    line_price, = ax2.plot(dates, price['close'], 'r--', label='BTC price')
    ax2.tick_params(axis='y', labelcolor=color)
    ax.axvline(x=datetime.datetime(2018, 10, 1, 0, 0),linestyle='--',color='black')
    ax.legend(handles=[ line_price,
                        line_total,
                        line_ETH,
                        line_BTC,
                        line_LTC,
                        line_BCH,
                        line_DOGE,
                        line_DASH,
                        line_ETC,
                        line_ZEC,
    ],loc='upper right')
    # plt.tight_layout()
    plt.xlim(
        xmin=dates[0],  # the one that doesn't change
        xmax=dates[-2]  # the latest datetime in your dataset
    )

    # plt.locator_params(numticks=12)
    # fig, ax = plt.subplots()
    # months = mdates.MonthLocator()
    # monthsFmt = mdates.DateFormatter('%m-%y')
    # ax.xaxis_date()
    # ax.xaxis.set_major_formatter(monthsFmt)
    # ax.xaxis.set_major_locator(months)
    # ax.xaxis.set_major_formatter(monthsFmt)
    # fig.autofmt_xdate()
    plt.show()
    #plt.savefig('total_counts_line.png')





if __name__ == '__main__':
    main()

