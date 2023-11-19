import { Divider, List, ListSubheader } from "@mui/material";
import { Job } from "../../services/housework/types";
import JobListItem from "./JobListItem";
import React from "react";

export interface JobGroup {
  name: string;
  jobs: Job[];
}

interface JobListProps {
  jobGroups: JobGroup[];
}

export default function JobListComponent({ jobGroups }: JobListProps) {
  return (
    <List sx={{ pt: 0 }}>
      {jobGroups.map(({ name, jobs }) => (
        <React.Fragment key={name}>
          <ListSubheader sx={{ textTransform: 'uppercase', lineHeight: 3, background: "#efefef", fontWeight: "700" }}>
            {name}
          </ListSubheader>
          {jobs.map((job) => (
            <JobListItem key={job.id} job={job} />
          ))}
        </React.Fragment>
      ))}
    </List>
  );
}
