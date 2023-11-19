import { useNavigate, useParams } from "react-router-dom";
import { useGetSelfQuery } from "../../services/housework/auth";
import {
  Box,
  Card,
  CardActionArea,
  CardHeader,
  Grid,
  Toolbar,
  Typography,
} from "@mui/material";
import { Cottage, Create } from "@mui/icons-material";
import CreateTeamView from "./CreateTeamView";
import { useState } from "react";

export default function MyTeamsView({ teamId }: { teamId?: string }) {
  const { data: selfData } = useGetSelfQuery();
  const [createOpen, setCreateOpen] = useState<boolean>(false);
  const navigate = useNavigate();
  const { subsection } = useParams();

  console.log(subsection, navigate);

  const memberships = selfData?.memberships || [];

  return (
    <>
      <Toolbar
        sx={{ display: "flex", gap: 1, justifyContent: "space-between" }}
      >
        <Typography variant="h6">My teams</Typography>
      </Toolbar>
      <Box sx={{ ml: 3, mr: 3 }}>
        <Grid container spacing={2}>
          {memberships.map((membership) => (
            <Grid key={membership.team.name} item sm={12} md={6} xs={12} lg={4}>
              <Card>
                <CardActionArea>
                  <CardHeader
                    avatar={<Cottage />}
                    title={membership.team.name}
                    subheader={membership.role}
                  />
                </CardActionArea>
              </Card>
            </Grid>
          ))}
          <Grid item sm={12} md={6} xs={12} lg={4}>
            <CreateTeamView
              open={createOpen}
              onClose={() => setCreateOpen(false)}
            />
            <Card
              sx={{
                opacity: 0.5,
                boxShadow: "none",
                border: "1px dashed #ddd",
              }}
            >
              <CardActionArea onClick={() => setCreateOpen(true)}>
                <CardHeader
                  avatar={<Create />}
                  title="New team"
                  subheader="Click to create a new team"
                />
              </CardActionArea>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </>
  );
}
