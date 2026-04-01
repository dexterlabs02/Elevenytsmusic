import logging
from pyrogram import filters, types

from GraceMusic import app, config, db, lang, queue
from GraceMusic.helpers import Track, buttons, thumb

logger = logging.getLogger(__name__)


@app.on_message(filters.command(["queue", "playing"]) & filters.group & ~app.bl_users)
@lang.language()
async def _queue_func(_, m: types.Message):
    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass
    
    # Check if music is playing
    if not await db.get_call(m.chat.id):
        return await m.reply_text(m.lang["not_playing"])

    _reply = await m.reply_text(m.lang["queue_fetching"])
    
    # Get queue for this chat
    _queue = queue.get_queue(m.chat.id)
    
    if not _queue:
        # Queue is empty
        await _reply.edit_text(m.lang["queue_empty"])
        return
    
    # Get current playing track (first in queue)
    _media = _queue[0]
    
    # Generate thumbnail
    _thumb = (
        await thumb.generate(_media)
        if isinstance(_media, Track)
        else config.DEFAULT_THUMB
    )
    
    # Format current track info
    _text = m.lang["queue_curr"].format(
        _media.url,
        _media.title[:50],
        _media.duration,
        _media.user,
    )
    
    # Get queue length and total duration
    queue_length = len(_queue)
    total_duration = 0
    
    # Add upcoming tracks (excluding current)
    if queue_length > 1:
        _text += "\n\n📋 **Upcoming Tracks:**\n"
        _text += "<blockquote expandable>"
        
        for i, media in enumerate(_queue[1:], start=1):  # Start from index 1 (skip current)
            if i == 15:  # Limit to 15 tracks in preview
                remaining = queue_length - 15
                _text += f"\n... and {remaining} more"
                break
                
            # Add track to display
            _text += m.lang["queue_item"].format(
                i,  # Position in queue (1, 2, 3...)
                media.title[:30],  # Truncate long titles
                media.duration,
            )
            
            # Calculate total duration
            if hasattr(media, 'duration_seconds'):
                total_duration += media.duration_seconds
            
        _text += "</blockquote>"
        
        # Add queue summary
        total_min = total_duration // 60
        total_sec = total_duration % 60
        _text += f"\n\n📊 **Queue Summary:**"
        _text += f"\n• Total tracks: `{queue_length}`"
        _text += f"\n• Total duration: `{total_min}:{total_sec:02d}`"
    
    # Check if currently playing or paused
    _playing = await db.playing(m.chat.id)
    
    # Edit message with queue info
    await _reply.edit_media(
        media=types.InputMediaPhoto(
            media=_thumb,
            caption=_text,
        ),
        reply_markup=buttons.queue_markup(
            m.chat.id,
            m.lang["playing"] if _playing else m.lang["paused"],
            _playing,
        ),
    )
    
    logger.info(f"Queue displayed for chat {m.chat.id} - {queue_length} tracks")
