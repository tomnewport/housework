import {
  Box,
  Divider,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
} from "@mui/material";
import { Job } from "../../services/housework/types";
import EventIcon from "@mui/icons-material/Event";
import { DateTime } from "luxon";
import { useGetTeamsQuery } from "../../services/housework/teams";
import { Navigate, useNavigate } from "react-router-dom";

interface JobListItemProps {
  job: Job;
}

function formatDate(dueDate: string) {
  const due = DateTime.fromISO(dueDate);
  const now = DateTime.now();

  if (due.hasSame(now, "day")) {
    return "Due Today";
  } else if (due.hasSame(now.plus({ days: 1 }), "day")) {
    return "Due Tomorrow";
  } else if (due < now) {
    // Calculate whole days overdue
    const daysOverdue = Math.ceil(now.diff(due, "days").days);
    const dayWord = daysOverdue === 1 ? "day" : "days";
    return `${daysOverdue} ${dayWord} overdue`;
  } else if (due.diff(now, "days").days <= 7) {
    // Check if the due date is within the next 7 days
    return `Due ${due.toFormat("cccc")}`;
  } else if (due.diff(now, "years").years < 1) {
    return `Due ${due.toFormat("MMM d")}`;
  } else {
    return `Due ${due.toFormat("MMM d 'yy")}`;
  }
}

export default function JobListItem({ job }: JobListItemProps) {
  const navigate = useNavigate();

  const dueText = formatDate(job.due_date);
  const { data: teamsData = [] } = useGetTeamsQuery(undefined);
  const teamName = teamsData.find((team) => team.id == job.team)
    ?.name;

  return (
    <>
      <ListItemButton
        alignItems="flex-start"
        onClick={() => navigate(`/jobs/${job.id}/`)}
      >
        <ListItemText
          secondaryTypographyProps={{ component: "div" }}
          primary={job.name}
          secondary={
            <Box
              sx={{ display: "flex", gap: 1, justifyContent: "space-between" }}
            >
              <Typography
                sx={{ display: "inline" }}
                component="div"
                variant="body2"
                color="text.primary"
              >
                {teamName}
              </Typography>
              {dueText}
            </Box>
          }
        />
      </ListItemButton>
      <Divider component="li" />
    </>
  );
}
