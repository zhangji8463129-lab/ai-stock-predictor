import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# =====================
# 获取数据
# =====================

def get_price(ticker):
    try:
        hist = yf.Ticker(ticker).history(period="2d")
        return hist["Close"].iloc[-1], hist["Close"].iloc[-2]
    except:
        return None, None

def get_data():
    data = {}

    # 指数
    data["nasdaq"], data["nasdaq_prev"] = get_price("^IXIC")
    data["vix"], data["vix_prev"] = get_price("^VIX")
    data["tnx"], data["tnx_prev"] = get_price("^TNX")

    # AI核心股
    data["nvda"], data["nvda_prev"] = get_price("NVDA")
    data["amd"], data["amd_prev"] = get_price("AMD")
    data["avgo"], data["avgo_prev"] = get_price("AVGO")

    return data

# =====================
# 工具函数
# =====================

def change(cur, prev):
    if cur and prev:
        return (cur - prev) / prev * 100
    return 0

# =====================
# AI板块强度
# =====================

def ai_strength(data):
    scores = [
        change(data["nvda"], data["nvda_prev"]),
        change(data["amd"], data["amd_prev"]),
        change(data["avgo"], data["avgo_prev"]),
    ]
    avg = sum(scores) / len(scores)

    if avg > 1:
        return "强"
    elif avg < -1:
        return "弱"
    else:
        return "中性"

# =====================
# 风险检测（关键）
# =====================

def risk_check(data):
    risk = 0

    # VIX上升
    if data["vix"] > data["vix_prev"]:
        risk += 1

    # 美债上升
    if data["tnx"] > data["tnx_prev"]:
        risk += 1

    # AI走弱
    if ai_strength(data) == "弱":
        risk += 2

    if risk >= 3:
        return "🚨 高风险"
    elif risk == 2:
        return "⚠️ 风险"
    else:
        return "正常"

# =====================
# 趋势 + 周期
# =====================

def trend():
    hist = yf.Ticker("^IXIC").history(period="5d")
    if hist["Close"].iloc[-1] > hist["Close"].mean():
        return "上升"
    else:
        return "下降"

def weekly_bias():
    hist = yf.Ticker("^IXIC").history(period="20d")
    if hist["Close"].iloc[-1] > hist["Close"].mean():
        return "进攻周"
    else:
        return "防守周"

# =====================
# 决策引擎（核心）
# =====================

def decision(prob, risk, strength):
    if risk == "🚨 高风险":
        return "❌ 空仓/观望"

    if prob > 70 and strength == "强":
        return "🔥 加仓"

    if prob > 60:
        return "🟡 小仓位"

    return "⚖️ 观望"

# =====================
# 概率模型
# =====================

def predict(data):
    score = 0

    if data["vix"] < 18:
        score += 2
    elif data["vix"] > 22:
        score -= 2

    if data["tnx"] < data["tnx_prev"]:
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

def report(prob, data, trend_val, week, strength, risk, action):
    return f"""
AI终极交易决策系统（{datetime.now().strftime('%Y-%m-%d')}）

【市场结构】
趋势：{trend_val}
周期：{week}

【风险评估】
风险等级：{risk}

【核心判断】
上涨概率：{prob}%
AI板块：{strength}

【关键数据】
VIX：{data['vix']}
美债：{data['tnx']}

NVDA：{data['nvda']}
AMD：{data['amd']}
AVGO：{data['avgo']}

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
    msg["Subject"] = "AI交易决策 V6"
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
    trend_val = trend()
    week = weekly_bias()

    prob, strength = predict(data)
    risk = risk_check(data)
    action = decision(prob, risk, strength)

    content = report(prob, data, trend_val, week, strength, risk, action)

    print(content)
    send_email(content)
