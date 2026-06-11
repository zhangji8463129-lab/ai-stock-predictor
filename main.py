import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# =====================
# 安全获取数据
# =====================

def get_price(ticker):
    try:
        hist = yf.Ticker(ticker).history(period="2d")
        if hist.empty or len(hist) < 2:
            return None, None
        return hist["Close"].iloc[-1], hist["Close"].iloc[-2]
    except:
        return None, None

def safe_compare(a, b):
    if a is None or b is None:
        return 0
    return a - b

# =====================
# 获取数据
# =====================

def get_data():
    data = {}

    data["nasdaq"], data["nasdaq_prev"] = get_price("^IXIC")
    data["vix"], data["vix_prev"] = get_price("^VIX")
    data["tnx"], data["tnx_prev"] = get_price("^TNX")

    data["nvda"], data["nvda_prev"] = get_price("NVDA")
    data["amd"], data["amd_prev"] = get_price("AMD")
    data["avgo"], data["avgo_prev"] = get_price("AVGO")

    return data

# =====================
# 涨跌幅
# =====================

def change(cur, prev):
    if cur is None or prev is None:
        return 0
    return (cur - prev) / prev * 100

# =====================
# AI强度
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
# 风险检测（修复版）
# =====================

def risk_check(data):
    risk = 0

    if data["vix"] and data["vix_prev"]:
        if data["vix"] > data["vix_prev"]:
            risk += 1

    if data["tnx"] and data["tnx_prev"]:
        if data["tnx"] > data["tnx_prev"]:
            risk += 1

    if ai_strength(data) == "弱":
        risk += 2

    if risk >= 3:
        return "🚨 高风险"
    elif risk == 2:
        return "⚠️ 风险"
    else:
        return "正常"

# =====================
# 趋势（容错）
# =====================

def trend():
    try:
        hist = yf.Ticker("^IXIC").history(period="5d")
        if hist.empty:
            return "未知"
        return "上升" if hist["Close"].iloc[-1] > hist["Close"].mean() else "下降"
    except:
        return "未知"

# =====================
# 周期
# =====================

def weekly_bias():
    try:
        hist = yf.Ticker("^IXIC").history(period="20d")
        if hist.empty:
            return "未知"
        return "进攻周" if hist["Close"].iloc[-1] > hist["Close"].mean() else "防守周"
    except:
        return "未知"

# =====================
# 预测
# =====================

def predict(data):
    score = 0

    if data["vix"] and data["vix"] < 18:
        score += 2
    elif data["vix"] and data["vix"] > 22:
        score -= 2

    if data["tnx"] and data["tnx_prev"]:
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
# 决策
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
# 报告
# =====================

def report(prob, data, trend_val, week, strength, risk, action):
    return f"""
AI交易系统 V6（{datetime.now().strftime('%Y-%m-%d')}）

趋势：{trend_val}
周期：{week}
风险：{risk}

概率：{prob}%
AI强度：{strength}

VIX：{data['vix']}
美债：{data['tnx']}

NVDA：{data['nvda']}
AMD：{data['amd']}
AVGO：{data['avgo']}

操作：{action}
"""

# =====================
# 邮件（加保护）
# =====================

def send_email(content):
    try:
        sender = "1024158718@qq.com"
        password = "flpfjztznvbbbbdb"
        receiver = "1024158718@qq.com"

        msg = MIMEText(content, "plain", "utf-8")
        msg["Subject"] = "AI交易 V6"
        msg["From"] = sender
        msg["To"] = receiver

        server = smtplib.SMTP_SSL("smtp.qq.com", 465)
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()

    except Exception as e:
        print("邮件发送失败:", e)

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

