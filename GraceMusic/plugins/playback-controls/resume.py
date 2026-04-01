import asyncio
import logging
from pyrogram import filters, types
from pyrogram.errors import ChatSendPlainForbidden, ChatWriteForbidden

from GraceMusic import tune, app, db, lang
from GraceMusic.helpers import buttons, can_manage_vc

logger = logging.getLogger(__name__)


@app.on_message(filters.command(["resume"]) & filters.group & ~app.bl_users)
@lang.language()
@can_manage_vc
async def _resume(_, m: types.Message):
    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass
    
    if not await db.get_call(m.chat.id):
        try:
            return await m.reply_text(m.lang["not_playing"])
        except (ChatSendPlainForbidden, ChatWriteForbidden):
            return

    if await db.playing(m.chat.id):
        try:
            return await m.reply_text(m.lang["play_not_paused"])
        except (ChatSendPlainForbidden, ChatWriteForbidden):
            return

    await tune.resume(m.chat.id)
    try:
        sent_msg = await m.reply_text(
            text=m.lang["play_resumed"].format(m.from_user.mention),
            reply_markup=buttons.controls(m.chat.id),
        )
        # Auto-delete after 3 minutes
        await asyncio.sleep(180)
        try:
            await sent_msg.delete()
        except Exception:
            pass
    except (ChatSendPlainForbidden, ChatWriteForbidden):
        logger.warning("Cannot send text in media-only chat")
