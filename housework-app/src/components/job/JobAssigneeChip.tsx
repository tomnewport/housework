import {
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  Skeleton,
} from "@mui/material";
import { GetJobByIDResponse } from "../../services/housework/jobs";
import { Face } from "@mui/icons-material";
import { useState } from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface JobAssigneeChipProps {
  job: GetJobByIDResponse;
}

export default function JobAssigneeChip({ job }: JobAssigneeChipProps) {
  const [open, setOpen] = useState<boolean>(false);

  if (!job?.assignee) {
    return (
      <Skeleton
        variant="rectangular"
        width={100}
        height={32}
        style={{ borderRadius: 16 }}
      />
    );
  }
  if (job.explanation) {
    return (
      <>
        <Chip
          color="primary"
          onClick={() => setOpen(true)}
          icon={<Face />}
          label={`${job.assignee.user.full_name}`}
        />
        <Dialog
          fullWidth={true}
          maxWidth="sm"
          open={open}
          onClose={() => setOpen(false)}
        >
          <DialogContent
            sx={{
              h1: { fontSize: "1.4rem", fontWeight: "300" },
              h2: { fontSize: "1.2rem", fontWeight: "900" },
              h3: { fontSize: "1.2rem", fontWeight: "300" },
              h4: { fontSize: "1rem", fontWeight: "900" },
              h5: { fontSize: "1rem", fontWeight: "600" },
              h6: { fontSize: "1rem", fontWeight: "400" },
              table: {
                borderCollapse: "collapse",
                display: "block",
                overflowX: "auto",
              },
              "td, th": {
                padding: ".5rem",
                border: "1px solid #ddd",
                whiteSpace: "nowrap",
              },
            }}
          >
            <Markdown remarkPlugins={[remarkGfm]}>{job.explanation}</Markdown>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>Close</Button>
          </DialogActions>
        </Dialog>
      </>
    );
  }
  return (
    <Chip
      color="primary"
      variant="outlined"
      icon={<Face />}
      label={`${job.assignee.user.full_name}`}
    />
  );
}
