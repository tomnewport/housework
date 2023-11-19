import {
  ArrowBack,
  SkipNext,
} from "@mui/icons-material";
import {
  AppBar,
  Card,
  Dialog,
  DialogContent,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  useTheme,
} from "@mui/material";
import { useState } from "react";
import {
  GetJobByIDResponse,
  useJobCloseMutation,
} from "../../services/housework/jobs";
import TransitionLeft from "../TransitionLeft";
import { useShouldFullscreen } from "../../utils/mediaQuery";
import JobDelayWidget from "./JobDelayWidget";

interface JobCancelDialogProps {
  open: boolean;
  onClose: () => void;
  job: GetJobByIDResponse;
  closeJob: () => void;
}

export default function JobCancelDialog({
  open,
  onClose,
  job,
  closeJob,
}: JobCancelDialogProps) {
  const [delay, setDelay] = useState<number>(0);
  const theme = useTheme();

  const [closeJobData] = useJobCloseMutation();

  async function handleClose() {
    if (!job.id) throw new Error("Job has no ID");
    await closeJobData({
      parameters: {
        path: {
          job_id: job.id,
          status: "Cancelled",
        },
      },
      requestBody: {
        content: {
          "application/json": {
            delay,
          },
        },
      },
    }).unwrap();
    closeJob();
  }
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
            Skip job
          </Typography>
        </Toolbar>
      </AppBar>
      <DialogContent>
        You are about to skip this job. No credit will be awarded.
        <JobDelayWidget
          status="Cancelled"
          delay={delay}
          setDelay={setDelay}
          job={job}
        />
        <Card sx={{ mt: 4 }}>
          <List sx={{ p: 0 }}>
            <ListItemButton
              onClick={handleClose}
              sx={{
                backgroundColor: theme.palette.secondary.main,
                color: "white",
                "&:hover": {
                  backgroundColor: theme.palette.secondary.main,
                },
              }}
            >
              <ListItemIcon>
                <SkipNext sx={{ color: theme.palette.primary.contrastText }} />
              </ListItemIcon>
              <ListItemText primary="Skip" />
            </ListItemButton>
          </List>
        </Card>
      </DialogContent>
    </Dialog>
  );
}
