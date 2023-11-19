import JobsPage from "../pages/JobsPage";
import ProfilePage from "../pages/Profile";
import SiteNav from "./SiteNav";
import { Box, Slide } from "@mui/material";
import MyTeamsView from "./team/MyTeamsView";
import { useParams } from "react-router-dom";
import FloatingActionButton from "./FloatingActionButton";

/*
    Site layout:
    - Jobs
        - JobID
    - Teams
        - TeamID
            - JobConfig
                - JobConfigID
    - Search
        - JobConfigID
    - Profile
*/

export default function Site() {
  const { section = "jobs", subsection } = useParams();

  const pages = [
    {
      section: "profile",
      component: <ProfilePage />,
    },
    {
      section: "jobs",
      component: (
        <JobsPage jobId={section === "jobs" ? subsection : undefined} />
      ),
    },
    {
      section: "teams",
      component: (
        <MyTeamsView teamId={section === "teams" ? subsection : undefined} />
      ),
    },
  ];
  return (
    <SiteNav path={[section, subsection || ""]}>
      <FloatingActionButton />
      {pages.map((item) => (
        <Slide
          key={item.section}
          in={item.section === section}
          direction={item.section === section ? "left" : "right"}
        >
          <Box
            sx={{
              position: "absolute",
              left: 0,
              top: 0,
              width: "100%",
              height: "100%",
            }}
          >
            {item.component}
          </Box>
        </Slide>
      ))}
    </SiteNav>
  );
}
