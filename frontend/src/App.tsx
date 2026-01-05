import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { Container, Box, Paper, Typography, AppBar, Toolbar } from '@mui/material'
import { useRef, useState } from 'react'
import Board, { type BoardHandle } from './Board.tsx'
import ControlPanel from './ControlPanel.tsx'

// Create a custom theme with a modern, elegant design
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#2c3e50',
      dark: '#1a252f',
      light: '#34495e',
    },
    secondary: {
      main: '#e74c3c',
      dark: '#c0392b',
      light: '#ec7063',
    },
    background: {
      default: '#f8f9fa',
      paper: '#ffffff',
    },
    text: {
      primary: '#2c3e50',
      secondary: '#7f8c8d',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 700,
      letterSpacing: '-0.02em',
    },
    h5: {
      fontWeight: 600,
      letterSpacing: '-0.01em',
    },
    h6: {
      fontWeight: 600,
    },
    button: {
      textTransform: 'none',
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 12,
  },
})

function App() {
  const boardRef = useRef<BoardHandle>(null);
  const [modelType, setModelType] = useState<'Classical' | 'Reinforcement' | 'MCTS' | 'Neural'>('Classical');

  const handleResetBoard = async () => {
    if (boardRef.current) {
      await boardRef.current.resetBoard();
    }
  };

  const handleSwitchModel = (model: 'Classical' | 'Reinforcement' | 'MCTS' | 'Neural') => {
    setModelType(model);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
        <AppBar 
          position="static" 
          elevation={0}
          sx={{ 
            bgcolor: 'primary.main',
            borderBottom: '1px solid',
            borderColor: 'divider',
          }}
        >
          <Toolbar>
            <Typography variant="h5" component="div" sx={{ flexGrow: 1, fontWeight: 700 }}>
              ♟️ Chess Engine
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              Play against AI
            </Typography>
          </Toolbar>
        </AppBar>
        
        <Container 
          maxWidth="xl" 
          sx={{ 
            py: 2,
            px: 2,
          }}
        >
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: { xs: '1fr', lg: '320px 1fr' },
              gap: 2,
              alignItems: 'start',
            }}
          >
            {/* Control Panel */}
            <Box>
              <Paper 
                elevation={2}
                sx={{ 
                  p: 2,
                  borderRadius: 2,
                  bgcolor: 'background.paper',
                  border: '1px solid',
                  borderColor: 'divider',
                  position: 'sticky',
                  top: 16,
                }}
              >
                <ControlPanel 
                  onResetBoard={handleResetBoard}
                  modelType={modelType}
                  onSwitchModel={handleSwitchModel}
                />
              </Paper>
            </Box>

            {/* Chess Board */}
            <Box>
              <Paper 
                elevation={2}
                sx={{ 
                  p: 2,
                  borderRadius: 2,
                  bgcolor: 'background.paper',
                  border: '1px solid',
                  borderColor: 'divider',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                }}
              >
                <Board ref={boardRef} modelType={modelType} />
              </Paper>
            </Box>
          </Box>
        </Container>
      </Box>
    </ThemeProvider>
  )
}

export default App
