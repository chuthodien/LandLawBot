import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import CircularProgress, { CircularProgressProps } from '@material-ui/core/CircularProgress';

const useStyles = makeStyles((theme) => ({
  root: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
  },
}));

const Loading = (props: CircularProgressProps) => {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <CircularProgress {...props} />
    </div>
  );
};

export default Loading;
