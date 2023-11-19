import { Divider, List, ListItem, ListItemButton, ListItemIcon, ListItemText } from "@mui/material";
import { useGetTeamsQuery } from "../../services/housework/teams"
import { Cottage } from "@mui/icons-material";
import { useNavigate, useParams } from "react-router-dom";

export default function MyTeamsList() {
    const {data: teams} = useGetTeamsQuery();
    const navigate = useNavigate();
    const { subsection } = useParams();
    if (!teams) return null;

    return (
        <List sx={{p: 0}}>
            <Divider />
            {teams.map(team => (
                <ListItemButton selected={team.id === subsection} key={team.id} onClick={() => navigate(`/teams/${team.id}`)} sx={{ pl: 4 }}>
                <ListItemIcon><Cottage /></ListItemIcon>
                <ListItemText>{teams[0].name}</ListItemText>
            </ListItemButton>
            ))
            
}
            <Divider />
        </List>
    )
}
