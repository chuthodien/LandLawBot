// import { useAuth } from 'contexts/Auth';
import { makeStyles } from '@material-ui/core';
import React from 'react';
import { Redirect } from 'react-router-dom';
import { useAuth } from '../contexts/Auth';
import MenuAppBar from './MenuAppBar';

const useStyles = makeStyles(() => ({
  container: {},
  children:{
    marginTop: 70
  }
}));

const InitUserWrapper = ({ children }: { children: React.ReactNode }) => {
  const { user } = useAuth();
  const classes = useStyles();

  if (!user?.access_token) {
    return (
      <Redirect
        to={{
          pathname: `/login`,
        }}
      />
    );
  }


  return (
    <div className={classes.container}>
      <MenuAppBar />
      <div className={classes.children}>{children}</div>
    </div>
  );
};

export default InitUserWrapper;
