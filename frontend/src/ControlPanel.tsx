import { 
    Button, 
    Card, 
    CardContent, 
    Typography,
    Chip,
    Stack
} from '@mui/material'
import { Psychology, SmartToy, AccountTree } from '@mui/icons-material'

interface ControlPanelProps {
    onResetBoard?: () => Promise<void>;
    modelType: 'Classical' | 'Reinforcement' | 'MCTS';
    onSwitchModel: () => void;
}

function ControlPanel({ onResetBoard, modelType, onSwitchModel }: ControlPanelProps) {

    return (
        <Card>
            <CardContent>
                <Stack direction="column" spacing={2} alignItems="center">
                    <Typography variant="body1">
                        Current Model:
                    </Typography>
                    
                    <Chip 
                        icon={modelType === 'Classical' ? <Psychology /> : modelType === 'Reinforcement' ? <SmartToy /> : <AccountTree />}
                        label={modelType}
                        color={modelType === 'Classical' ? 'primary' : modelType === 'Reinforcement' ? 'secondary' : 'success'}
                        variant="outlined"
                    />
                    
                    <Button 
                        variant="contained" 
                        onClick={onSwitchModel}
                        sx={{ marginLeft: 2 }}
                    >
                        Switch Model
                    </Button>

                    <Button
                        variant="contained"
                        onClick={onResetBoard}
                        sx={{ marginLeft: 2 }}
                    >
                        Reset Board
                    </Button>
                </Stack>
            </CardContent>
        </Card>
    )
}

export default ControlPanel