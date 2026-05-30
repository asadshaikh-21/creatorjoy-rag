import uvicorn
import multiprocessing
import os

# -----------------------------
# WINDOWS SAFETY FIX (IMPORTANT)
# -----------------------------
multiprocessing.set_start_method("spawn", force=True)


def start():
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        reload=True,   # dev mode (turn OFF in production)
        log_level="info",
        workers=1      # IMPORTANT: prevents Chroma + Gemini conflicts
    )


if __name__ == "__main__":
    start()