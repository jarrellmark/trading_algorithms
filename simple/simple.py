from pyalgotrade import strategy
from pyalgotrade.barfeed import yahoofeed

class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instruments):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.__positions = {}
        self.__instruments = instruments
        self.__yesterday = {}
        self.__change_from_yesterday = {}
        self.__first_day = True

    def calculate_change(self, bar, instrument):
        # change_from_yesterday = (todays_price / yesterdays_price) - 1
        self.__change_from_yesterday[instrument] = (bar.getClose() / self.__yesterday[instrument]) - 1
        self.__yesterday[instrument] = bar.getClose()

    # Returns a list
    # output is a list of the keys of the max num_maxes elements
    # in descending (large to small) order
    # if dictionary.size() < num_maxes, then the list is as large as dictionary.size()
    def max_n_from_dict(self, dictionary, num_maxes):
        output = []
        self.info("      dictionary: " + str(dictionary))
        dictionary_sorted = sorted(dictionary, key=dictionary.get)
        dictionary_sorted.reverse()
        for i in range(0, num_maxes):
            if i < len(dictionary_sorted):
                output.append(dictionary_sorted[i])
            else:
                break
        self.info("      dictionary_max_n_keys: " + str(output))
        return output

    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        self.info("  Buy "+position.getEntryOrder().getInstrument()+" at $%.2f" % (execInfo.getPrice()))

    def onEnterCanceled(self, position):
        self.__postitions[position.getEntryOrder().getInstrument()] = None

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        instrument = position.getExitOrder().getInstrument()
        self.info("  Sell "+instrument+" at $%.2f" % (execInfo.getPrice()))
        self.__positions[instrument] = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        instrument = position.getExitOrder().getInstrument()
        self.__positions[instrument].exitMarket()

    def onBars(self, bars):
        if self.__first_day:
            for instrument in self.__instruments:
                bar = bars[instrument]
                self.__yesterday[instrument] = bar.getClose()
        self.info("[")
        # Close all open positions
        for instrument in self.__instruments:
            if not self.__positions.get(instrument) is None:
                self.__positions[instrument].exitMarket()
        # Calculate today's change
        for instrument in self.__instruments:
            bar = bars[instrument]
            self.info("  " + instrument + ": " + str(bar.getClose()))
            self.calculate_change(bar, instrument)
            # Set tomorrow's yesterday now
            self.__yesterday[instrument] = bar.getClose()
        # Get max 5 movers from yesterday
        max_change = self.max_n_from_dict(self.__change_from_yesterday, 5)
        # Buy 10 shares of each biggest market mover from yesterday
        for instrument in max_change:
            self.__positions[instrument] = self.enterLong(instrument, 10, True)
        self.info("]")
        self.__first_day = False

# Stocks
stocks = []
stocks.append("AXP")
stocks.append("BA")
stocks.append("CAT")
stocks.append("CSCO")
stocks.append("CVX")
stocks.append("DD")
stocks.append("DIS")
stocks.append("GE")
stocks.append("GS")
stocks.append("HD")
stocks.append("IBM")
stocks.append("INTC")
stocks.append("JNJ")
stocks.append("JPM")
stocks.append("KO")
stocks.append("MCD")
stocks.append("MMM")
stocks.append("MRK")
stocks.append("MSFT")
stocks.append("NKE")
stocks.append("PFE")
stocks.append("PG")
stocks.append("T")
stocks.append("TRV")
stocks.append("UNH")
stocks.append("UTX")
#stocks.append("V")
stocks.append("VZ")
stocks.append("WMT")
stocks.append("XOM")

# Load the yahoo feed from the CSV file
feed = yahoofeed.Feed()
for stock in stocks:
    feed.addBarsFromCSV(stock, "data/"+stock+"-2008.csv")

# Evaluate the strategy with the feed's bars.
myStrategy = MyStrategy(feed, stocks)
starting = myStrategy.getBroker().getEquity()
myStrategy.run()
ending = myStrategy.getBroker().getEquity()
print "Starting portfolio value: $%.2f" % starting
print "Final portfolio value: $%.2f" % ending
final = ((ending - starting) / starting) * 100
print "Final gain: %.2f percent" % final
