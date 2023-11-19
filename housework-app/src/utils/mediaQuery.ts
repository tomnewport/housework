import { useMediaQuery, useTheme } from "@mui/material";

export function useShouldFullscreen() {
  const theme = useTheme();
  const matchesWidth = useMediaQuery(theme.breakpoints.up("sm"));
  const matchesHeight = useMediaQuery("(min-height:400px)");
  return !(matchesWidth && matchesHeight);
}
