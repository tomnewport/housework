import { useState } from "react";
import {
  Chip,
  Skeleton,
  Dialog,
  DialogTitle,
  DialogContent,
  ListItem,
  List,
  ListItemText,
  DialogActions,
  Button,
} from "@mui/material";
import {
  Schedule,
  PlayCircleFilled,
  ErrorOutline,
  CheckCircleOutline,
  Cancel,
} from "@mui/icons-material";
import { GetJobByIDResponse } from "../../services/housework/jobs";
import { DateTime } from "luxon";

interface JobCreditChipProps {
  job: GetJobByIDResponse;
}

const statusToIcon: Record<string, JSX.Element> = {
  Scheduled: <Schedule />,
  Open: <PlayCircleFilled />,
  Overdue: <ErrorOutline />,
  Complete: <CheckCircleOutline />,
  Cancelled: <Cancel />,
};

function formatDate(isoDate?: string): string {
  if (!isoDate) return "--";
  return DateTime.fromISO(isoDate).toLocaleString(DateTime.DATETIME_FULL);
}

export default function JobCreditChip({ job }: JobCreditChipProps) {
  const [open, setOpen] = useState<boolean>(false);

  if (!job?.status) {
    return (
      <Skeleton
        variant="rectangular"
        width={100}
        height={32}
        style={{ borderRadius: 16 }}
      />
    );
  }

  const icon = statusToIcon[job.status];

  return (
    <>
      <Chip
        color="primary"
        onClick={() => setOpen(true)}
        icon={icon}
        label={job.status}
      />
      <Dialog
        fullWidth={true}
        maxWidth="sm"
        open={open}
        onClose={() => setOpen(false)}
      >
        <DialogTitle>Assigner process</DialogTitle>
        <DialogContent>
          <List>
            <ListItem>
              <ListItemText
                primary="Created"
                secondary={formatDate(job.created_date)}
              />
            </ListItem>
            <ListItem>
              <ListItemText
                primary="Due"
                secondary={formatDate(job.due_date)}
              />
            </ListItem>
            <ListItem>
              <ListItemText
                primary="Closed"
                secondary={formatDate(job.closed_date)}
              />
            </ListItem>
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
