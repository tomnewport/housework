import {
  Alert,
  Box,
  Button,
  Container,
  TextField,
  Typography,
} from "@mui/material";
import { useSendOtpMutation } from "../../services/housework/auth";
import { useCallback, useState } from "react";
import OtpLogin from "./OtpLogin";

export default function AuthPortal() {
  const [sendOtp, { error: otpError }] = useSendOtpMutation();
  const [sub, setSub] = useState("");
  const [authMode, setAuthMode] = useState<"otp" | "password" | null>(null);

  const handleSendOtp = useCallback(async () => {
    try {
      await sendOtp(sub).unwrap();
      setAuthMode("otp");
    } catch (e) {}
  }, [sub, setAuthMode, sendOtp]);

  let errorText = null;
  if (otpError) {
    errorText =
      "status" in otpError && otpError.status === 422
        ? "Invalid email"
        : "Unknown error";
  }
  return (
    <Container maxWidth="sm">
      <Box my={4} textAlign="center">
        <Typography variant="h3" gutterBottom>
          Housework
        </Typography>
        <Typography variant="body1" color="textSecondary" gutterBottom>
          Housework helps you allocate and track your chores. You can sign up or
          sign in by receiving a code by email. Existing users can sign in using
          a password.
        </Typography>
        <Box my={2}>
          {authMode === null ? (
            <TextField
              value={sub}
              onChange={(e) => setSub(e.target.value)}
              fullWidth
              label="Email"
              type="email"
              variant="outlined"
            />
          ) : null}
          {errorText && (
            <Alert sx={{ mt: 2 }} severity="error">
              {errorText}
            </Alert>
          )}
          {authMode === "otp" ? (
            <OtpLogin onQuit={() => setAuthMode(null)} sub={sub} />
          ) : null}
          {authMode === null ? (
            <Button
              onClick={handleSendOtp}
              sx={{ mt: 2 }}
              fullWidth={true}
              variant="contained"
            >
              Get a code
            </Button>
          ) : null}
          {authMode === null ? (
            <Button sx={{ mt: 2, mb: 2 }} fullWidth={true}>
              Sign in with password
            </Button>
          ) : null}
        </Box>
      </Box>
    </Container>
  );
}
