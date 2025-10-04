import { useState, useRef, useEffect } from 'react'
import { Chessboard, type PieceDropHandlerArgs } from 'react-chessboard'
import { Chess } from 'chess.js'


const backend_url = `http://127.0.0.1:8000`;

function Board() {
    const chessGameRef = useRef(new Chess());
    const chessGame = chessGameRef.current;
    const [position, setPosition] = useState(chessGame.fen());
    useEffect(() => {
        resetBoard();
    }, []);

    async function resetBoard() {
        const url = backend_url + "/reset-board";
        await fetch(url, { method: "POST" })
    }

    async function randMove() {
        const possibleMoves = chessGame.moves();

        if (chessGame.isGameOver()) {
            return;
        } 

        const randomMove = possibleMoves[Math.floor(Math.random() * possibleMoves.length)];
        chessGame.move(randomMove);
        setPosition(chessGame.fen());

        const url = backend_url + `/move-san/${randomMove}`;

        await fetch(url, { method: 'POST' })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Http error! Status: ${response.status}`)
                }
                return response.json();
            })
            .catch(error => {
                console.error("Fetch error:", error);
            })
    }

    async function onDrop({
        sourceSquare,
        targetSquare,
    }: PieceDropHandlerArgs) {
        if (!targetSquare) {
            return false;
        }

        try {
            const move = chessGame.move({
                from: sourceSquare,
                to: targetSquare,
                promotion: 'q' // Always promote to queen for simplicity
            });

            // If move is invalid, chess.js will throw an error
            if (move === null) return false;

            setPosition(chessGame.fen());

            const url = backend_url + `/move-uci/${sourceSquare + targetSquare}`;
            await fetch(url, { method: "POST" });

            setTimeout(randMove, 500);
            return true;
        } catch (error) {
            return false;
        }
    }

    const chessboardOptions = {
        position,
        onPieceDrop: onDrop,
        id: 'play-vs-random'
    }

    return (
        <div>
            <div style={{ width: '50%', margin: 'auto' }}>
                <Chessboard options={chessboardOptions}/>
            </div>
        </div>
    );
}
export default Board