
import yfinance as yf

from configs import macro_cfg
from core.stock import Stock
from core.macros import MacroEconomic
from core.valuation import Valuation
from core.evaluation import Evaluator

#build a streamlit app to display stock, fair_value_payload, and evaluation_payload.
ticker = "AAPL"
t = yf.Ticker(ticker)
p = yf.download(tickers=[ticker], interval="1d", period="10y")

stock = Stock(t, p)
stock_payload = stock.to_payload()


val = Valuation(stock)
fair_value_payload = val.valuate()

country = stock.country
macros = MacroEconomic(macro_cfg['base_currency_country'], country, macro_cfg['macro_years'], macro_cfg["fx_years"], macro_cfg["ca_years"], macro_cfg["inflation_years"])
macro_payload = macros.to_payload()

eva = Evaluator(stock, macros)
evaluation_payload = eva.run_all()









