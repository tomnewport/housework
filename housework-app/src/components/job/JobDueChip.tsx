import {
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  List,
  ListItem,
  ListItemText,
  Skeleton,
} from "@mui/material";
import { GetJobByIDResponse } from "../../services/housework/jobs";
import { Event } from "@mui/icons-material";
import { useState } from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { DateTime } from "luxon";

interface JobDueChipProps {
  job: GetJobByIDResponse;
}

function formatDateToRelative(dateString: string) {
  const date = DateTime.fromISO(dateString);
  const now = DateTime.now();

  return date.toRelative({ base: now });
}

export default function JobDueChip({ job }: JobDueChipProps) {
  const [open, setOpen] = useState<boolean>(false);

  if (!job.due_date) return null;
  if (job.status === "Complete" || job.status === "Cancelled") return null;

  return (
    <Chip
    color="primary"
    variant="outlined"
      icon={<Event />}
      label={`Due ${formatDateToRelative(job.due_date)}`}
    />
  );
}
