from pyrogram import filters, types

from Elevenyts import app, db, lang
from Elevenyts.helpers import can_manage_vc


@app.on_message(filters.command(["loop"]) & filters.group & ~app.bl_users)
@lang.language()
@can_manage_vc
async def _loop(_, m: types.Message):
    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass
    
    current_loop = await db.get_loop(m.chat.id)
    
    # Check if user specified a mode
    if len(m.command) > 1:
        mode_arg = m.command[1].lower()
        if mode_arg in ["0", "disable"]:
            new_loop = 0
            text = "<blockquote>➡️ Loop mode disabled</blockquote>"
        elif mode_arg in ["single", "1", "one"]:
            new_loop = 1
            text = "<blockquote>🔂 Loop mode set to Single Track</blockquote>"
        elif mode_arg in ["queue", "all", "10"]:
            new_loop = 10
            text = "<blockquote>🔁 Loop mode set to Queue</blockquote>"
        else:
            return await m.reply_text(
                "<blockquote><b>Usage:</b>\n"
                "• /loop - Cycle through modes\n"
                "• /loop disable - Disable loop\n"
                "• /loop single - Loop current track\n"
                "• /loop queue - Loop entire queue</blockquote>"
            )
    else:
        # Cycle through modes
        if current_loop == 0:
            new_loop = 1
            text = "<blockquote>🔂 Loop mode set to Single Track</blockquote>"
        elif current_loop == 1:
            new_loop = 10
            text = "<blockquote>🔁 Loop mode set to Queue</blockquote>"
        else:
            new_loop = 0
            text = "<blockquote>➡️ Loop mode disabled</blockquote>"
    
    await db.set_loop(m.chat.id, new_loop)
    await m.reply_text(text)
