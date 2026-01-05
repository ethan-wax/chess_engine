import { useState, useRef, useEffect, forwardRef, useImperativeHandle } from 'react'
import { Chessboard, type PieceDropHandlerArgs } from 'react-chessboard'
import { Chess } from 'chess.js'
import { 
    Box, 
    Stack, 
    Alert,
    CircularProgress,
    Typography
} from '@mui/material'

const backend_url = `http://127.0.0.1:8000`;

export interface BoardHandle {
    resetBoard: () => Promise<void>;
}

interface BoardProps {
    modelType: 'Classical' | 'Reinforcement' | 'MCTS' | 'Neural';
}

const Board = forwardRef<BoardHandle, BoardProps>(({ modelType }, ref) => {
    const chessGameRef = useRef(new Chess());
    const chessGame = chessGameRef.current;
    const [position, setPosition] = useState(chessGame.fen());
    const [isLoading, setIsLoading] = useState(false);
    const [gameStatus, setGameStatus] = useState('');
    const [error, setError] = useState('');
    const [playerWin, setPlayerWin] = useState(false);
    const [playerLoss, setPlayerLoss] = useState(false);
    const [playerDraw, setPlayerDraw] = useState(false);
    
    useEffect(() => {
        resetBoard();
    }, []);

    useImperativeHandle(ref, () => ({
        resetBoard
    }));

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
            setPlayerWin(false);
            setPlayerLoss(false);
            setPlayerDraw(false);
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

    async function reinforcementMove() {
        load();
        try {
            const url = backend_url + "/ai-reinforcement";
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

    async function mctsMove() {
        load();
        try {
            const url = backend_url + "/ai-mcts";
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

    async function neuralMove() {
        load();
        try {
            const url = backend_url + "/ai-neural";
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

            if (chessGame.isCheckmate()) {
                setTimeout(() => setPlayerWin(true), 500);
                return true;
            } else if (chessGame.isDraw()) {
                setTimeout(() => setPlayerDraw(true), 500);
                return true;
            }

            setTimeout(async () => {
                if (modelType === 'Classical') {
                    await classicalMove();
                } else if (modelType === 'Reinforcement') {
                    await reinforcementMove();
                } else if (modelType === 'MCTS') {
                    await mctsMove();
                } else if (modelType === 'Neural') {
                    await neuralMove();
                }
                // Check game end conditions after AI move
                if (chessGame.isCheckmate()) {
                    setTimeout(() => setPlayerLoss(true), 500);
                } else if (chessGame.isDraw()) {
                    setTimeout(() => setPlayerDraw(true), 500);
                }
            }, 500);

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
        <Stack alignItems='center' spacing={1.5} sx={{ width: '100%' }}>
            { error && (
                <Alert 
                    variant='filled' 
                    severity='error' 
                    sx={{ 
                        maxWidth: 500,
                        borderRadius: 1.5,
                        fontSize: '0.85rem',
                        py: 0.5,
                    }}
                >
                    {error}
                </Alert>
            ) }
            { gameStatus && (
                <Alert 
                    variant='filled' 
                    severity='info' 
                    sx={{ 
                        maxWidth: 500,
                        borderRadius: 1.5,
                        fontSize: '0.85rem',
                        py: 0.5,
                    }}
                >
                    {gameStatus}
                </Alert>
            ) }
            { playerWin && (
                <Alert 
                    variant='filled' 
                    severity='success' 
                    sx={{ 
                        maxWidth: 500,
                        borderRadius: 1.5,
                        fontSize: '0.9rem',
                        fontWeight: 600,
                        py: 0.5,
                    }}
                >
                    🎉 Congratulations! You won!
                </Alert>
            ) }
            { playerLoss && (
                <Alert 
                    variant='filled' 
                    severity='error' 
                    sx={{ 
                        maxWidth: 500,
                        borderRadius: 1.5,
                        fontSize: '0.9rem',
                        fontWeight: 600,
                        py: 0.5,
                    }}
                >
                    Game Over - You lost!
                </Alert>
            ) }
            { playerDraw && (
                <Alert 
                    variant='filled' 
                    severity='warning' 
                    sx={{ 
                        maxWidth: 500,
                        borderRadius: 1.5,
                        fontSize: '0.9rem',
                        fontWeight: 600,
                        py: 0.5,
                    }}
                >
                    It's a draw!
                </Alert>
            ) }
            { isLoading && (
                <Alert 
                    variant='filled' 
                    severity='info' 
                    icon={<CircularProgress size={16} sx={{ color: 'inherit' }} />}
                    sx={{ 
                        maxWidth: 500,
                        borderRadius: 1.5,
                        fontSize: '0.85rem',
                        py: 0.5,
                    }}
                >
                    AI is thinking...
                </Alert>
            ) }
            
            <Box 
                sx={{ 
                    width: '100%',
                    maxWidth: 560,
                    display: 'flex',
                    justifyContent: 'center',
                }}
            >
                <Chessboard options={chessboardOptions}/>
            </Box>
        </Stack>
    );
});

Board.displayName = 'Board';

export default Board