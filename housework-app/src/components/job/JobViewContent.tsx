import {
  AppBar,
  DialogContent,
  IconButton,
  Stack,
  Toolbar,
  Typography,
} from "@mui/material";
import { GetJobByIDResponse } from "../../services/housework/jobs";
import { useNavigate } from "react-router-dom";
import JobStatusChip from "./JobStatusChip";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import JobAssigneeChip from "./JobAssigneeChip";
import JobDueChip from "./JobDueChip";
import JobPriorityChip from "./JobPriorityChip";
import JobCreditChip from "./JobCreditChip";
import JobCompleterWidget from "./JobCompleterWidget";
import { ArrowBack } from "@mui/icons-material";

export default function JobViewContent({
  job,
  closeJob,
}: {
  job: GetJobByIDResponse;
  closeJob: () => void;
}) {
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
            {job.status} job
          </Typography>
        </Toolbar>
      </AppBar>
      <DialogContent>
        <Typography variant="h6">{job.name}</Typography>
        <Stack
          useFlexGap
          flexWrap="wrap"
          direction="row"
          spacing={1}
          sx={{ mt: 2, mb: 1 }}
        >
          <JobStatusChip job={job} />
          <JobAssigneeChip job={job} />
          <JobDueChip job={job} />
          <JobPriorityChip job={job} />
          <JobCreditChip job={job} />
        </Stack>
        <Markdown remarkPlugins={[remarkGfm]}>
          {job.description || job.job_config?.description || "*No description*"}
        </Markdown>
        <JobCompleterWidget closeJob={closeJob} job={job} />
      </DialogContent>
    </>
  );
}
