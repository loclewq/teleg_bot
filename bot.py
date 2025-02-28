import os
import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

def getnews_baomoi():
    news = []
    r = requests.get('https://baomoi.com/tag/LITE.epi')
    soup = BeautifulSoup(r.text, 'html.parser')
    titles = soup.find_all('h3', class_='font-semibold block')
    for title in titles:
        a_tag = title.find('a')
        if a_tag:
            link = a_tag.get('href')
            if link:
                full_link = "https://baomoi.com" + link
                news.append(full_link)
    return news

def getnews_nguoiquansat(key):
    base_url = 'https://nguoiquansat.vn/'
    full_url = f"{base_url}{key}"

    r = requests.get(full_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    h2_titles = soup.find_all('h2', class_='b-grid__title')
    h3_titles = soup.find_all('h3', class_='b-grid__title')

    unique_links = set()
    for tag in h2_titles + h3_titles:
        a_tag = tag.find('a')
        if a_tag:
            link = a_tag.get('href')
            if link:
                unique_links.add(link.strip())
    return list(unique_links)

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Xin chào {update.effective_user.first_name}')

async def show_news_categories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Tin mới", callback_data='getnews')],
        [InlineKeyboardButton("Chứng khoán", callback_data='chung-khoan')],
        [InlineKeyboardButton("Bất động sản", callback_data='bat-dong-san')],
        [InlineKeyboardButton("Tài chính Ngân hàng", callback_data='tai-chinh-ngan-hang')],
        [InlineKeyboardButton("Doanh nghiệp", callback_data='doanh-nghiep')],
        [InlineKeyboardButton("Thế giới", callback_data='the-gioi')],
        [InlineKeyboardButton("Thị trường", callback_data='thi-truong')],
        [InlineKeyboardButton("Công nghệ", callback_data='cong-nghe')],
        [InlineKeyboardButton("Vĩ mô", callback_data='vi-mo')],
        [InlineKeyboardButton("Xã hội", callback_data='xa-hoi')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text('Chọn một chủ đề:', reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text('Chọn một chủ đề:', reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    context.user_data['category'] = query.data
    context.user_data['offset'] = 0

    keyboard = [
        [InlineKeyboardButton("5", callback_data='5')],
        [InlineKeyboardButton("10", callback_data='10')],
        [InlineKeyboardButton("15", callback_data='15')],
        [InlineKeyboardButton("20", callback_data='20')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Bạn muốn hiển thị bao nhiêu tin tức?", reply_markup=reply_markup)

async def select_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    num_articles = int(query.data)
    category = context.user_data.get('category')
    offset = context.user_data.get('offset', 0)

    if category == 'getnews':
        news_list = getnews_baomoi()
    else:
        news_list = getnews_nguoiquansat(category)

    end = offset + num_articles
    for i, news in enumerate(news_list[offset:end], offset + 1):
        await context.bot.send_message(chat_id=query.message.chat_id, text=f"{i}. {news}")

    context.user_data['offset'] = end

    keyboard = [
        [InlineKeyboardButton("Xem tiếp", callback_data=f'continue_{num_articles}')],
        [InlineKeyboardButton("Chọn danh mục khác", callback_data='new_category')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=query.message.chat_id, text="Bạn muốn làm gì tiếp theo?", reply_markup=reply_markup)

async def continue_or_new_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data.startswith('continue'):
        num_articles = int(query.data.split('_')[1])
        category = context.user_data.get('category')
        offset = context.user_data.get('offset', 0)

        if category == 'getnews':
            news_list = getnews_baomoi()
        else:
            news_list = getnews_nguoiquansat(category)

        end = offset + num_articles
        for i, news in enumerate(news_list[offset:end], offset + 1):
            await context.bot.send_message(chat_id=query.message.chat_id, text=f"{i}. {news}")

        context.user_data['offset'] = end

        keyboard = [
            [InlineKeyboardButton("Xem tiếp", callback_data=f'continue_{num_articles}')],
            [InlineKeyboardButton("Chọn danh mục khác", callback_data='new_category')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=query.message.chat_id, text="Bạn muốn làm gì tiếp theo?", reply_markup=reply_markup)

    elif query.data == 'new_category':
        await show_news_categories(update, context)

# Lấy token từ biến môi trường
TOKEN = os.getenv('TELEGRAM_TOKEN')

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("news", show_news_categories))
app.add_handler(CallbackQueryHandler(button, pattern='^(getnews|chung-khoan|bat-dong-san|tai-chinh-ngan-hang|doanh-nghiep|the-gioi|thi-truong|cong-nghe|vi-mo|xa-hoi)$'))
app.add_handler(CallbackQueryHandler(select_number, pattern='^(5|10|15|20)$'))
app.add_handler(CallbackQueryHandler(continue_or_new_category, pattern='^(continue_[0-9]+|new_category)$'))

app.run_polling()
