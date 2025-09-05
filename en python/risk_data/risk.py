import random
from .risk_data import RiskData

# Danh sách các User-Agent phổ biến
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
]

def generate_risk_data():
    # Chọn một user-agent ngẫu nhiên từ danh sách trên
    ua = random.choice(USER_AGENTS)
    
    risk = RiskData(
        user_agent=ua,
        language="en-US",
        color_depth=24,
        device_memory=8,
        hardware_concurrency=8,
        width=1920,
        height=1080,
        avail_width=1920,
        avail_height=1040,
        timezone_offset=-300,
        timezone="America/Chicago",
        platform="Win32"
    )
    return risk.generate()