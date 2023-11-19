import {
  AppBar,
  Avatar,
  Card,
  Collapse,
  Dialog,
  DialogContent,
  IconButton,
  List,
  ListItem,
  ListItemAvatar,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  useTheme,
} from "@mui/material";
import TransitionLeft from "../TransitionLeft";
import {
  ArrowBack,
  Check,
  Edit,
} from "@mui/icons-material";
import {
  GetJobByIDResponse,
  useJobCloseMutation,
} from "../../services/housework/jobs";
import { useState } from "react";
import { useShouldFullscreen } from "../../utils/mediaQuery";
import JobDelayWidget from "./JobDelayWidget";
import { TransitionGroup } from "react-transition-group";

interface JobCompleteDialogProps {
  open: boolean;
  onClose: () => void;
  job: GetJobByIDResponse;
  closeJob: () => void;
}

const colours = [
  [111, 62, 149],
  [72, 63, 181],
  [63, 148, 181],
  [63, 181, 126],
  [144, 181, 63],
  [181, 135, 63],
  [181, 96, 63],
  [181, 63, 140],
];

function getColour(idx: number, alpha: number): string {
  while (idx < 0) {
    idx += colours.length;
  }
  const [r, g, b] = colours[idx % colours.length];
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

interface ColouredVariant {
  id: number | null;
  credit: number;
  idx: number;
  colour: string;
  hoverColour: string;
  name: string;
  description: string;
}

export default function JobCompleteDialog({
  open,
  onClose,
  job,
  closeJob,
}: JobCompleteDialogProps) {
  const [delay, setDelay] = useState<number>(0);
  const [variantId, setVariantId] = useState<number | null>(null);
  const theme = useTheme();
  const fullscreen = useShouldFullscreen();
  const [editAmountOpen, setEditAmountOpen] = useState<boolean>(false);

  const [closeJobData] = useJobCloseMutation();

  async function handleClose() {
    if (!job.id) throw new Error("Job has no ID");
    await closeJobData({
      parameters: {
        path: {
          job_id: job.id,
          status: "Complete",
        },
      },
      requestBody: {
        content: {
          "application/json": {
            delay,
            variant: variantId || undefined,
          },
        },
      },
    }).unwrap();
    closeJob();
  }

  const variants = [
    ...(job.job_config?.variants || []),
    {
      id: null,
      name: "Standard",
      description: `This job is usually worth ${job.job_config?.default_credit} points.`,
      credit: job.job_config?.default_credit,
    },
  ].sort((a, b) => ((a.credit || 0) < (b.credit || 0) ? -1 : 1));

  const defaultIndex = variants.findIndex(({ id = 0 }) => id === null);

  const colouredVariants: ColouredVariant[] = variants.map((variant, idx) => ({
    id: variant.id || null,
    name: variant.name,
    credit: variant.credit || 0,
    description: variant.description,
    colour: getColour(idx - defaultIndex, 1),
    hoverColour: getColour(idx - defaultIndex, 0.75),
    idx,
  }));

  const selectedVariant = colouredVariants.find(({ id }) => id === variantId);

  return (
    <Dialog
      fullWidth={true}
      maxWidth="sm"
      fullScreen={fullscreen}
      open={open}
      onClose={onClose}
      TransitionComponent={TransitionLeft}
    >
      <AppBar sx={{ position: "relative" }}>
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            onClick={onClose}
            aria-label="close"
          >
            <ArrowBack />
          </IconButton>
          <Typography sx={{ ml: 2, flex: 1 }} variant="h6" component="div">
            Complete job
          </Typography>
        </Toolbar>
      </AppBar>
      <DialogContent>
        <Card sx={{ mt: 4 }}>
          <List sx={{ p: 0 }}>
            <TransitionGroup>
              {!editAmountOpen && (
                <Collapse>
                  <ListItem>
                    <ListItemAvatar>
                      <Avatar sx={{ background: selectedVariant?.colour }}>
                        {selectedVariant?.credit}
                      </Avatar>
                    </ListItemAvatar>
                    {variants.length > 1 ? (
                      <ListItemText
                        primary={job.name}
                        secondary={selectedVariant?.name}
                      />
                    ) : (
                      <ListItemText
                        primary={job.name}
                        secondary={`This job is worth ${selectedVariant?.credit} points`}
                      />
                    )}
                    {variants.length > 1 && (
                      <IconButton
                        onClick={() => {
                          setEditAmountOpen(true);
                        }}
                        color="primary"
                      >
                        <Edit />
                      </IconButton>
                    )}
                  </ListItem>
                </Collapse>
              )}
              {(editAmountOpen ? colouredVariants : []).map((variant) => (
                <Collapse key={variant.id}>
                  <ListItemButton
                    sx={{
                      "& .MuiTypography-body2": {
                        color: "rgba(255, 255, 255, 0.8)",
                      },
                      color: theme.palette.primary.contrastText,
                      background: variant?.colour,
                      "&:hover": { background: variant?.hoverColour },
                      "&.Mui-focusVisible": {
                        background: variant?.hoverColour,
                      },
                    }}
                    onClick={() => {
                      setVariantId(variant.id || null);
                      setEditAmountOpen(false);
                    }}
                  >
                    <ListItemAvatar>
                      <Avatar
                        sx={{
                          color: variant?.colour,
                          background: theme.palette.primary.contrastText,
                        }}
                      >
                        {variant.credit}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={variant.name}
                      secondary={variant.description}
                    />
                  </ListItemButton>
                </Collapse>
              ))}
            </TransitionGroup>
          </List>
        </Card>
        <JobDelayWidget
          status="Complete"
          delay={delay}
          setDelay={setDelay}
          job={job}
        />
        <Card sx={{ mt: 4 }}>
          <List sx={{ p: 0 }}>
            <ListItemButton
              disabled={editAmountOpen}
              onClick={handleClose}
              sx={{
                backgroundColor: theme.palette.secondary.main,
                color: "white",
                "&:hover": {
                  backgroundColor: theme.palette.secondary.main,
                },
              }}
            >
              <ListItemIcon>
                <Check sx={{ color: theme.palette.primary.contrastText }} />
              </ListItemIcon>
              <ListItemText primary="Complete" />
            </ListItemButton>
          </List>
        </Card>
      </DialogContent>
    </Dialog>
  );
}
