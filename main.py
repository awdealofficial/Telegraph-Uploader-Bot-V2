import os
import time
import math
import json
import string
import random
import traceback
import asyncio
import datetime
import aiofiles
import requests
from dotenv import load_dotenv
from random import choice 
from pyrogram import Client, filters
from helpers import humanbytes, convert
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid, UserNotParticipant, UserBannedInChannel
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid
from database import Database


load_dotenv()
BOT_OWNER = int(os.environ.get("BOT_OWNER", "875770605"))
DATABASE_URL = os.environ.get("DATABASE_URL", "mongodb+srv://aman:aman@cluster0.chnpche.mongodb.net/?retryWrites=true&w=majority")
db = Database(DATABASE_URL, "Telegraph-Uploader-Bot")

Bot = Client(
    "Telegraph Uploader Bot V2",
    bot_token=os.environ.get("BOT_TOKEN", "5475320054:AAGnT6eMBInj7v5scpjfw1Sw9jF_rwcERj8"),
    api_id=int(os.environ.get("API_ID","9411723")),
    api_hash=os.environ.get("API_HASH","30fa091455c0548d77dc254f0bb705b0")
)






START_TEXT = """**Hello {} 😌
⚡\nɪ ᴀᴍ ᴍᴅɪsᴋ ʙʏᴘᴀssᴇʀ ʙᴏᴛ\n\n>> ɪ ᴄᴀɴ ʙʏᴘᴀss ᴀɴʏ ᴍᴅɪsᴋ ʟɪɴᴋ ᴛᴏ ᴅɪʀᴇᴄᴛ ʟɪɴᴋ.\n\n#ɴᴏᴛᴇ sᴇɴᴅ ʟɪɴᴋ ᴏɴᴇ ʙʏ ᴏɴᴇ \n\n ᴍᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ @redxtgbots**

Made by @AmanReDX"""

DONATION_TEXT = """Hi there!

Please support in the development of **Mdisk Downloade Bot** by supporting me via some funds!

Here is the UPI id on which you can donate: `shrivastavaman100-1@okaxis`
A donation of 10Rs+ can help me a lot!

You can also help us to maintain **Mdisk Downloade Bot** by sharing or opening the below links if you didn't want to pay.

> https://clk.asia/redxtgbots
> https://clk.today/F2P5O
> https://clk.asia/F2P5O

Made by @AmanReDX"""

HELP_TEXT = """**Hey, Follow these steps:**

➠ Just give me a Mdisk Link.
(Single Link at a Time)

➠ Ex. `https://mdisk.me/convertor/16x9/vqBoOg`

➠ Than I Will Provide You Bypass Link. (File Download and Online Play Link)

**Available Commands**

/start - Checking Bot Online
/help - For more help
/about - For more about me

Made by @AmanReDX"""

ABOUT_TEXT = """--**ᴀʙᴏᴜᴛ ᴍᴇ**-- 😎

🤖 **Name :** [ᴍᴅɪsᴋ ᴅᴏᴡɴʟᴏᴀᴅᴇʀ ʙᴏᴛ](https://telegram.me/{})

👨‍💻 **Developer :** [ᴀᴍᴀɴʀҽᴅx](https://t.me/AmanReDX)

📢 **Channel :** [ʀҽᴅx ᴛɢ ʙᴏᴛs](https://t.me/redxtgbots)

📝 **Language :** [ᴘʏᴛʜᴏɴ𝟹](https://python.org)

🧰 **Framework :** [ᴘʏʀᴏɢʀᴀᴍ](https://pyrogram.org)"""

START_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton('⚙ Help', callback_data='help'),
            InlineKeyboardButton('About 🔰', callback_data='about'),
            InlineKeyboardButton('Close ✖️', callback_data='close')         
        ],
        [InlineKeyboardButton("💸 ᴅᴏɴᴀᴛᴇ 💸", url="https://te.legra.ph/ReDX-11-15-2")]
        
    ]
)

