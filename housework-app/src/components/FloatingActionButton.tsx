import { Bolt, Check, Close, Create, Star } from "@mui/icons-material";
import { SpeedDial, SpeedDialAction, SpeedDialIcon } from "@mui/material";
import { useIsLandscape } from "../utils/useIsLandscape";
import ShortcutFavourites from "./shortcuts/ShortcutFavourites";
import { useState } from "react";

export default function FloatingActionButton() {
    const isLandscape = useIsLandscape();
    const [shortcut, setShortcut] = useState<null | "favourites" | "create" | "complete">(null);
    return (
        <>
        <ShortcutFavourites open={shortcut === 'favourites'} handleClose={() => shortcut === "favourites" ? setShortcut(null) : setShortcut(shortcut)} />
        <SpeedDial ariaLabel="Shortcuts" icon={<SpeedDialIcon openIcon={<Close />} icon={<Bolt />} />} sx={{ position: 'fixed', bottom: isLandscape ? 16 : 72, right: 16 }}>
            <SpeedDialAction onClick={() => setShortcut("favourites")} icon={<Star />} tooltipTitle="Favourites" />
            <SpeedDialAction icon={<Create />} tooltipTitle="Create job" />
            <SpeedDialAction icon={<Check />} tooltipTitle="Complete job" />
        </SpeedDial>
        </>
    )
}