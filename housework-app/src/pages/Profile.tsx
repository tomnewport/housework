import {
  useGetSelfQuery,
  useLogoutUserMutation,
} from "../services/housework/auth";
import {
  Button,
  List,
  ListItem,
  ListItemText,
  Paper,
  Typography,
} from "@mui/material";

export default function ProfilePage() {
  const { data: userData, isLoading } = useGetSelfQuery(undefined);
  const [logoutUser] = useLogoutUserMutation();
  if (isLoading) {
    return <p>Loading...</p>;
  }
  if (!userData) {
    return <p>Not logged in.</p>;
  }
  return (
    <div style={{ padding: "20px" }}>
      <Typography variant="h4" gutterBottom>
        Profile
      </Typography>

      <Paper elevation={3} style={{ padding: "20px", marginBottom: "20px" }}>
        <List>
          <ListItem>
            <ListItemText primary="Full name" secondary={userData.full_name} />
          </ListItem>
          <ListItem>
            <ListItemText
              primary="Short name"
              secondary={userData.short_name}
            />
          </ListItem>
          {userData.is_superuser && (
            <ListItem>
              <ListItemText primary="Status" secondary="Superuser" />
            </ListItem>
          )}
          {!userData.approved && (
            <ListItem>
              <ListItemText
                primary="Approval Status"
                secondary="Not Approved"
              />
            </ListItem>
          )}
        </List>
      </Paper>

      <Button variant="contained" color="primary" onClick={logoutUser}>
        Logout
      </Button>
    </div>
  );
};
