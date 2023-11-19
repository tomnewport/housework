import { Box, Button, Card, CardActions, CardHeader, MenuItem, Select } from "@mui/material";

import { components } from '../../services/housework/schema';
import { Check, Close, Mail } from "@mui/icons-material";
import { useRespondInvitationMutation } from "../../services/housework/teams";

export default function InvitationCard({ invitation }: {invitation: components["schemas"]["InvitationSchema"]}) {
    const [respond] = useRespondInvitationMutation();
    if (invitation.declined === false) {
        return (
            <Card sx={{  }}>
                    <CardHeader
                        avatar={<Check sx={{ opacity: 0.5 }} />}
                        title={invitation.team.name}
                        subheader={`${invitation.role} - joined`}
                    />
            </Card>
        )
    }
    return (
        <Card sx={{  }}>
                    <CardHeader
                        avatar={<Mail sx={{ opacity: 0.5 }} />}
                        title={invitation.team.name}
                        subheader={`${invitation.role} - invited by ${invitation.issuer.full_name}`}
                    />
                    <CardActions sx={{ display: 'flex', justifyContent: 'space-between'}}>
                        <Button onClick={() => respond({ invitation_id: invitation.id || 0, action: "block" })}size="small">
                            Block sender
                        </Button>
                        <Box sx={{ flexGrow: 1 }} />
                        <Button variant={invitation.declined === true ? "contained" : undefined} onClick={() => respond({ invitation_id: invitation.id || 0, action: "decline" })}size="small">
                            Decline
                        </Button>
                        <Button onClick={() => respond({ invitation_id: invitation.id || 0, action: "accept" })} size="small">
                            Accept
                        </Button>
                    </CardActions>
                </Card>
    )
}
