import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# =====================
# 1. 获取市场数据
# =====================

def get_data():
    nasdaq = yf.Ticker("^IXIC").history(period="1d")
    sp500 = yf.Ticker("^GSPC").history(period="1d")
    vix = yf.Ticker("^VIX").history(period="1d")
    tnx = yf.Ticker("^TNX").history(period="1d")

    data = {
        "nasdaq": nasdaq["Close"].iloc[-1],
        "sp500": sp500["Close"].iloc[-1],
        "vix": vix["Close"].iloc[-1],
        "tnx": tnx["Close"].iloc[-1],
    }

    return data

# =====================
# 2. 简单AI判断逻辑
# =====================

def predict(data):
    score = 0

    # VIX低 → 加分
    if data["vix"] < 18:
        score += 2
    elif data["vix"] > 22:
        score -= 2

    # 美债收益率低 → 利好科技
    if data["tnx"] < 4:
        score += 2
    else:
        score -= 1

    # 简单概率映射
    prob = 50 + score * 10
    prob = max(10, min(90, prob))

    return prob

# =====================
# 3. 生成报告
# =====================

def generate_report(prob, data):
    action = "观望"
    if prob > 70:
        action = "加仓"
    elif prob > 60:
        action = "小幅加仓"
    elif prob < 50:
        action = "谨慎/减仓"

    report = f"""
AI美股盘前预测报告（{datetime.now().strftime('%Y-%m-%d')}）

纳指上涨概率：{prob}%

VIX指数：{data['vix']}
10年期美债：{data['tnx']}

操作建议：{action}
"""
    return report

# =====================
# 4. 发送邮件（QQ邮箱）
# =====================

def send_email(content):
    sender = "你的QQ邮箱@qq.com"
    password = "你的授权码"
    receiver = "你的QQ邮箱@qq.com"

    msg = MIMEText(content, "plain", "utf-8")
    msg["Subject"] = "AI盘前预测"
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
    prob = predict(data)
    report = generate_report(prob, data)

    print(report)
    send_email(report)
