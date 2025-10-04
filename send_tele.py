import json
import requests

# ==== CẤU HÌNH TELEGRAM ====
TELEGRAM_BOT_TOKEN = "7729812653:AAH8aKKVOeLEHMA6ri7noJ7dULhg1bQKaeo"
TELEGRAM_CHAT_ID = "-4853323997"
RESULT_JSON_PATH = "result_count.json"  # File JSON chứa kết quả


def send_telegram_message(bot_token, chat_id, message):
    """Gửi text message đến Telegram"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode":"HTML"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("✓ Đã gửi message đến Telegram")
            return True
        else:
            print(f"✗ Lỗi gửi message: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Exception khi gửi message: {e}")
        return False


def send_telegram_document(bot_token, chat_id, file_path, caption=""):
    """Gửi file JSON đến Telegram"""
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    try:
        with open(file_path, 'rb') as file:
            files = {'document': file}
            data = {
                'chat_id': chat_id,
                'caption': caption
            }
            response = requests.post(url, files=files, data=data)
            if response.status_code == 200:
                print("✓ Đã gửi file JSON đến Telegram")
                return True
            else:
                print(f"✗ Lỗi gửi file: {response.text}")
                return False
    except Exception as e:
        print(f"✗ Exception khi gửi file: {e}")
        return False


# ==== ĐỌC FILE KẾT QUẢ ====
try:
    with open(RESULT_JSON_PATH, "r", encoding="utf-8") as f:
        result_data = json.load(f)
except FileNotFoundError:
    print(f"✗ Không tìm thấy file {RESULT_JSON_PATH}")
    exit()
except json.JSONDecodeError:
    print(f"✗ File {RESULT_JSON_PATH} không đúng định dạng JSON")
    exit()


# ==== TẠO MESSAGE ====
telegram_message = "🤖 <b>KẾT QUẢ KIỂM ĐẾM ĐỐI TƯỢNG</b>\n"
telegram_message += "━━━━━━━━━━━━━━━━━━━━━━\n\n"

for item in result_data:
    obj_name = item['object_name']
    expected = item['expected_count']
    detected = item['detected_count']
    status = item['status']
    difference = item['difference']
    
    if status == "đủ":
        emoji = "✅"
        telegram_message += f"{emoji} <b>{obj_name.upper()}</b>: Đủ {expected}\n"
    elif status == "thiếu":
        emoji = "❌"
        telegram_message += f"{emoji} <b>{obj_name.upper()}</b>: Thiếu {difference} (có {detected}/{expected})\n"
    else:  # thừa
        emoji = "⚠️"
        telegram_message += f"{emoji} <b>{obj_name.upper()}</b>: Thừa {difference} (có {detected}/{expected})\n"

telegram_message += "\n━━━━━━━━━━━━━━━━━━━━━━"


# ==== GỬI ĐẾN TELEGRAM ====
print("\n🚀 Đang gửi kết quả đến Telegram...")

# Gửi message
send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, telegram_message)

# Gửi file JSON
send_telegram_document(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, RESULT_JSON_PATH, 
                      caption="📄 File JSON chi tiết kết quả kiểm đếm")

print("\n✅ Hoàn tất!")