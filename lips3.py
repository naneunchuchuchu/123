import time
import pyupbit
import datetime
import requests

access = ""     # access key
secret = ""     # secret key
myToken = ""

def post_message(token, channel, text):
    """슬랙 메시지 전송"""
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
op_mode = False # 거래 여부
hold = False # 코인 보유 여부

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
post_message(myToken,"#xrp-auto", "autotrade start")

# 잔고 조회
xrp_balance = upbit.get_balance("KRW-XRP")
xrp_price = pyupbit.get_current_price("KRW-XRP")
while True:
    try:
        now = datetime.datetime.now()

        # 매도 시도
        if now.hour == 9 and now.minute == 59 and 50 <= now.second <= 59:
            if op_mode is True and hold is True :
                xrp_balance = upbit.get_balance("KRW-XRP")
                sell_result = upbit.sell_market_order("KRW-XRP", xrp_balance*0.9995)
                post_message(myToken,"#xrp-auto", "XRP sell : " +str(sell_result))
                hold = False
            op_mode = False
            time.sleep(10)
        
        # 10:00:00 목표가 갱신
        if now.hour == 10 and now.minute == 0 and 20 <= now.second <=30:
            target = cal_target("KRW-XRP")
            op_mode=True
            time.sleep(10)
        
        price = pyupbit.get_current_price("KRW-XRP")

        # 매초마다 조건을 확인한 후 매수 시도
        if op_mode is True and hold is False and price >= target and price is not None:
            # 매수
            krw_balance = upbit.get_balance("KRW")
            buy_result = upbit.buy_market_order("KRW-XRP",krw_balance*0.9995)
            post_message(myToken,"#xrp-auto", "XRP buy : " +str(buy_result))
            hold = True
    except Exception as e:
        print(e)
        post_message(myToken,"#xrp-auto", e)
        time.sleep(1)

    #상태 출력
    print(f"현재 시간: {now} 목표가: {target} 현재가: {price} 보유상태: {hold} 동작상태: {op_mode}")
    time.sleep(1)