import {
  Chip,
} from "@mui/material";
import { GetJobByIDResponse } from "../../services/housework/jobs";
import { Stars } from "@mui/icons-material";

interface JobPriorityChipProps {
  job: GetJobByIDResponse;
}

export default function JobPriorityChip({ job }: JobPriorityChipProps) {
  if (job.is_priority) {
    return (
      <Chip
        color="primary"
        variant="outlined"
        icon={<Stars />}
        label="Priority"
      />
    );
  }
  return null;
}
