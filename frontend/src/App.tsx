import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { Container, Box, Typography, Paper, Grid } from '@mui/material'
import Board from './Board.tsx'
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
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="xl" sx={{ p: 2, display: 'flex', justifyContent: 'space-evenly', gap: 4 }}>
        <Box sx={{ width: '40%' }}>
          <Paper elevation={1}>
            <ControlPanel />
          </Paper>
        </Box>
        <Box>
          <Paper elevation={1} sx={{ p: 2 }}>
            <Board />
          </Paper>
        </Box>
      </Container>
    </ThemeProvider>
  )
}

export default App
