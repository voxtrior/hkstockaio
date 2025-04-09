import json
import akshare as ak
import requests
from baoliusiwei import siwei
import time
import sys
from wangcode import wang




def gen_json(stockcode='601188'):


    df = ak.stock_zh_a_hist(symbol=stockcode, period="daily", start_date="20240101", end_date='20251024', adjust="qfq")
    df.rename(columns={'收盘':'close','日期':'trade_date','成交量':'amount'},inplace=True) 

    if df is None or len(df)<=2:
        return {'code':stockcode}

    df['trade_date'] = [str(i) for i in df['trade_date']]

    l = len(df)
    close = list(df['close'])
    junzhi = [sum(close[-5:])/5,sum(close[-10:])/10,sum(close[-20:])/20,sum(close[-40:])/40,sum(close[-80:])/80]
    # print(junzhi)


    # 计算 MACD
    df['EMA12'] = df['close'].ewm(span=12).mean()
    df['EMA26'] = df['close'].ewm(span=26).mean()
    df['DIFF'] = df['EMA12'] - df['EMA26']
    df['DEA'] = df['DIFF'].ewm(span=9).mean()
    df['MACD'] = 2 * (df['DIFF'] - df['DEA'])

    if len(list(df['EMA12']))==0:
        return {'code':stockcode}
    
    l = 30
    ema12 = list(df['EMA12'])[-1]
    ema26 = list(df['EMA26'])[-1]
    dea = list(df['DEA'][-l:])
    macd = list(df['MACD'][-l:])
    close = list(df['close'][-l:])
    amount = list(df['amount'][-l:])
    diff = list(df['DIFF'][-l:])

    conclusion = ""

    jsonresult = {'dea':dea,'diff':diff,'macd':macd,'close':close,'amount':amount,'code':stockcode,'trade_date':list(df['trade_date'])[-1:],
                  'junzhi':junzhi,'ema12':ema12,'ema26':ema26,'conclusion':conclusion}
    
    for i in jsonresult.keys():
        jsonresult[i] = siwei(jsonresult[i])

    return jsonresult



def judge_code(codecontent):
   
    code = codecontent['code']

    close = codecontent['close']
    minprice = min(close)
    maxprice = max(close)
    macd = codecontent['macd']

    
    # conclusion = code + ' '+ df.loc[code]['名称'] 
    conclusion = name[code]  


    t = codecontent['junzhi']
    if t[0] < t[1] and t[1] < t[2] and t[2] < t[3] and t[3] < t[4]:
        conclusion = conclusion + ' 股票5、10、20、40、80日均值一直下跌,非常不建议入手；'

    
    dea = list(codecontent['dea'])
    cha = [round(dea[i]-dea[i-1],4) for i in range(-10,0)]

    # print(dea)
    # print(cha)
    ma5 = [round(sum(close[i-5:i])/5,2) for i in range(-5,0)]
    ma5.append(round(sum(close[-5:])/5,2))
    # print(ma5)
    
    i=-1

    if (dea[i]>dea[i-1] or abs(dea[i]-dea[i-1])<0.001) and dea[i-1]<dea[i-2]  :
        conclusion = conclusion + "该建/加仓；" + str(dea[-3:]) + ";" + str()

    if  dea[-3]<dea[-2]>dea[-1]  :
        conclusion = conclusion + "该卖/减了" + str(dea[-3:]) + ";" + str()

    # if ((dea[i]>dea[i-1] or abs(dea[i]-dea[i-1])<0.001) and dea[i-1]>dea[i-2]  and (close[i]>=close[i-1]-0.02 ) ):
    #     conclusion = conclusion + "这只谷子处于上升趋势，可以一看；"
    
    
    # if ma5[-1]>ma5[-2] and macd[-1]>macd[-2] and macd[-1]<0:
    #     conclusion += '<div class=\'macd\'>此时macd正值向上，可以考虑加仓;<br/>macd:' + str(macd[-3:]) + ';<br/>   macd差值：' + str(cha[-3:]) +'</div>'

    # if dea[-1]<dea[-2] and ma5[-1]<ma5[-2] and dea[-1]>0 and macd[-1]<macd[-2]:
    #     conclusion += '<div class=\'xiadie\'>此时属于下跌趋势,建议不要加仓，观望一下</div>'

    return conclusion + "\r\n\r\n"

def send_text_message(content):

    webhook_url = "https://oapi.dingtalk.com/robot/send?access_token=f9f13340f18a82aa8a1abb8054b8714008260b54697294b60de4114c53ce45d9"
    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "text",
        "text": {"content": content+"1"}
    }
    response = requests.post(webhook_url, headers=headers, data=json.dumps(data))
    return response.json()


if __name__ == "__main__":

    # df = ak.stock_zh_a_spot_em()
    # df.sort_values(by='代码',inplace=True)
    # df.index = df['代码']
    # ll = list(df.index)



    with open('ctn.json','r+') as f:
    # print(json.loads(f.read()))
        name = json.loads(f.read())
        f.close()

    ll =list(wang)
    # ll.append("000625")
    # all_json = []
    print(ll)
    ll.sort()

    con = ""
  
    for i in ll:
        if 1 and (i.startswith('00') or i.startswith('60')):
            # print(i)
            a =  gen_json(i)
            b = judge_code(a)

            if len(b)>20:
                con = con + b
            # print(a)
            # all_json.append(a)
    
    df = ak.stock_zh_index_daily(symbol="sh000001")
    df['EMA12'] = df['close'].ewm(span=12).mean()
    df['EMA26'] = df['close'].ewm(span=26).mean()
    df['DIFF'] = df['EMA12'] - df['EMA26']
    df['DEA'] = df['DIFF'].ewm(span=9).mean()
    df['MACD'] = 2 * (df['DIFF'] - df['DEA'])
    dea = list(df['DEA'])
     
    if dea[-1]<dea[-2]:
        con = "上证指数是下降趋势\r\n\r\n" + con
    else:
        con = "上证指数是上升趋势\r\n\r\n" + con

    send_text_message(con)


    # print(judge_code(gen_json("600373")))
    # print(ll)


