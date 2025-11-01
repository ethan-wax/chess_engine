from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import chess
import logging
from classical import classical_move

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

board = chess.Board()

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"]
)

@app.post("/move-uci/{move}")
async def make_uci_move(move: str):
    uci_move = chess.Move.from_uci(move)
    board.push(uci_move)
    logger.info(f"UCI move {move} made. Current board:\n{board}")

@app.post("/move-san/{move}")
async def make_san_move(move: str):
    board.push_san(move)
    logger.info(f"SAN move {move} made. Current board:\n{board}")

@app.post("/reset-board")
async def reset_board():
    global board
    board = chess.Board()
    logger.info(f"Board reset. Current board:\n{board}")

@app.get("/ai-classical")
async def ai_classical():
    try:
        move = classical_move(board)
        # Make the move on the backend board
        board.push_san(move)
        logger.info(f"AI classical move {move} made. Current board:\n{board}")
        return JSONResponse(content={"move": move})
    except Exception as e:
        logger.error(f"Error in ai_classical: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)