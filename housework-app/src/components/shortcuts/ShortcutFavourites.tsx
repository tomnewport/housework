import { Dialog, DialogContent } from "@mui/material";
import TransitionLeft from "../TransitionLeft";
import { useShouldFullscreen } from "../../utils/mediaQuery";

export default function ShortcutFavourites({
  open,
  handleClose,
}: {
  open: boolean;
  handleClose: () => void;
}) {
  const fullscreen = useShouldFullscreen();
  return (
    <>
      <Dialog
        fullScreen={fullscreen}
        open={open}
        onClose={handleClose}
        TransitionComponent={TransitionLeft}
        fullWidth={true}
        maxWidth="sm"
      >
        <DialogContent>OK</DialogContent>
      </Dialog>
    </>
  );
}
