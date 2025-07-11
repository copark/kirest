
class Stock:
    def __init__(self, market, code, name):
        self.market = market
        self.code = code
        self.name = name

    def __repr__(self):
        return f"Stock(market='{self.market}', code='{self.code}', name='{self.name}')"
    


class StockList:
    def __init__(self):
        self.stocks = []

    def add(self, stock):
        self.stocks.append(stock)

    def find_by_code(self, code):
        for stock in self.stocks:
            if stock.code == code:
                return stock
        return None
    
    def find_by_name(self, name):
        for stock in self.stocks:
            if stock.name == name:
                return stock
        return None

    def list_all(self):
        return self.stocks
