import yfinance as yf
try:
    from StockMonitor import StockMonitor
except:
    from .StockMonitor import StockMonitor
import asyncio
from datetime import datetime, timedelta
import logging
from time import sleep
import threading


class YStockMonitor(StockMonitor):
    @staticmethod
    def getPrice(symbol, handlers, debug=False):
        if debug:
            start_date = datetime.now() - timedelta(days=8)
        else:
            start_date = datetime.now() - timedelta(days=1)
        data = yf.download(
            tickers=symbol,
            start=start_date,
            group_by="ticker",
            auto_adjust=False,
            progress=False,
        )
        if len(data):
            price = data["Close"].iloc[-1]
            for h in handlers:
                h.notify(price)
        # Update data every 30 seconds
        sleep(30)
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.call_soon(YStockMonitor.getPrice,symbol,handlers,debug)

    def _monitor(self) -> None:
        self._log.info("start monitor")
        self.loop = asyncio.new_event_loop()
        self.loop.call_soon(
            YStockMonitor.getPrice, self.symbol, self.handlers, self.debug
        )
        self.loop.run_forever()

    def monitor(self):
        self._run_thread = threading.Thread(target=self._monitor)
        self._run_thread.start()

    def quit(self) -> None:
        self.loop.stop()
        if self._run_thread:
            self._run_thread.join()


if __name__ == "__main__":
    log = logging.getLogger("main")
    log.setLevel(logging.DEBUG)
    stock = YStockMonitor("2454.tw")
    stock.setDebug()
    stock.monitor()
    log.info("quit")
    sleep(3 * 30)
    log.info("quit")
    stock.quit()
    pass