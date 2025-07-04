class PlaylistError(Exception):
    """Base class for all playlist-related errors."""
    pass

class EmptyPlaylistError(PlaylistError):
    """Raised when the playlist is empty and an operation can't proceed."""
    pass

class ReadHandlerNotFoundError(PlaylistError):
    """Raised when a requested song is not found in the playlist."""
    pass