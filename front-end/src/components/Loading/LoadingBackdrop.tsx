import React, { useEffect, useState } from 'react';
import { Box, createStyles, makeStyles, Theme, Typography } from '@material-ui/core';
import Backdrop from '@material-ui/core/Backdrop';
import { theme } from 'theme';
import Loading from './Loading';

type Props = {
  open: boolean;
};

const useStyles = makeStyles((themes: Theme) =>
  createStyles({
    backdrop: {
      zIndex: themes.zIndex.drawer + 1,
    },
    loading: {
      marginTop: 10,
      color: theme.palette.primary.main,
    },
    title: { fontWeight: 600 },
    box: {
      boxShadow:
        '0px 11px 15px -7px rgb(0 0 0 / 20%), 0px 24px 38px 3px rgb(0 0 0 / 14%), 0px 9px 46px 8px rgb(0 0 0 / 12%);',
      backgroundColor: theme.palette.primary.contrastText,
      padding: 20,
      borderRadius: 5,
    },
  }),
);

const LoadingBackdrop = ({ open }: Props) => {
  const classes = useStyles();
  return (
    <>
      <Backdrop className={classes.backdrop} open={open}>
        <Loading size={22} className={classes.loading} style={{ color: '#38c948' }} />
      </Backdrop>
    </>
  );
};

export default LoadingBackdrop;
