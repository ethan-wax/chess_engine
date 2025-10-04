import { useState, useRef } from 'react'
import { Chessboard, type PieceDropHandlerArgs } from 'react-chessboard'
import { Chess } from 'chess.js'

function Board() {
    const chessGameRef = useRef(new Chess());
    const chessGame = chessGameRef.current;
    const [position, setPosition] = useState(chessGame.fen());

    async function randMove() {
        const color = "black";
        const backend_url = `http://127.0.0.1:8000/move/${color}`;

        const res = await fetch(backend_url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Http error! Status: ${response.status}`)
                }
                return response.json();
            })
            .catch(error => {
                console.error("Fetch error:", error);
            })

        const possibleMoves = chessGame.moves();

       if (chessGame.isGameOver()) {
        return;
       } 

       const randomMove = possibleMoves[Math.floor(Math.random() * possibleMoves.length)];
       chessGame.move(randomMove);
       setPosition(chessGame.fen());
    }

    function onDrop({
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