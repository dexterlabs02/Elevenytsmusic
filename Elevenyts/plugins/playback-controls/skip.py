# ==============================================================================
# skip.py - Skip Track Command
# ==============================================================================
# This plugin handles skipping to the next track in the queue.
#
# Commands:
# - /skip - Skip current track and play next
# - /next - Same as /skip
#
# Requirements:
# - User must be admin or authorized user
# - Music must be playing
# ==============================================================================

import asyncio
import logging
from pyrogram import filters, types
from pyrogram.errors import ChatSendPlainForbidden, ChatWriteForbidden

from HasiiMusic import tune, app, db, lang, queue
from HasiiMusic.helpers import can_manage_vc

logger = logging.getLogger(__name__)


@app.on_message(filters.command(["skip", "next"]) & filters.group & ~app.bl_users)
@lang.language()
@can_manage_vc
async def _skip(_, m: types.Message):
    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass
    
    # Check if music is playing
    if not await db.get_call(m.chat.id):
        try:
            return await m.reply_text(m.lang["not_playing"])
        except (ChatSendPlainForbidden, ChatWriteForbidden):
            return

    # Get current queue
    chat_queue = queue.get_queue(m.chat.id)
    
    # Check if there are more tracks in queue
    if len(chat_queue) > 1:
        # Remove current track (index 0)
        current_track = chat_queue.pop(0)
        logger.info(f"Skipped track: {current_track.title} in chat {m.chat.id}")
        
        # Play next track
        await tune.play_next(m.chat.id)
        
        # Get the new current track for display
        new_track = chat_queue[0] if chat_queue else None
        
        try:
            sent_msg = await m.reply_text(
                m.lang["play_skipped"].format(
                    m.from_user.mention,
                    new_track.title if new_track else "Unknown"
                )
            )
        except (ChatSendPlainForbidden, ChatWriteForbidden):
            logger.warning("Cannot send plain text in media-only chat")
            return
    else:
        # No more tracks in queue - stop playback
        logger.info(f"No more tracks in queue for chat {m.chat.id}, stopping playback")
        
        # Clear queue and stop
        queue.clear_queue(m.chat.id)
        await tune.stop(m.chat.id)
        
        try:
            sent_msg = await m.reply_text(
                m.lang["queue_empty"].format(m.from_user.mention)
            )
        except (ChatSendPlainForbidden, ChatWriteForbidden):
            logger.warning("Cannot send plain text in media-only chat")
            return
    
    # Auto-delete after 5 seconds
    await asyncio.sleep(5)
    try:
        await sent_msg.delete()
    except Exception:
        pass
