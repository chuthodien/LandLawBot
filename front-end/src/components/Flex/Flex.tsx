import React from 'react';
import { Box, BoxProps } from '@material-ui/core';

const Flex = (props: BoxProps & { gap?: string | number }) => (
  <Box
    display="flex"
    {...props}
    style={{ ...(props.style || {}), gap: props.style?.gap || props.gap }}
  >
    {props.children}
  </Box>
);
export default Flex;
