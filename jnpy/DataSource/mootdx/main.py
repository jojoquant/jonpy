
from mootdx.quotes import Quotes

if __name__ == '__main__':
    client = Quotes.factory('ext')
    df = client.markets()
    print(1)
