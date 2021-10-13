import time
import pyupbit
import datetime
import requests

access = ""
secret = ""
myToken = ""

def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

def cal_target(ticker):
    df=pyupbit.get_ohlcv(ticker,"day")
    yesterday = df.iloc[-2]
    today = df.iloc[-1]
    yesterday_range = yesterday['high'] - yesterday['low']
    target = today['open'] + yesterday_range * 0.5
    return target

target = cal_target("KRW-XRP")
op_mode = False
hold = False

upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
post_message(myToken,"#xrp-auto", "autotrade start")

xrp_balance = upbit.get_balance("KRW-XRP")
xrp_price = pyupbit.get_current_price("KRW-XRP")
while True:
    try:
        now = datetime.datetime.now()

        if now.hour == 9 and now.minute == 59 and 50 <= now.second <= 59:
            if op_mode is True and hold is True :
                xrp_balance = upbit.get_balance("KRW-XRP")
                sell_result = upbit.sell_market_order("KRW-XRP", xrp_balance*0.9995)
                hold = False
            op_mode = False
            post_message(myToken,"#xrp-auto", "XRP sell : " +str(sell_result))
            time.sleep(10)
        if now.hour == 10 and now.minute == 0 and 20 <= now.second <=30:
            target = cal_target("KRW-XRP")
            op_mode=True
            time.sleep(10)
        price = pyupbit.get_current_price("KRW-XRP")
        if op_mode is True and hold is False and price >= target and price is not None:
            krw_balance = upbit.get_balance("KRW")
            buy_result = upbit.buy_market_order("KRW-XRP",krw_balance*0.9995)
            hold = True
            post_message(myToken,"#xrp-auto", "XRP buy : " +str(buy_result))
    except Exception as e:
        print(e)
        time.sleep(1)

    print(f"현재 시간: {now} 목표가: {target} 현재가: {price} 보유상태: {hold} 동작상태: {op_mode}")
    time.sleep(1)