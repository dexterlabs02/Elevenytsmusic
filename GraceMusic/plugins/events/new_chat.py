from pyrogram import filters, types
from pyrogram.errors import ChatAdminRequired, ChannelPrivate

from GraceMusic import app, config


@app.on_message(filters.new_chat_members & filters.group)
async def new_chat_member(_, message: types.Message):
    """Handler for when bot is added to a new group"""

    # Check if the bot itself was added
    for member in message.new_chat_members:
        if member.id == app.id:
            chat = message.chat

            # Get chat information
            chat_name = chat.title
            chat_id = chat.id
            chat_username = f"@{chat.username}" if chat.username else "Private Group"
            try:
                members_count = await app.get_chat_members_count(chat_id)
            except (ChannelPrivate, Exception):
                members_count = "Unknown"

            # Get the user who added the bot
            added_by = message.from_user
            added_by_name = added_by.mention if added_by else "Unknown"

            # Create the formatted message with blockquote
            text = f"""<blockquote>🟢 <b>🎵 Grace Music Added to a New Group 🎵</b></blockquote>

<blockquote>
📍 <b>Chat Name:</b> {chat_name}
🆔 <b>Chat ID:</b> <code>{chat_id}</code>
👤 <b>Username:</b> {chat_username}
🔗 <b>Chat Link:</b> {f"https://t.me/{chat.username}" if chat.username else "N/A"}
👥 <b>Members:</b> {members_count}
✨ <b>Added By:</b> {added_by_name}
</blockquote>
"""

            try:
                # Send the notification to the logger group
                await app.send_photo(
                    chat_id=config.LOGGER_ID,
                    photo=config.START_IMG,
                    caption=text
                )
            except Exception as e:
                print(f"Failed to send new chat notification: {e}")

            break


@app.on_message(filters.left_chat_member & filters.group)
async def left_chat_member(_, message: types.Message):
    """Handler for when bot is removed from a group"""

    # Check if the bot itself was removed
    if message.left_chat_member.id == app.id:
        chat = message.chat

        # Get chat information
        chat_name = chat.title
        chat_id = chat.id
        chat_username = f"@{chat.username}" if chat.username else "Private Group"

        # Get the user who removed the bot
        removed_by = message.from_user
        removed_by_name = removed_by.mention if removed_by else "Unknown"

        # Create the formatted message with blockquote
        text = f"""<blockquote>🔴 <b>🎵 Grace Music Removed from a Group 🎵</b></blockquote>

<blockquote>
📍 <b>Chat Name:</b> {chat_name}
🆔 <b>Chat ID:</b> <code>{chat_id}</code>
👤 <b>Username:</b> {chat_username}
🔗 <b>Chat Link:</b> {f"https://t.me/{chat.username}" if chat.username else "N/A"}
❌ <b>Removed By:</b> {removed_by_name}
</blockquote>
"""

        try:
            # Send the notification to the logger group
            await app.send_photo(
                chat_id=config.LOGGER_ID,
                photo=config.START_IMG,
                caption=text
            )
        except Exception as e:
            print(f"Failed to send left chat notification: {e}")
