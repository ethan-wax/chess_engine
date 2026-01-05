import { 
    Button, 
    Typography,
    Stack,
    Box,
    Divider,
    MenuItem,
    Select,
    FormControl,
    InputLabel,
} from '@mui/material'
import type { SelectChangeEvent } from '@mui/material'
import { Psychology, SmartToy, AccountTree, Computer, RestartAlt } from '@mui/icons-material'

interface ControlPanelProps {
    onResetBoard?: () => Promise<void>;
    modelType: 'Classical' | 'Reinforcement' | 'MCTS' | 'Neural';
    onSwitchModel: (model: 'Classical' | 'Reinforcement' | 'MCTS' | 'Neural') => void;
}

const modelOptions: Array<{
    value: 'Classical' | 'Reinforcement' | 'MCTS' | 'Neural';
    label: string;
    icon: React.ReactNode;
}> = [
    { value: 'Classical', label: 'Classical', icon: <Psychology /> },
    { value: 'MCTS', label: 'MCTS', icon: <AccountTree /> },
    { value: 'Neural', label: 'Neural', icon: <Computer /> },
    { value: 'Reinforcement', label: 'Reinforcement', icon: <SmartToy /> },
];

function ControlPanel({ onResetBoard, modelType, onSwitchModel }: ControlPanelProps) {
    const handleModelChange = (event: SelectChangeEvent) => {
        onSwitchModel(event.target.value as 'Classical' | 'Reinforcement' | 'MCTS' | 'Neural');
    };

    return (
        <Stack spacing={2}>
            <Box>
                <Typography 
                    variant="h6" 
                    sx={{ 
                        mb: 1.5,
                        fontWeight: 600,
                        color: 'text.primary',
                        fontSize: '1.1rem',
                    }}
                >
                    Game Controls
                </Typography>
                
                <Stack spacing={2}>
                    <FormControl fullWidth size="small">
                        <InputLabel id="model-select-label">AI Model</InputLabel>
                        <Select
                            labelId="model-select-label"
                            id="model-select"
                            value={modelType}
                            label="AI Model"
                            onChange={handleModelChange}
                            sx={{
                                borderRadius: 1.5,
                            }}
                        >
                            {modelOptions.map((option) => (
                                <MenuItem key={option.value} value={option.value}>
                                    <Stack direction="row" spacing={1.5} alignItems="center">
                                        {option.icon}
                                        <Typography>{option.label}</Typography>
                                    </Stack>
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>

                    <Divider />

                    <Button
                        variant="outlined"
                        onClick={onResetBoard}
                        startIcon={<RestartAlt />}
                        fullWidth
                        size="small"
                        sx={{
                            py: 1,
                            fontSize: '0.9rem',
                            fontWeight: 600,
                            borderRadius: 1.5,
                            textTransform: 'none',
                        }}
                    >
                        Reset Board
                    </Button>
                </Stack>
            </Box>

            <Divider />

            <Box>
                <Typography 
                    variant="body2" 
                    sx={{ 
                        color: 'text.secondary',
                        fontSize: '0.75rem',
                        lineHeight: 1.5,
                    }}
                >
                    Select an AI model to play against. Move pieces by dragging and dropping.
                </Typography>
            </Box>
        </Stack>
    )
}

export default ControlPanel