import { useEffect, useState } from "react";
import {
  GetJobByIDResponse,
  useGetJobDryRunQuery,
} from "../../services/housework/jobs";
import {
  Button,
  Card,
  Collapse,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  IconButton,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Skeleton,
  TextField,
} from "@mui/material";
import { TransitionGroup } from "react-transition-group";
import { Bolt, EditCalendar, Repeat } from "@mui/icons-material";
import { DateTime } from "luxon";

function formatDate(dateStr: string) {
  const date = DateTime.fromISO(dateStr);

  // Check if the date is valid
  if (!date.isValid) {
    return "Invalid date";
  }

  // Format the date
  const formattedDate = date.toFormat("cccc d MMMM");

  // Calculate the difference in days from now
  const now = DateTime.now();
  const diffInDays = date.diff(now, "days").days;
  let relativeTime;

  if (diffInDays < 0) {
    relativeTime = `${Math.abs(Math.floor(diffInDays))} days ago`;
  } else if (diffInDays === 0) {
    relativeTime = "today";
  } else {
    relativeTime = `in ${Math.ceil(diffInDays)} days`;
  }

  return `${formattedDate} (${relativeTime})`;
}

export default function JobDelayWidget({
  delay,
  setDelay,
  job,
  status,
}: {
  delay: number;
  setDelay: (a: number) => void;
  job: GetJobByIDResponse;
  status: "Complete" | "Cancelled";
}) {
  if (!job.id) {
    throw new Error("Job has no ID");
  }
  const [delayDlgOpen, setDelayDlgOpen] = useState<boolean>(false);

  const [delayStr, setDelayStr] = useState<string>(delay.toString());

  let delayAsNumber = parseInt(delayStr) || 0;
  if (isNaN(delayAsNumber)) {
    delayAsNumber = 0;
  }

  const {
    data: dryRunData = [],
    isLoading,
    isFetching,
  } = useGetJobDryRunQuery({
    path: { job_id: job.id, action: status },
    query: { delay: delayAsNumber },
  });

  useEffect(() => setDelay(delayAsNumber), [setDelay, delayAsNumber]);
  const delayText =
    delayAsNumber === 0
      ? "This action will create new jobs"
      : `This action will create new jobs after a ${delay} day pause.`;

  if (!isLoading && !isFetching && dryRunData.length === 0) return null;
  return (
    <Card sx={{ mt: 4 }}>
      <List>
        <TransitionGroup>
          <Collapse>
            <ListItem>
              <ListItemText
                primary={delayText}
                secondary="You can add a delay if these jobs are too soon."
              />
              <IconButton onClick={() => setDelayDlgOpen(true)} color="primary">
                <EditCalendar />
              </IconButton>
            </ListItem>
          </Collapse>
          <Collapse>
            <Divider />
          </Collapse>
          {!(isLoading || isFetching) &&
            dryRunData.map((item) => (
              <Collapse key={item.trigger.id}>
                <ListItem>
                  {item.trigger.id === job.job_config?.id ? (
                    <ListItemAvatar>
                      <Repeat />
                    </ListItemAvatar>
                  ) : (
                    <ListItemAvatar>
                      <Bolt />
                    </ListItemAvatar>
                  )}
                  <ListItemText
                    primary={item.created_job.name}
                    secondary={formatDate(item.proposed_date)}
                  />
                </ListItem>
              </Collapse>
            ))}
          {(isLoading || isFetching) && (
            <Collapse>
              <ListItem>
                <ListItemAvatar>
                  <Skeleton variant="circular" width={32} height={32} />
                </ListItemAvatar>

                <ListItemText
                  primary={<Skeleton width={400} />}
                  secondary={<Skeleton width={200} />}
                />
              </ListItem>
            </Collapse>
          )}
        </TransitionGroup>
      </List>
      <Dialog
        fullWidth={true}
        maxWidth="sm"
        open={delayDlgOpen}
        onClose={() => setDelayDlgOpen(false)}
      >
        <DialogTitle>Change delay</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Delay (days)"
            type="number"
            variant="standard"
            value={delay}
            InputProps={{ inputProps: { step: 1, min: 0, max: 365 } }}
            onChange={(event) => setDelayStr(event.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDelayDlgOpen(false)}>OK</Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
}
