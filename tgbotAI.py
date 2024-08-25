from telegram.ext import Application, MessageHandler, filters, CommandHandler
import anthropic, random
from openai import OpenAI
import requests

ANTHROPIC_API_KEY = "token"
TELEGRAM_BOT_TOKEN = "token"
openAI_key = "token"
UNSPLASH_ACCESS_KEY = "token"

client_openai = OpenAI(api_key=openAI_key)
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# 自定義 prompt，您可以根據需要修改這個部分
CUSTOM_PROMPT = """我想讓你擔任我的私人造型師。我會告訴你我的時尚偏好和體型，你會建議我穿的衣服。您應該只回覆您推薦的服裝，而不要回覆其他內容。不要寫解釋。我的第一個請求是“我要參加一個正式活動，需要幫助選擇服裝設計一個服裝設計機器人，能提供設計輔助、3D建模、樣版生成、趨勢分析、客製化建議、生產管理、協作平台和環保選項。”"""


async def handle_message(update, context):
    global client , client_openai
    try:
        user_message_color = str(update.message.text.split(" ")[1])
        user_message_style = str(update.message.text.split(" ")[2])
        user_message_stature = str(update.message.text.split(" ")[3])
        try:
            user_message_else = str(update.message.text.split(" ")[4])
        except Exception as e:
            user_message_else = 'none'

        total = (
            user_message_color
            + user_message_style
            + user_message_stature
            + user_message_else
            + "以上為user的資訊請給予建議"
        )

        try:
            response = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1500,
                system=CUSTOM_PROMPT,
                messages=[{"role": "user", "content": total}],
            )
            await update.message.reply_text(response.content[0].text)
        except Exception as e:
            await update.message.reply_text(f"發生錯誤：{str(e)}")

        keywords = [response.content[0].text,response.content[0].text]
        selected_keyword = random.choice(keywords)
        
        url = f"https://api.unsplash.com/photos/random?query={selected_keyword}&client_id={UNSPLASH_ACCESS_KEY}"
        
        try:
            response = requests.get(url)
            data = response.json()
            
            # 確保圖像URL可用
            if response.status_code == 200 and 'urls' in data:
                image_url = data['urls']['regular']
                await update.message.reply_photo(photo=image_url)
            else:
                await update.message.reply_text("抱歉，無法獲取圖片，請稍後再試。")
        
        except Exception as e:
            await update.message.reply_text(f"發生錯誤：{str(e)}")        
        #openai
        # try:   
        #     client_openai = OpenAI(api_key=openAI_key)

        #     response = client_openai.images.generate(
        #         prompt=str(response.content[0]), n=2, size="1024x1024"
        #     )
        #     await update.message.reply_photo(photo=str(response.data[0].url))
        # except Exception as e:
        #     await update.message.reply_text(f"圖片錯誤 {e}")
    except Exception as e:
        print(e)
        await update.message.reply_text(f"資訊量不足請填完整 {e}")


async def hello(update, context):
    await update.message.reply_text(f"你好，{update.message.from_user.first_name}！")


async def guess_start(update, context):
    await update.message.reply_text(f"遊戲開始，請輸入 /guess 開始猜數字")
    global number
    number = random.randint(1, 100)


async def guess(update, context):
    global number
    if number == None:
        await update.message.reply_text("遊戲還沒開始，請輸入 /guess_start 開始")
        return

    try:
        guess_num = int(update.message.text.split(" ")[1])
        if guess_num < number:
            await update.message.reply_text("太小了~!")
        if guess_num > number:
            await update.message.reply_text("太大了~!")
        if guess_num == number:
            await update.message.reply_text("great")
            number = None

    except ValueError:
        await update.message.reply_text("請輸入有效數字!!")


async def pong(update, context):
    await update.message.reply_text(f"pong")


async def help(update, context):
    await update.message.reply_text(
        f"你好!我是您的專屬機器人\n\n我可以根據你的需求與風格喜好為您搭配服裝，並提供精確的服裝搭配建議，協助你輕鬆展現個人魅力。\n\n以下為指令列表\n\n-/help 查看清單 \n-/hello 與你打招呼 \n-/guess_start 猜數字\n/ping ping\n\n核心功能\n\n-/clothes [喜歡的顏色] [風格] [身材] [其他] \n沒有填no\n!!!!!!!!這樣你就可以隨時隨地輕鬆穿出最合適的搭配，展現自信與品味"
    )

def main():
    bot = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    bot.add_handler(CommandHandler("guess_start", guess_start))
    bot.add_handler(CommandHandler("guess", guess))
    bot.add_handler(CommandHandler("hello", hello))
    bot.add_handler(CommandHandler("ping", pong))
    bot.add_handler(CommandHandler("help", help))
    bot.add_handler(CommandHandler("clothes", handle_message))
    # bot.add_handler(CommandHandler('order_beta', order))
    print("============\nBot online\n============")
    bot.run_polling()


if __name__ == "__main__":
    main()