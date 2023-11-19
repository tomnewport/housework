import {
  DoneAll,
  Notifications,
  NotificationsOff,
  Settings,
} from "@mui/icons-material";
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  IconButton,
  ListItemIcon,
  Menu,
  MenuItem,
  MenuList,
} from "@mui/material";
import { useState, MouseEvent } from "react";
import {
  useMarkAllNotificationsAsReadMutation,
} from "../../services/housework/notifications";
import useNotificationPermission from "./useNotificationPermission";
import UnreadList from "./UnreadList";

export default function NotificationMenu() {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleMenu = (event: MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const notificationPermission = useNotificationPermission();
  const [markAllAsRead] = useMarkAllNotificationsAsReadMutation();

  return (
    <>
      {notificationPermission === "default" && (
        <Dialog fullWidth={true} maxWidth="sm" open={true}>
          <DialogTitle>Set notification preferences</DialogTitle>
          <DialogContent></DialogContent>
          <DialogActions>
            <Button onClick={() => Notification.requestPermission()}>
              Set
            </Button>
          </DialogActions>
        </Dialog>
      )}
      <IconButton onClick={handleMenu} color="inherit">
        {notificationPermission === "granted" ? (
          <Notifications />
        ) : (
          <NotificationsOff />
        )}
      </IconButton>
      <Menu
        id="menu-appbar"
        anchorEl={anchorEl}
        anchorOrigin={{
          vertical: "top",
          horizontal: "right",
        }}
        keepMounted
        transformOrigin={{
          vertical: "top",
          horizontal: "right",
        }}
        open={Boolean(anchorEl)}
        onClose={handleClose}
      >
        <MenuList sx={{ p: 0 }}>
          <MenuItem onClick={() => markAllAsRead()}>
            <ListItemIcon>
              <DoneAll />
            </ListItemIcon>{" "}
            Mark all as read
          </MenuItem>
          <MenuItem>
            <ListItemIcon>
              <Settings />
            </ListItemIcon>{" "}
            Preferences
          </MenuItem>
          <Divider />
          <UnreadList />
        </MenuList>
      </Menu>
    </>
  );
}
