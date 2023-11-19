import {
  AppBar,
  Dialog,
  DialogContent,
  IconButton,
  Skeleton,
  Toolbar,
  Typography,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import { useGetJobByIdQuery } from "../../services/housework/jobs";
import JobViewContent from "./JobViewContent";
import { ArrowBack } from "@mui/icons-material";
import TransitionLeft from "../TransitionLeft";
import { useShouldFullscreen } from "../../utils/mediaQuery";

function JobViewLoading() {
  const navigate = useNavigate();
  return (
    <>
      <AppBar sx={{ position: "relative" }}>
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            onClick={() => navigate("/jobs/")}
            aria-label="close"
          >
            <ArrowBack />
          </IconButton>
          <Typography sx={{ ml: 2, flex: 1 }} variant="h6" component="div">
            <Skeleton />
          </Typography>
        </Toolbar>
      </AppBar>
      <DialogContent>
        <Skeleton />
        <Skeleton />
        <Skeleton />
      </DialogContent>
    </>
  );
}

function JobViewNotFound() {
  const navigate = useNavigate();
  return (
    <>
      <AppBar sx={{ position: "relative" }}>
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            onClick={() => navigate("/jobs/")}
            aria-label="close"
          >
            <ArrowBack />
          </IconButton>
          <Typography sx={{ ml: 2, flex: 1 }} variant="h6" component="div">
            Job not found
          </Typography>
        </Toolbar>
      </AppBar>
      <DialogContent>
        <Typography variant="body1" component="div">
          This job does not exist. If you followed a link to get here, the job
          may have been deleted.
        </Typography>
      </DialogContent>
    </>
  );
}

export default function JobView({
  open,
  jobId,
  handleClose,
}: {
  open: boolean;
  handleClose: () => void;
  jobId?: number;
}) {
  const { data: jobData, isLoading } = useGetJobByIdQuery(jobId || 0, {
    skip: !!!jobId,
  });

  const fullscreen = useShouldFullscreen();

  return (
    <Dialog
      fullScreen={fullscreen}
      open={open}
      onClose={handleClose}
      TransitionComponent={TransitionLeft}
      fullWidth={true}
      maxWidth="sm"
    >
      {isLoading && <JobViewLoading />}
      {!isLoading && !jobData && <JobViewNotFound />}
      {!!jobData && <JobViewContent closeJob={handleClose} job={jobData} />}
    </Dialog>
  );
}
