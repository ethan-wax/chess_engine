import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { Container, Box, Paper } from '@mui/material'
import { useRef, useState } from 'react'
import Board, { type BoardHandle } from './Board.tsx'
import ControlPanel from './ControlPanel.tsx'

// Create a custom theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    h4: {
      fontWeight: 600,
    },
  },
})

function App() {
  const boardRef = useRef<BoardHandle>(null);
  const [modelType, setModelType] = useState<'Classical' | 'Reinforcement'>('Classical');

  const handleResetBoard = async () => {
    if (boardRef.current) {
      await boardRef.current.resetBoard();
    }
  };

  const handleSwitchModel = () => {
    setModelType(prev => prev === 'Classical' ? 'Reinforcement' : 'Classical');
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="xl" sx={{ p: 2, display: 'flex', justifyContent: 'space-evenly', gap: 4 }}>
        <Box sx={{ width: '40%' }}>
          <Paper elevation={1}>
            <ControlPanel 
              onResetBoard={handleResetBoard}
              modelType={modelType}
              onSwitchModel={handleSwitchModel}
            />
          </Paper>
        </Box>
        <Box>
          <Paper elevation={1} sx={{ p: 2 }}>
            <Board ref={boardRef} modelType={modelType} />
          </Paper>
        </Box>
      </Container>
    </ThemeProvider>
  )
}

export default App
