import { useState } from 'react'
import { 
    Button, 
    Card, 
    CardContent, 
    Typography,
    Chip,
    Stack
} from '@mui/material'
import { Psychology, SmartToy } from '@mui/icons-material'

function ControlPanel() {
    const [modelType, setModelType] = useState('Classical');

    function switchModel(current: string) {
        console.log('clicked');
        console.log(current === 'Classical');
        if (current === 'Classical') {
            setModelType('Reinforcement');
        } else {
            setModelType('Classical');
        }
    }

    return (
        <Card>
            <CardContent>
                <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap">
                    <Typography variant="body1">
                        Current Model:
                    </Typography>
                    
                    <Chip 
                        icon={modelType === 'Classical' ? <Psychology /> : <SmartToy />}
                        label={modelType}
                        color={modelType === 'Classical' ? 'primary' : 'secondary'}
                        variant="outlined"
                    />
                    
                    <Button 
                        variant="contained" 
                        onClick={() => switchModel(modelType)}
                        sx={{ marginLeft: 2 }}
                    >
                        Switch Model
                    </Button>
                </Stack>
            </CardContent>
        </Card>
    )
}

export default ControlPanel