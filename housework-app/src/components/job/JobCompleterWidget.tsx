import {
  Card,
  List,
  ListItem,
  ListItemAvatar,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  useTheme,
} from "@mui/material";
import { useGetSelfQuery } from "../../services/housework/auth";
import {
  GetJobByIDResponse,
  useGetJobDryRunQuery,
} from "../../services/housework/jobs";
import { useState } from "react";
import JobCompleteDialog from "./JobCompleteDialog";
import JobCancelDialog from "./JobCancelDialog";
import { Check, SkipNext } from "@mui/icons-material";
import { purple } from "@mui/material/colors";

interface JobCompleterWidgetProps {
  job: GetJobByIDResponse;
  closeJob: () => void;
}

export default function JobCompleterWidget({
  job,
  closeJob,
}: JobCompleterWidgetProps) {
  const { data: selfData } = useGetSelfQuery(undefined);
  const [completeOpen, setCompleteOpen] = useState<boolean>(false);
  const [cancelOpen, setCancelOpen] = useState<boolean>(false);

  const isAssignee = job.assignee.user.id === selfData?.id;
  const isOpen = job.status !== "Complete" && job.status !== "Cancelled";
  const isPastDue = job.status === "Overdue";

  const canComplete = isPastDue || (isAssignee && isOpen);

  const variants = job.job_config?.variants || [];

  const theme = useTheme();

  if (!canComplete && !isAssignee) {
    return (
      <p>
        Cannot complete as this job belongs to {job.assignee.user.full_name}{" "}
        {job.assignee.user.full_name}.
      </p>
    );
  }
  if (job.status === "Complete" || job.status === "Cancelled") return null;
  return (
    <>
      <JobCompleteDialog
        open={completeOpen}
        onClose={() => setCompleteOpen(false)}
        job={job}
        closeJob={closeJob}
      />
      <JobCancelDialog
        job={job}
        open={cancelOpen}
        onClose={() => setCancelOpen(false)}
        closeJob={closeJob}
      />
      <Card>
        <List sx={{ p: 0 }}>
          <ListItemButton
            onClick={() => setCompleteOpen(true)}
            sx={{
              backgroundColor: theme.palette.secondary.main,
              color: "white",
              "&:hover": {
                backgroundColor: theme.palette.secondary.main,
              },
            }}
          >
            <ListItemAvatar>
              <Check />
            </ListItemAvatar>
            <ListItemText primary="Complete job" />
          </ListItemButton>
          </List>
          </Card>
      <Card sx={{ mt: 4 }}>
        <List sx={{ p: 0 }}>
          <ListItemButton onClick={() => setCancelOpen(true)}>
            <ListItemIcon>
              <SkipNext />
            </ListItemIcon>
            <ListItemText primary="Skip job" />
          </ListItemButton>
        </List>
      </Card>
    </>
  );
}
