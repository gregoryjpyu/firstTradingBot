import krakenex
import json
import time
import datetime
import calendar

#open High Low Close; pair is the crypto pair, since is the timeframe
def get_crypto_data(pair,since):
    return api.query_public("OHLC", data={'pair': pair, 'since': since})["result"][pair]

def analyze(pair, since):
    data = get_crypto_data(pair[0]+pair[1], since)

    lowest = 0
    highest = 0

    for prices in data:
        balance = get_fake_balance()
        last_trade = get_last_trade(pair[0]+pair[1])
        price_last_trade = float(last_trade["price"])

        open_ = float(prices[1])
        high_ = float(prices[2])
        low_ = float(prices[3])
        close_ = float(prices[4])

        did_sell = False

        try:
            #if we own any of the pair currency that we are looking then check sell
            balance[pair[0]]
            selling_point_win = price_last_trade * 1.000005
            selling_point_loss = price_last_trade * 0.999995

            #take profit
            if open_ >= selling_point_win or close_ >= selling_point_win:
                print("win")
                #sell at a profit
                did_sell = True
                fake_sell(pair, close_, last_trade)
            elif open_ <= selling_point_loss or close_ <= selling_point_loss:
                #sell at a loss
                did_sell = True
                fake_sell(pair, close_, last_trade)
                print("loss")
        except:
            pass


        #print("run else code")
        #logic for if we should buy
        if not did_sell and float(balance["USD.HOLD"]) > 0:
            avaliable_money = balance["USD.HOLD"]
            fake_buy(pair, avaliable_money, close_, last_trade)

def fake_update_balance(pair, dollar_amount, close_, was_sold):
    balance = get_fake_balance()
    prev_balance = float(balance["USD.HOLD"])
    if was_sold:
        new_balance = prev_balance + float(dollar_amount)
        del balance[pair[0]]

    else:
        new_balance = prev_balance - float(dollar_amount)
        balance[pair[0]] = str(float(dollar_amount)/close_)

    balance["USD.HOLD"] = str(new_balance)
    with open("balance.json", "w") as f:
        json.dump(balance, f, indent=4)

def fake_buy(pair, dollar_amount, close_, last_trade):
    #api.query_private() real buy look up
    trades_history = get_fake_tradeshistory()
    last_trade["price"] = str(close_)
    last_trade["type"] = "buy"
    last_trade["cost"] = dollar_amount
    last_trade["time"] = datetime.datetime.now().timestamp()
    last_trade["vol"] = str(float(dollar_amount)/close_)

    trades_history[str(datetime.datetime.now().timestamp())] = last_trade
    with open("tradeshistory.json", "w") as f:
        json.dump(trades_history, f, indent = 4)
        fake_update_balance(pair, dollar_amount, close_, False)

def fake_sell(pair, close_, last_trade):
    trades_history = get_fake_tradeshistory()
    last_trade["price"] = str(close_)
    last_trade["type"] = "sell"
    last_trade["cost"] = str(float(last_trade["vol"])*close_)
    last_trade["time"] = str(datetime.datetime.now().timestamp())
    dollar_amount = str(float(last_trade["vol"])*close_)
    trades_history[str(datetime.datetime.now().timestamp())] = last_trade
    with open("tradeshistory.json", "w") as f:
        json.dump(trades_history, f, indent=4)
        fake_update_balance(pair, dollar_amount, close_, True)






def get_balance():
    return api.query_private("Balance") #["result"] when you have no money!!!!!!!!!!!!!!!!!!!!!!!!!!

def get_fake_balance():
    with open("balance.json", "r") as f:
        return json.load(f)

def get_fake_tradeshistory():
    with open("tradeshistory.json", "r") as f:
        return json.load(f)

#get last trade of this pair
def get_last_trade(pair):
    trades_history = get_fake_tradeshistory()
    last_trade = {}

    for trade in trades_history:
        distrade = trades_history[trade]
        if distrade["pair"] == pair and distrade["type"] == "buy":
            last_trade = distrade
    return last_trade
def get_trades_history():
    start_date = datetime.datetime(2021, 7, 4)
    end_date = datetime.datetime.today()
    return api.query_private("TradesHistory", req(start_date, end_date, 1))["result"]["trades"]

def date_nix(str_date):
    return calendar.timegm(str_date.timetuple())

def req(start, end, ofs):
    req_data = {
        "type": "all",
        "trades": "true",
        "start": str(date_nix(start)),
        "end": str(date_nix(end)),
        "ofs": str(ofs)
    }
    return req_data

if __name__ == "__main__":
    api = krakenex.API()
    api.load_key("kraken.key")
    pair = ("XETH", "ZUSD")  #etherum vs usd
    since = str(int(time.time() - 3600)) #look at time since 1 hour ago
    analyze(pair, since)
    #print(json.dumps(get_crypto_data(pair, since), indent=4))
    #print(json.dumps(get_balance(), indent=4))
    #print(json.dumps(get_trades_history(), indent=4))
    #print(json.dumps(get_fake_balance(), indent=4))
    #print(json.dumps(get_fake_tradeshistory(), indent=4))






