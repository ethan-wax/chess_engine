import { useState, useRef, useEffect } from 'react'
import { Chessboard, type PieceDropHandlerArgs } from 'react-chessboard'
import { Chess } from 'chess.js'
import { 
    Box, 
    Stack, 
    Alert,
    CircularProgress
} from '@mui/material'

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

    function load() {
        setIsLoading(true);
        setError('');
        setGameStatus('');
    }

    function httpError(response: Response) {
        throw new Error(`Http error! Status: ${response.status}`);
    }

    async function resetBoard() {
        load();
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

    async function classicalMove() {
        load();
        try {
            const url = backend_url + "/ai-classical";
            const response = await fetch(url, { method: "GET" });
            if (!response.ok) {
                httpError(response);
            }
            
            const data = await response.json();
            if (data.error) {
                setError(`AI Error: ${data.error}`);
                return;
            }
            
            const move = data.move;
            chessGame.move(move);
            setPosition(chessGame.fen());
            setGameStatus(`AI played: ${move}`);
            
        } catch (err) {
            setError('AI failed to move');
        } finally {
            setIsLoading(false);
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
            setError('');

            const url = backend_url + `/move-uci/${sourceSquare + targetSquare}`;
            fetch(url, { method: "POST" });

            setTimeout(classicalMove, 500);
            return true;
        } catch (error) {
            setError('Invalid move');
            setGameStatus('');
            return false;
        }
    }

    const chessboardOptions = {
        position,
        onPieceDrop: onDrop,
        id: 'play-vs-random'
    }

    return (
        <Stack alignItems='center' spacing={3}>
            { error && <Alert variant='outlined' severity='error' sx={{ maxWidth: '50%'}}>{error}</Alert> }
            { gameStatus && <Alert variant='outlined' severity='info' sx={{ maxWidth: '50%'}}>{gameStatus}</Alert> }
            { isLoading && <CircularProgress /> }
            
            <Box sx={{ width: '70%', margin: 'auto' }}>
                <Chessboard options={chessboardOptions}/>
            </Box>
        </Stack>
    );
}
export default Board