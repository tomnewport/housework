import { ThemeOptions, createTheme } from "@mui/material/styles";

export const themeOptions: ThemeOptions = {
  palette: {
    mode: "light",
    primary: {
      main: "#823fb5",
    },
    secondary: {
      main: "#00bd9b",
    },
  },
  typography: {
    fontSize: 12,
  },
  shape: {
    borderRadius: 4,
  },
};

export const theme = createTheme(themeOptions);
