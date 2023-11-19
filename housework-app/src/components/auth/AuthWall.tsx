import { Box, CircularProgress, Grow } from "@mui/material";
import { useGetSelfQuery } from "../../services/housework/auth";
import AuthPortal from "./AuthPortal";
import { useEffect, useMemo, useState } from "react";
import UserDetails from "./UserDetails";

export default function AuthWall({
  children,
}: {
  children: JSX.Element | JSX.Element[];
}) {
  const { data, error, isLoading } = useGetSelfQuery();

  const displayType = useMemo(() => {
    if (error !== undefined && "status" in error) {
      if (error.status === 401) {
        return "login";
      } else {
        return "error";
      }
    }
    if (isLoading) return "loading";
    if (!data?.is_set_up) {
      return "profile";
    }
    return "allow";
  }, [error, isLoading, data]);

  const [doSetup, setDoSetup] = useState<boolean>(false);

  useEffect(() => {
    if (displayType === "profile") {
      setDoSetup(true);
    }
  }, [displayType, setDoSetup]);

  console.log(doSetup, displayType);
  return (
    <>
      <Grow in={isLoading}>
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          minHeight="100vh"
          minWidth="100vw"
          position="fixed"
          top="0"
          left="0"
          zIndex="modal" // or use a specific z-index value
          sx={{ background: "white" }}
        >
          <CircularProgress sx={{ width: "10vh", height: "10vh" }} />
        </Box>
      </Grow>
      {displayType === "login" && <AuthPortal />}
      {!doSetup && displayType === "allow" && children}
      {(doSetup || displayType === "profile") && (
        <UserDetails handleClose={() => setDoSetup(false)} />
      )}
      {displayType === "error" && <p>Unknown error</p>}
    </>
  );
}
