"""Application-wide constants."""

APP_NAME = "DATA ROOM"
APP_TAGLINE = "Data analysis & cleaning workspace"
APP_VERSION = "1.1.0"

MAX_ROWS = 1_000_000          # hard limit on imported rows
MAX_PREVIEW_ROWS = 500        # rows shown in previews (import, cleaning)
MAX_EXPLORER_ROWS = 10_000    # rows rendered in the Data Explorer table
MAX_HISTORY = 10              # undoable cleaning steps kept in memory
MAX_ACTIVITY = 50             # activity entries kept in the session
