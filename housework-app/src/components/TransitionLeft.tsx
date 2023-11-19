import { Slide } from "@mui/material";
import React from "react";
import { TransitionProps } from "react-transition-group/Transition";

const TransitionLeft = React.forwardRef(function Transition(
  props: TransitionProps & {
    children: React.ReactElement;
  },
  ref: React.Ref<unknown>,
) {
  return <Slide direction="left" ref={ref} {...props} />;
});

export default TransitionLeft;
