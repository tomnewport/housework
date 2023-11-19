import {
  Chip,
} from "@mui/material";
import { GetJobByIDResponse } from "../../services/housework/jobs";
import { Event } from "@mui/icons-material";
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
