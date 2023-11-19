import {
  Chip,
} from "@mui/material";
import {
  EmojiEventsRounded,
} from "@mui/icons-material";
import { GetJobByIDResponse } from "../../services/housework/jobs";

interface JobCreditChipProps {
  job: GetJobByIDResponse;
}

export default function JobCreditChip({ job }: JobCreditChipProps) {
  const credit = job.credits[0];

  if (credit) {
    const winner = `${credit.person.user.full_name}`;
    return (
      <Chip
        icon={<EmojiEventsRounded />}
        label={`${winner} earned ${credit.amount}`}
      />
    );
  }

  if (job.status !== "Complete" && job.status !== "Cancelled") {
    const { variants = [] } = job.job_config || {};
    if (variants.length) {
      return (
        <Chip
          color="primary"
          variant="outlined"
          icon={<EmojiEventsRounded />}
          label={`${job.default_credit} | ${variants
            .map((v) => v.credit)
            .join(" | ")}`}
        />
      );
    }
    return (
      <Chip
        color="primary"
        variant="outlined"
        icon={<EmojiEventsRounded />}
        label={`${job.default_credit} available`}
      />
    );
  }
  return null;
}
