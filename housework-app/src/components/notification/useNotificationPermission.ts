import { useState, useEffect } from "react";

const useNotificationPermission = () => {
  const [permission, setPermission] = useState(Notification.permission);

  useEffect(() => {
    const handlePermissionChange = () => {
      setPermission(Notification.permission);
    };

    // Event listener for permission changes
    navigator.permissions
      .query({ name: "notifications" })
      .then((notificationPerm) => {
        notificationPerm.onchange = handlePermissionChange;
      });

    // Cleanup function to remove event listener
    return () => {
      navigator.permissions
        .query({ name: "notifications" })
        .then((notificationPerm) => {
          notificationPerm.onchange = null;
        });
    };
  }, []);

  return permission;
};

export default useNotificationPermission;
