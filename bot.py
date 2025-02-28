import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
from bs4 import BeautifulSoup


def getnews():
    tieude = []
    r = requests.get('https://baomoi.com/tag/LITE.epi')
    soup = BeautifulSoup(r.text, 'html.parser')
    titles = soup.find_all('h3', class_='font-semibold block')

    for i, title in enumerate(titles[:10], 1):
        try:
            a_tag = title.find('a')
            if a_tag:
                title_text = a_tag.get_text(strip=True)
                link = a_tag.get('href')
                base_url = "https://baomoi.com"
                full_link = base_url + link
                tieude.append(f"{i}. {full_link}")
            else:
                print(f"{i}. Không tìm thấy thẻ a trong tiêu đề.")
        except Exception as e:
            print(f"Lỗi khi xử lý tiêu đề {i}: {e}")

    return tieude


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Xin chào {update.effective_user.first_name}')


async def news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tieude = getnews()
    for x in tieude:
        await update.message.reply_text(f'{x}')


# Lấy token từ biến môi trường
TOKEN = os.getenv('TELEGRAM_TOKEN')

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("news", news))

app.run_polling()
