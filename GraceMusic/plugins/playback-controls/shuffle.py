import random
from pyrogram import filters, types

from GraceMusic import app, db, lang, queue
from GraceMusic.helpers import can_manage_vc


@app.on_message(filters.command(["shuffle"]) & filters.group & ~app.bl_users)
@lang.language()
@can_manage_vc
async def _shuffle(_, m: types.Message):
    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass
    
    items = queue.get_all(m.chat.id)
    
    if not items or len(items) <= 1:
        return await m.reply_text("⚠️ Queue is empty or has only one track!")
    
    # Get current track and remaining items
    current = items[0] if items else None
    remaining = items[1:] if len(items) > 1 else []
    
    if not remaining:
        return await m.reply_text("⚠️ No tracks to shuffle!")
    
    # Shuffle remaining tracks
    random.shuffle(remaining)
    
    # Rebuild queue with current track first
    queue.clear(m.chat.id)
    if current:
        queue.add(m.chat.id, current)
    for item in remaining:
        queue.add(m.chat.id, item)
    
    await m.reply_text(f"🔀 Queue **shuffled**! ({len(remaining)} tracks randomized)")
