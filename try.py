
import yfinance as yf

from configs import macro_cfg
from core.stock import Stock
from core.macros import MacroEconomic
from core.valuation import Valuation
from core.evaluation import Evaluator

#Get the stock data and price series from yfinance
ticker = "AAPL"
t = yf.Ticker(ticker)
p = yf.download(tickers=[ticker], interval="1d", period="10y")

# Establish the stock object and get the payload.
stock = Stock(t, p)
stock_payload = stock.to_payload()

# Conduct the valuation and get the payload.
val = Valuation(stock)
fair_value_payload = val.valuate()

# Conduct the Macroeconomics evaluation using the World Bank API.
country = stock.country
macros = MacroEconomic(macro_cfg['base_currency_country'], country, macro_cfg['macro_years'])

# Conduct the 6-category evaluation and get the payload.
eva = Evaluator(stock, macros)
evaluation_payload = eva.run_all()

print(0)









