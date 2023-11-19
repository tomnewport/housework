import { useNavigate } from "react-router-dom";
import {
  Box,
  Paper,
  BottomNavigation,
  BottomNavigationAction,
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Collapse,
  AppBar,
  Toolbar,
  Typography,
  useTheme,
} from "@mui/material";
import AssignmentIcon from "@mui/icons-material/Assignment";
import Diversity3Icon from "@mui/icons-material/Diversity3";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import SearchIcon from "@mui/icons-material/Search";
import NotificationMenu from "./notification/NotificationMenu";
import MyTeamsList from "./team/MyTeamsList";
import { useIsLandscape } from "../utils/useIsLandscape";

interface SiteNavProps {
  children: React.ReactNode;
  path: string[];
}

interface MenuItem {
  name: string;
  url: string;
  Icon: React.ElementType;
  children?: JSX.Element | JSX.Element[] | null;
}

interface NavigationItemProps {
  item: MenuItem;
  path: string[];
}

const menuItems: MenuItem[] = [
  { name: "My Jobs", url: "/jobs", Icon: AssignmentIcon },
  {
    name: "Teams",
    url: "/teams",
    Icon: Diversity3Icon,
    children: <MyTeamsList />,
  },
  { name: "Profile", url: "/profile", Icon: AccountCircleIcon },
  { name: "Search", url: "/search", Icon: SearchIcon },
];

const NavigationItem: React.FC<NavigationItemProps> = ({ item, path }) => {
  const navigate = useNavigate();
  const isSelected = `/${path[0]}` === item.url;

  return (
    <>
      <ListItemButton selected={isSelected} onClick={() => navigate(item.url)}>
        <ListItemIcon>
          <item.Icon />
        </ListItemIcon>
        <ListItemText primary={item.name} />
      </ListItemButton>
      <Collapse in={isSelected} timeout="auto" unmountOnExit>
        {item.children || null}
      </Collapse>
    </>
  );
};

const SiteNavPortrait: React.FC<SiteNavProps> = ({ children, path }) => {
  const navigate = useNavigate();
  const currentPathIndex = menuItems.findIndex(
    (item) => item.url === `/${path[0]}`,
  );

  return (
    <Box sx={{ pb: 7 }}>
      <AppBar sx={{ position: "sticky", top: 0 }}>
        <Toolbar>
          <Typography sx={{ ml: 2, flexGrow: 1 }} variant="h6" component="div">
            Housework
          </Typography>
          <NotificationMenu />
        </Toolbar>
      </AppBar>
      <Box sx={{ position: "relative " }}>{children}</Box>
      <Paper
        sx={{ zIndex: 1, position: "fixed", bottom: 0, left: 0, right: 0 }}
        elevation={3}
      >
        <BottomNavigation
          showLabels
          value={currentPathIndex}
          onChange={(event, newValue) => navigate(menuItems[newValue].url)}
        >
          {menuItems.map((item) => (
            <BottomNavigationAction
              key={item.name}
              label={item.name}
              icon={<item.Icon />}
            />
          ))}
        </BottomNavigation>
      </Paper>
    </Box>
  );
};

const SiteNavLandscape: React.FC<SiteNavProps> = ({ children, path }) => {
  const drawerWidth = 250;
  const theme = useTheme();

  return (
    <Box sx={{ pl: `${drawerWidth}px` }}>
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          "& .MuiDrawer-paper": {
            width: drawerWidth,
            boxSizing: "border-box",
            boxShadow: "0px 0px 10px rgba(0,0,0,0.5)",
            border: "none",
          },
        }}
      >
        <Toolbar
          sx={{
            backgroundColor: theme.palette.primary.main,
            color: theme.palette.primary.contrastText,
          }}
        >
          <Typography sx={{ ml: 2, flex: 1 }} variant="h6" component="div">
            Housework
          </Typography>
          <NotificationMenu />
        </Toolbar>
        <List sx={{ pt: 0 }}>
          {menuItems.map((item) => (
            <NavigationItem key={item.name} item={item} path={path} />
          ))}
        </List>
      </Drawer>
      <Box sx={{ position: "relative " }}>{children}</Box>
    </Box>
  );
};

const SiteNav: React.FC<SiteNavProps> = (props) => {
  const isLandscape = useIsLandscape();
  return isLandscape ? (
    <SiteNavLandscape {...props} />
  ) : (
    <SiteNavPortrait {...props} />
  );
};

export default SiteNav;
