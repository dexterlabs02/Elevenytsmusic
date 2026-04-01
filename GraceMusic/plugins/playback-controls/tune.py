async def play_next(chat_id: int):
    """Play next track in queue"""
    from GraceMusic import queue
    
    logger.info(f"Playing next track for chat {chat_id}")
    
    # Get next track (current is already removed by skip command)
    next_track = queue.get_current_track(chat_id)
    
    if next_track:
        # Play the next track
        await play_track(chat_id, next_track)
        return True
    else:
        # No more tracks
        logger.info(f"No more tracks in queue for chat {chat_id}")
        await stop_playback(chat_id)
        return False
