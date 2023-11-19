import {
  Box,
  Collapse,
  IconButton,
  ListItemText,
  MenuItem,
  Typography,
} from "@mui/material";
import {
  useGetUnreadNotificationsQuery,
  useMarkNotificationAsReadMutation,
} from "../../services/housework/notifications";
import { TransitionGroup } from "react-transition-group";
import { useNavigate } from "react-router-dom";
import { Check } from "@mui/icons-material";
import RelativeDate from "../RelativeDate";

export default function UnreadList() {
  const { data = [] } = useGetUnreadNotificationsQuery(undefined, {
    pollingInterval: 10000,
  });
  const [markRead] = useMarkNotificationAsReadMutation();
  const navigate = useNavigate();

  return (
    <>
      <TransitionGroup>
        {data.map((notifi) => (
          <Collapse key={notifi.id}>
            <MenuItem>
              <ListItemText
                onClick={() => {
                  markRead(notifi.id!);
                  navigate(notifi.url);
                }}
                primary={
                  <Box
                    sx={{
                      display: "flex",
                      gap: 1,
                      justifyContent: "space-between",
                    }}
                  >
                    <Typography
                      sx={{ display: "inline", mr: 2 }}
                      component="div"
                      color="text.primary"
                    >
                      {notifi.title}
                    </Typography>
                    <Typography
                      sx={{ display: "inline" }}
                      component="div"
                      color="text.secondary"
                    >
                      <RelativeDate value={notifi.date_created!} />
                    </Typography>
                  </Box>
                }
                secondary={notifi.body}
              />
              <IconButton onClick={() => markRead(notifi.id!)}>
                <Check />
              </IconButton>
            </MenuItem>
          </Collapse>
        ))}
      </TransitionGroup>
      {data.length === 0 && (
        <MenuItem sx={{ opacity: 0.7, pointerEvents: "none" }}>
          You have no new notifications
        </MenuItem>
      )}
    </>
  );
}
