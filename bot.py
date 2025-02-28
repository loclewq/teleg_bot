import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes


def getnews():
    tieude = []
    r = requests.get('https://baomoi.com/tag/LITE.epi')
    soup = BeautifulSoup(r.text, 'html.parser')
    titles = soup.find_all('h3', class_='font-semibold block')

    # Chỉ lấy 10 tiêu đề đầu tiên
    for i, title in enumerate(titles[:10], 1):
        try:
            # Tìm thẻ a bên trong h3
            a_tag = title.find('a')

            if a_tag:
                # Lấy nội dung text của thẻ a (tiêu đề)
                title_text = a_tag.get_text(strip=True)

                # Lấy URL từ thuộc tính href của thẻ a
                link = a_tag.get('href')

                # Thêm domain vào URL tương đối để tạo URL đầy đủ
                base_url = "https://baomoi.com"
                full_link = base_url + link

                #tieude.append(f"{i}. {title_text}")
                tieude.append(f"{i}. {full_link}")
                #tieude.append("-" * 50)
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


app = ApplicationBuilder().token("8180575813:AAHlZg9ECm-bopEKE7_AzycPy-cJXXOtu_w").build()

app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("news", news))

app.run_polling()