import sys
from PyQt5.QtWidgets import QApplication
from market_data_viewer import MarketDataViewer
#Period 1 A and B is best looking for 2 stocks at once, Period 7 A is the best stock
if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = MarketDataViewer("./cache")
    viewer.show()
    sys.exit(app.exec_())

'''
sample data in TrainingData/Period3/C/market_data_C.csv:
bidVolume,bidPrice,askVolume,askPrice,timestamp
11,5043.75,27,5044.0,08:00:00.005926909
11,5043.75,27,5044.0,08:00:00.005933024


sample data in TrainingData/Period3/C/trade_data_C.csv:
price,volume,timestamp
5044.0,1,08:00:00.015534389
5043.75,2,08:00:00.037621161
'''