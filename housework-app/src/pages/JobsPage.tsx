import { useNavigate } from "react-router-dom";
import JobList, { JobGroup } from "../components/job/JobList";
import JobView from "../components/job/JobView";
import {
  useGetOverdueJobsQuery,
  useGetOwnOpenJobsQuery,
} from "../services/housework/jobs";
import { Job } from "../services/housework/types";
import { DateTime } from "luxon";

function isOverdue(job: Job) {
  return job.status === "Overdue";
}

function isOpen(job: Job) {
  return job.status === "Open";
}

function isPriority(job: Job) {
  return job.is_priority;
}

function isSoon(job: Job) {
  const dueDateTime = DateTime.fromISO(job.due_date);
  const now = DateTime.now();

  return dueDateTime.diff(now, "days").days < 3;
}

export default function JobsPage({ jobId }: { jobId?: string }) {
  const { data: ownOpenJobs } = useGetOwnOpenJobsQuery(undefined);
  const { data: overdueJobs } = useGetOverdueJobsQuery(undefined);
  const navigate = useNavigate();

  const usedIds = new Set();

  const urgentSoon: Job[] = [];
  const overdue: Job[] = [];
  const open: Job[] = [];
  const upcoming: Job[] = [];

  [...(ownOpenJobs?.items || []), ...(overdueJobs?.items || [])].forEach(
    (job) => {
      if (job.id in usedIds) return;
      usedIds.add(job.id);
      if (isPriority(job) && isSoon(job)) {
        urgentSoon.push(job);
      } else if (isOverdue(job)) {
        overdue.push(job);
      } else if (isOpen(job)) {
        open.push(job);
      } else {
        upcoming.push(job);
      }
    },
  );

  const jobGroups: JobGroup[] = [
    {
      name: "Urgent",
      jobs: urgentSoon,
    },
    {
      name: "Overdue",
      jobs: overdue,
    },
    {
      name: "Open",
      jobs: open,
    },
    {
      name: "Upcoming",
      jobs: upcoming,
    },
  ].filter((group) => group.jobs.length > 0);

  return (
    <>
      <JobList jobGroups={jobGroups} />
      <JobView
        handleClose={() => navigate("/jobs")}
        open={!!jobId}
        jobId={parseInt(jobId || "0")}
      />
    </>
  );
}