HELP_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton('🏘 Home', callback_data='home'),
            InlineKeyboardButton('About 🔰', callback_data='about'),
            InlineKeyboardButton('Close ✖️', callback_data='close')
        ]
    ]
)

ABOUT_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton('🏘 Home', callback_data='home'),
            InlineKeyboardButton('Help ⚙', callback_data='help'),
            InlineKeyboardButton('Close ✖️', callback_data='close')
        ]
    ]
)


async def send_msg(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return 200, None
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        return 400, f"{user_id} : deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id} : user is blocked\n"
    except PeerIdInvalid:
        return 400, f"{user_id} : user id invalid\n"
    except Exception as e:
        return 500, f"{user_id} : {traceback.format_exc()}\n"


@Bot.on_callback_query()
async def cb_handler(bot, update):
    
    if update.data == "home":
        await update.message.edit_text(
            text=START_TEXT.format(update.from_user.mention),
            reply_markup=START_BUTTONS,
            disable_web_page_preview=True
        )
    
    elif update.data == "help":
        await update.message.edit_text(
            text=HELP_TEXT,
            reply_markup=HELP_BUTTONS,
            disable_web_page_preview=True
        )
    
    elif update.data == "about":
        await update.message.edit_text(
            text=ABOUT_TEXT.format((await bot.get_me()).username),
            reply_markup=ABOUT_BUTTONS,
            disable_web_page_preview=True
        )
    
    else:
        await update.message.delete()


@Bot.on_message(filters.private & filters.command(["start"]))
async def start(bot, update):
    
    if not await db.is_user_exist(update.from_user.id):
        await db.add_user(update.from_user.id)
    
    await update.reply_text(
        text=START_TEXT.format(update.from_user.mention),
        disable_web_page_preview=True,
        reply_markup=START_BUTTONS
    )


@Bot.on_message(filters.private & filters.command(["help"]))
async def help(bot, update):
    
    if not await db.is_user_exist(update.from_user.id):
        await db.add_user(update.from_user.id)
    
    await update.reply_text(
        text=HELP_TEXT,
        disable_web_page_preview=True,
        reply_markup=HELP_BUTTONS
    )


@Bot.on_message(filters.private & filters.command(["about"]))
async def about(bot, update):
    
    if not await db.is_user_exist(update.from_user.id):
        await db.add_user(update.from_user.id)
    
    await update.reply_text(
        text=ABOUT_TEXT.format((await bot.get_me()).username),
        disable_web_page_preview=True,
        reply_markup=ABOUT_BUTTONS
    )
    
  
    
    
    
 

@Bot.on_message(
    filters.private &
    filters.command("broadcast") &
    filters.user(BOT_OWNER) &
    filters.reply
)
async def broadcast(bot, update, broadcast_ids={}):
    
    all_users = await db.get_all_users()
    broadcast_msg = update.reply_to_message
    
    while True:
        broadcast_id = ''.join([random.choice(string.ascii_letters) for i in range(3)])
        if not broadcast_ids.get(broadcast_id):
            break

    out = await update.reply_text(text=f"Broadcast Started! You will be notified with log file when all the users are notified.")
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    failed = 0
    success = 0
    broadcast_ids[broadcast_id] = dict(total = total_users, current = done, failed = failed, success = success)
        
    async with aiofiles.open('broadcast.txt', 'w') as broadcast_log_file:
        async for user in all_users:
            sts, msg = await send_msg(user_id = int(user['id']), message = broadcast_msg)
            if msg is not None:
                await broadcast_log_file.write(msg)
            if sts == 200:
                success += 1
            else:
                failed += 1
            if sts == 400:
                await db.delete_user(user['id'])
            done += 1
            if broadcast_ids.get(broadcast_id) is None:
                break
            else:
                broadcast_ids[broadcast_id].update(dict(current = done, failed = failed, success = success))
        
    if broadcast_ids.get(broadcast_id):
        broadcast_ids.pop(broadcast_id)
    
    completed_in = datetime.timedelta(seconds=int(time.time()-start_time))
    await asyncio.sleep(3)
    await out.delete()

    if failed == 0:
        await update.reply_text(text=f"broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.", quote=True)
    else:
        await update.reply_document(document='broadcast.txt', caption=f"broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.")
        
    os.remove('broadcast.txt')


@Bot.on_message(filters.private & filters.command("status"), group=5)
async def status(bot, update):

    total_users = await db.total_users_count()
    text = "**Bot Status**\n"
    text += f"\n**Total Users:** `{total_users}`"

    await update.reply_text(
        text=text,
        quote=True,
        disable_web_page_preview=True
    )

    
@Bot.on_message(filters.private & filters.text) 
async def link_extract(bot, message): 
    urls = message.text 
     
    if not message.text.startswith("https://mdisk.me"): 
        await message.reply_text( 
            f"INVALID LINK", 
            reply_to_message_id=message.id 
        ) 
        return 
    a = await bot.send_message( 
            chat_id=message.chat.id, 
            text=f"Processing…", 
            reply_to_message_id=message.id 
        ) 
    inp = urls #input('Enter the Link: ') 
    fxl = inp.split("/") 
    cid = fxl[-1] 
    URL=f'https://diskuploader.entertainvideo.com/v1/file/cdnurl?param={cid}' 
    header = { 
        'Accept': '*/*', 
        'Accept-Language': 'en-US,en;q=0.5', 
        'Accept-Encoding': 'gzip, deflate, br', 
        'Referer': 'https://mdisk.me/', 
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36' 
    } 
    resp = requests.get(url=URL, headers=header).json()
    fn = resp['filename']
    dn = resp['display_name']
    dr = resp['duration']
    sz = resp['size']
    ht = resp['height']
    wt = resp['width']
    download = resp['download']
    source = resp['source']
    
    await a.edit_text("**ᴛɪᴛʟᴇ :** {}\n\n**📏 sɪᴢᴇ :** {}\n\n**⏳ ᴅᴜʀᴀᴛɪᴏɴ :** {}\n\n**📹 ʀᴇsᴏʟᴜᴛɪᴏɴ :** {}*{}\n\n**🤓 ᴜᴘʟᴏᴀᴅᴇʀ :** {}\n\n**💽 ᴅᴏᴡɴʟᴏᴀᴅ ɴᴏᴡ (sᴜᴘᴘᴏʀᴛ ᴏɴʟʏ ᴍx ᴘʟᴀʏᴇʀ) :** {}\n\n**🖥️ sᴏᴜʀᴄᴇ ᴅᴏᴡɴʟᴏᴀᴅ ᴜʀʟ (ɪғ ᴍxᴠ ᴘʀᴇsᴇɴᴛ ɪɴ ʟɪɴᴋ ᴛʜᴇɴ ɪᴛ sᴜᴘᴘᴏʀᴛ ᴏɴʟʏ ᴍx ᴘʟᴀʏᴇʀ  ɪғ ᴅᴀsʜ, ᴍᴘᴅ, ᴍ𝟹ᴜ𝟾, ʜʟs ᴘʀᴇsᴇɴᴛ ɪɴ ʟɪɴᴋ ᴛʜᴇɴ ɪᴛ sᴜᴘᴘᴏʀᴛ ᴀʟʟ ᴘʟᴀʏᴇʀ) :** {}".format(fn, humanbytes(sz), convert(dr), wt, ht, dn, download, source),  disable_web_page_preview=True, 
                     reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('⚡ ᴊᴏɪɴ sᴜᴘᴘᴏʀᴛ ⚡', url="https://t.me/redxtgbots")]])#Download Link
                     
                     )
    


Bot.run()
