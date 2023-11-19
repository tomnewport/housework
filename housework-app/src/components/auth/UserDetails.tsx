import {
  Container,
  Stepper,
  Step,
  StepButton,
  StepContent,
  TextField,
  Typography,
  Box,
  Button,
  CardHeader,
  Card,
} from "@mui/material";
import { useGetInvitationsQuery } from "../../services/housework/teams";
import { useCallback, useState } from "react";
import {
  UpdateSelfRequest,
  useGetSelfQuery,
  useUpdateSelfMutation,
} from "../../services/housework/auth";
import { useForm } from "react-hook-form";
import InvitationCard from "../team/InvitationCard";
import { Info } from "@mui/icons-material";

export default function UserDetails({
  handleClose,
}: {
  handleClose: () => void;
}) {
  const { data: invitations = [] } = useGetInvitationsQuery(undefined, {
    pollingInterval: 30000,
  });
  const [step, setStep] = useState<number>(0);

  const [updateSelf] = useUpdateSelfMutation();
  const { data: selfData } = useGetSelfQuery();
  const [newPassword, setNewPassword] = useState<string>("");

  const { register, getValues, watch } =
    useForm<UpdateSelfRequest>({
      defaultValues: {
        full_name: selfData?.full_name,
        short_name: selfData?.short_name,
      },
    });

  const save = useCallback(async () => {
    await updateSelf(getValues()).unwrap();
  }, [getValues, updateSelf]);
  const fullName = watch("full_name");
  const shortName = watch("short_name");

  const allDone =
    selfData?.is_set_up === true &&
    invitations.every((i) => i.declined !== null);

  return (
    <Container maxWidth="sm">
      <Typography variant="h4" sx={{ mt: 4, mb: 3 }}>
        Finish setting up your account
      </Typography>
      <Stepper nonLinear activeStep={step} orientation="vertical">
        <Step completed={Boolean(selfData?.full_name && selfData?.short_name)}>
          <StepButton onClick={() => setStep(0)}>Set your name</StepButton>
          <StepContent>
            <Typography variant="body1">
              What should we call you? You will see some examples of how these
              names will be used below.
            </Typography>
            <TextField
              sx={{ mt: 2, mb: 3 }}
              label="Full name"
              fullWidth
              {...register("full_name")}
            />
            <TextField
              label="Short name"
              fullWidth
              {...register("short_name")}
            />
            <Card sx={{ mt: 3, mb: 2 }}>
              <CardHeader
                avatar={<Info sx={{ opacity: 0.5 }} />}
                title={`Job assigned to ${fullName || "(full name)"}`}
                subheader="Full name is usually used to refer to you."
              />
            </Card>
            <Card sx={{ mt: 1, mb: 2 }}>
              <CardHeader
                avatar={<Info sx={{ opacity: 0.5 }} />}
                title={`Hi ${
                  shortName || "(short name)"
                } - you have some jobs to do!`}
                subheader="Short name is used to address you in messages."
              />
            </Card>
            <Box sx={{ mb: 2 }}>
              <div>
                <Button
                  disabled={Boolean(!shortName || !fullName)}
                  variant="contained"
                  onClick={() => save().then(() => setStep(1))}
                  sx={{ mt: 1, mr: 1 }}
                >
                  Continue
                </Button>
              </div>
            </Box>
          </StepContent>
        </Step>
        <Step completed={selfData?.has_usable_password}>
          <StepButton onClick={() => setStep(1)}>
            Set a secure password
          </StepButton>
          <StepContent>
            {!!!selfData?.has_usable_password ? (
              <>
                <TextField
                  fullWidth
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  type="password"
                  label="Set a password"
                />
                <Button
                  variant="contained"
                  onClick={() =>
                    updateSelf({ password: newPassword }).then(() => setStep(3))
                  }
                  sx={{ mt: 1, mr: 1 }}
                >
                  Set password
                </Button>
              </>
            ) : (
              <>
                <Typography variant="body1">
                  Your account has a password set.
                </Typography>
                <Button
                  variant="contained"
                  onClick={() => setStep(2)}
                  sx={{ mt: 1, mr: 1 }}
                >
                  Next
                </Button>
              </>
            )}
          </StepContent>
        </Step>
        {(invitations?.length || 0) >= 1 ? (
          <Step completed={invitations.every((i) => i.declined !== null)}>
            <StepButton onClick={() => setStep(2)}>Join teams</StepButton>
            <StepContent>
              {(invitations || []).map((invitation) => (
                <InvitationCard invitation={invitation} />
              ))}
              {invitations.every((i) => i.declined !== null) && (
                <Button
                  variant="contained"
                  onClick={() => setStep(3)}
                  sx={{ mt: 1, mr: 1 }}
                >
                  Next
                </Button>
              )}
            </StepContent>
          </Step>
        ) : null}
        <Step completed={allDone}>
          <StepButton
            onClick={() => setStep((invitations?.length || 0) >= 1 ? 3 : 2)}
          >
            Confirm
          </StepButton>
          <StepContent>
            {allDone ? (
              selfData.approved ? (
                <>
                  <Typography gutterBottom variant="body1">
                    Your account is set up and approved for use. Welcome to
                    Housework.
                  </Typography>
                  <Button variant="contained" onClick={handleClose}>
                    Finish
                  </Button>
                </>
              ) : (
                <>
                  <Typography gutterBottom variant="body1">
                    Your account is set up, but still needs to be approved. Get
                    your account approved with an invitation from an existing
                    team, or email support@tdn.sh to create your own team.
                  </Typography>
                  <Button variant="contained" onClick={handleClose}>
                    Finish
                  </Button>
                </>
              )
            ) : (
              <Typography variant="body1">
                Account setup is not yet complete. Please check the steps above.
              </Typography>
            )}
          </StepContent>
        </Step>
      </Stepper>
    </Container>
  );
}
