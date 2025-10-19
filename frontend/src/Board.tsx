import { useState, useRef, useEffect } from 'react'
import { Chessboard, type PieceDropHandlerArgs } from 'react-chessboard'
import { Chess } from 'chess.js'
import { 
    Box, 
    Button, 
    Stack, 
    Typography, 
    Alert,
    CircularProgress
} from '@mui/material'
import { 
    Refresh, 
    PlayArrow
} from '@mui/icons-material'

const backend_url = `http://127.0.0.1:8000`;

function Board() {
    const chessGameRef = useRef(new Chess());
    const chessGame = chessGameRef.current;
    const [position, setPosition] = useState(chessGame.fen());
    const [isLoading, setIsLoading] = useState(false);
    const [gameStatus, setGameStatus] = useState('');
    const [error, setError] = useState('');
    
    useEffect(() => {
        resetBoard();
    }, []);

    async function resetBoard() {
        setIsLoading(true);
        setError('');
        try {
            const url = backend_url + "/reset-board";
            await fetch(url, { method: "POST" });
            chessGame.reset();
            setPosition(chessGame.fen());
            setGameStatus('Game reset');
        } catch (err) {
            setError('Failed to reset board');
        } finally {
            setIsLoading(false);
        }
    }

    async function randMove() {
        const possibleMoves = chessGame.moves();

        if (chessGame.isGameOver()) {
            setGameStatus('Game Over');
            return;
        } 

        const randomMove = possibleMoves[Math.floor(Math.random() * possibleMoves.length)];
        chessGame.move(randomMove);
        setPosition(chessGame.fen());

        const url = backend_url + `/move-san/${randomMove}`;

        try {
            const response = await fetch(url, { method: 'POST' });
            if (!response.ok) {
                throw new Error(`Http error! Status: ${response.status}`);
            }
            setGameStatus(`AI played: ${randomMove}`);
        } catch (error) {
            console.error("Fetch error:", error);
            setError('Failed to make AI move');
        }
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
            setGameStatus(`You played: ${move.san}`);

            const url = backend_url + `/move-uci/${sourceSquare + targetSquare}`;
            fetch(url, { method: "POST" });

            setTimeout(randMove, 500);
            return true;
        } catch (error) {
            setError('Invalid move');
            return false;
        }
    }

    const chessboardOptions = {
        position,
        onPieceDrop: onDrop,
        id: 'play-vs-random'
    }

    return (
        <Stack>
            <Box sx={{ width: '70%', margin: 'auto' }}>
                <Chessboard options={chessboardOptions}/>
            </Box>
        </Stack>
    );
}
export default Board