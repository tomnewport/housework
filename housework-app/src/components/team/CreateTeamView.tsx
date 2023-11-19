import { ArrowBack } from "@mui/icons-material";
import { AppBar, Dialog, DialogContent, IconButton, Toolbar, Typography } from "@mui/material";
import { useShouldFullscreen } from "../../utils/mediaQuery";
import TransitionLeft from "../TransitionLeft";

export default function CreateTeamView({ open, onClose }: { open: boolean, onClose: () => void }) {
    const fullscreen = useShouldFullscreen();

    return (
        <Dialog
            fullWidth={true}
            maxWidth="sm"
            fullScreen={fullscreen}
            open={open}
            onClose={onClose}
            TransitionComponent={TransitionLeft}
        >
            <AppBar sx={{ position: "relative" }}>
            <Toolbar>
                <IconButton
                    edge="start"
                    color="inherit"
                    onClick={onClose}
                    aria-label="close"
                >
                    <ArrowBack />
                </IconButton>
                <Typography sx={{ ml: 2, flex: 1 }} variant="h6" component="div">
                    Start a new team
                </Typography>
            </Toolbar>
            </AppBar>
            <DialogContent>
                
            </DialogContent>
        </Dialog>
    )
}
