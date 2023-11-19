import React, { useState } from "react";
import {
  Chip,
  Skeleton,
  ChipProps,
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
  EmojiEventsRounded,
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

const statusToColor: Record<
  string,
  "default" | "primary" | "secondary" | "warning"
> = {
  Scheduled: "default",
  Open: "primary",
  Overdue: "warning",
  Complete: "secondary",
  Cancelled: "default",
};

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
  const credit = job.credits[0];

  if (credit) {
    const winner = `${credit.person.user.full_name}`;
    const amount = credit.amount;
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
