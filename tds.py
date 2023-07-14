import mysql.connector
import requests
from telegram.ext import Updater, CommandHandler
from datetime import datetime
import time
import re

# Kết nối tới MySQL
conn = mysql.connector.connect(
    host="103.255.237.3",
    user="trumcard5_tds",
    password="trumcard5_tds",
    database="trumcard5_tds"
)

# Tạo bảng tokens trong cơ sở dữ liệu
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS tokens
                  (chat_id BIGINT PRIMARY KEY, token TEXT, cookie TEXT, created_at DATETIME)''')

# Khởi tạo Updater và Dispatcher
updater = Updater("6384089824:AAEq7oWZJyg6SdxntbQdW4viHZA3t0RLJfw", use_context=True)
dispatcher = updater.dispatcher


def add_token(update, context):
    chat_id = update.message.chat_id
    token = context.args[0]  # Lấy token từ tham số truyền vào
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute("INSERT INTO tokens (chat_id, token, created_at) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE token = %s, created_at = %s",
                   (chat_id, token, created_at, token, created_at))
    conn.commit()

    update.message.reply_text('Token đã được thêm thành công!')


add_token_handler = CommandHandler('addtoken', add_token)
dispatcher.add_handler(add_token_handler)


def add_cookie(update, context):
    chat_id = update.message.chat_id

    if len(context.args) > 0:
        cookie = context.args[0]  # Lấy cookie từ tham số truyền vào

        cursor.execute("UPDATE tokens SET cookie = %s WHERE chat_id = %s",
                       (cookie, chat_id))
        conn.commit()

        update.message.reply_text('Cookie đã được thêm thành công!')
    else:
        update.message.reply_text('Vui lòng cung cấp cookie khi sử dụng lệnh /addcookie.')


add_cookie_handler = CommandHandler('addcookie', add_cookie)
dispatcher.add_handler(add_cookie_handler)


def login_facebook(update, context):
    chat_id = update.message.chat_id

    cursor.execute("SELECT token, cookie FROM tokens WHERE chat_id = %s", (chat_id,))
    result = cursor.fetchone()

    if result is not None:
        token = result[0]
        cookie = result[1]

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        url = 'https://www.facebook.com/'
        response = requests.get(url, headers=headers, cookies={'c_user': cookie})

        if response.status_code == 200 and 'c_user' in response.cookies:
            update.message.reply_text('Đăng nhập thành công vào Facebook!')
        else:
            update.message.reply_text('Đăng nhập thất bại vào Facebook. Vui lòng kiểm tra lại cookie.')
    else:
        update.message.reply_text('Vui lòng thêm token và cookie trước khi sử dụng lệnh /loginfb.')


login_facebook_handler = CommandHandler('loginfb', login_facebook)
dispatcher.add_handler(login_facebook_handler)


def task(update, context):
    chat_id = update.message.chat_id

    cursor.execute("SELECT token FROM tokens WHERE chat_id = %s", (chat_id,))
    result = cursor.fetchone()

    if result is not None:
        token = result[0]

        # Lấy ID từ URL API
        url = f"https://traodoisub.com/api/?fields=like&access_token={token}"
        response = requests.get(url)
        data = response.json()

        if 'id' in data:
            job_id = data['id']
            perform_job(job_id)
        else:
            update.message.reply_text('Không tìm thấy công việc nào.')
    else:
        update.message.reply_text('Vui lòng thêm token trước khi thực hiện nhiệm vụ.')


def perform_job(job_id):
    url = f"https://traodoisub.com/api/coin/?type=LIKE&id={job_id}&access_token={token}"
    response = requests.get(url)
    data = response.json()

    if 'xu' in data:
        xu = data['xu']
        update.message.reply_text(f"Đã nhận {xu} Xu từ công việc.")
    else:
        update.message.reply_text('Không thể hoàn thành công việc.')

    # Xóa công việc đã thực hiện
    url = f"https://traodoisub.com/api/?fields=like&access_token={token}"
    requests.get(url)


task_handler = CommandHandler('task', task)
dispatcher.add_handler(task_handler)


def start(update, context):
    update.message.reply_text('Chào mừng bạn đến với bot!')


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


def main():
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
