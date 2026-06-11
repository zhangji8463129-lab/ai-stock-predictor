import pandas as pd
import requests
import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# =====================
# Stooq稳定数据源
# =====================

def get_stooq(symbol):
    try:
        url = f"https://stooq.com/q/d/l/?s={symbol}&i=d"
        df = pd.read_csv(url)

        if df is None or df.empty:
            return None, None

        return float(df["Close"].iloc[-1]), float(df["Close"].iloc[-2])
    except:
        return None, None

# =====================
# Yahoo备用源
# =====================

def get_yahoo(ticker):
    try:
        df = yf.Ticker(ticker).history(period="2d")
        if df is None or df.empty or len(df) < 2:
            return None, None
        return float(df["Close"].iloc[-1]), float(df["Close"].iloc[-2])
    except:
        return None, None

# =====================
# 安全兜底
# =====================

def safe(v):
    return v if v is not None else 0

# =====================
# 数据层（V8.1核心）
# =====================

def get_data():
    data = {}

    # ===== 指数类（Stooq稳定）=====
    data["vix"] = get_stooq("vix")
    data["tnx"] = get_stooq("tnx")
    data["nasdaq"] = get_stooq("ndx")

    # ===== AI股票（Yahoo优先）=====
    data["nvda"] = get_yahoo("NVDA")
    data["amd"] = get_yahoo("AMD")
    data["avgo"] = get_yahoo("AVGO")

    return data

# =====================
# 涨跌幅
# =====================

def change(cur, prev):
    cur, prev = safe(cur), safe(prev)
    if prev == 0:
        return 0
    return (cur - prev) / prev * 100

# =====================
# AI强度
# =====================

def ai_strength(data):
    scores = [
        change(*data["nvda"]),
        change(*data["amd"]),
        change(*data["avgo"]),
    ]

    avg = sum(scores) / len(scores)

    if avg > 1:
        return "强"
    elif avg < -1:
        return "弱"
    return "中性"

# =====================
# 风险系统（稳定版）
# =====================

def risk_check(data):
    risk = 0

    vix = data["vix"]
    tnx = data["tnx"]

    vix_now, vix_prev = safe(vix[0]), safe(vix[1])
    tnx_now, tnx_prev = safe(tnx[0]), safe(tnx[1])

    if vix_now > vix_prev:
        risk += 1

    if tnx_now > tnx_prev:
        risk += 1

    if ai_strength(data) == "弱":
        risk += 2

    if risk >= 3:
        return "高风险"
    elif risk == 2:
        return "中风险"
    return "低风险"

# =====================
# 周趋势
# =====================

def weekly_trend(data):
    ndx = data["nasdaq"]

    if ndx is None or ndx[0] is None:
        return "震荡周"

    ma5 = ndx[0]
    ma10 = sum([x for x in ndx if x]) / len(ndx)

    if ma5 > ma10:
        return "进攻周"
    return "防守周"

# =====================
# 决策
# =====================

def decision(prob, risk, strength):
    if risk == "高风险":
        return "❌ 空仓"

    if prob > 75 and strength == "强":
        return "🔥 重仓（70-90%）"

    if prob > 65:
        return "🟡 中仓（40-60%）"

    if prob > 55:
        return "⚖️ 轻仓（20-40%）"

    return "❌ 观望"

# =====================
# 概率模型
# =====================

def predict(data):
    score = 0

    vix = data["vix"]
    tnx = data["tnx"]

    vix_now = safe(vix[0])
    vix_prev = safe(vix[1])

    tnx_now = safe(tnx[0])
    tnx_prev = safe(tnx[1])

    if vix_now < 18:
        score += 2
    elif vix_now > 22:
        score -= 2

    if tnx_now < tnx_prev:
        score += 2
    else:
        score -= 1

    strength = ai_strength(data)

    if strength == "强":
        score += 3
    elif strength == "弱":
        score -= 3

    prob = 50 + score * 7
    prob = max(10, min(90, prob))

    return prob, strength

# =====================
# 报告
# =====================

def report(prob, data, risk, action):
    return f"""
AI交易系统 V8.1（稳定数据版）

【核心结果】
上涨概率：{prob}%
风险等级：{risk}

【AI强度】
{ai_strength(data)}

【关键数据】
NVDA：{data['nvda']}
AMD：{data['amd']}
AVGO：{data['avgo']}

VIX：{data['vix']}
美债：{data['tnx']}

【最终决策】
{action}
"""

# =====================
# 邮件
# =====================

def send_email(content):
    sender = "1024158718@qq.com"
    password = "flpfjztznvbbbbdb"
    receiver = "1024158718@qq.com"

    msg = MIMEText(content, "plain", "utf-8")
    msg["Subject"] = "AI交易系统 V8.1"
    msg["From"] = sender
    msg["To"] = receiver

    server = smtplib.SMTP_SSL("smtp.qq.com", 465)
    server.login(sender, password)
    server.sendmail(sender, receiver, msg.as_string())
    server.quit()

# =====================
# 主程序
# =====================

if __name__ == "__main__":
    data = get_data()

    prob, strength = predict(data)
    risk = risk_check(data)
    action = decision(prob, risk, strength)

    content = report(prob, data, risk, action)

    print(content)
    send_email(content)



       

