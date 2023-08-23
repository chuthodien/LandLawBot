import { CircularProgress, makeStyles } from '@material-ui/core';
import { loginAPI } from 'service/api/loginAPI';
import { useAuth } from 'contexts/Auth';
import { useEffect } from 'react';
import { Redirect, useHistory } from 'react-router-dom';
import url from 'url';

const useStyles = makeStyles((theme) => ({
  wrapperLoading: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
}));

const CallBackPage = () => {
  const classes = useStyles();
  const history = useHistory();
  const { handleLogin, user } = useAuth();

  if (user?.access_token) {
    <Redirect
      to={{
        pathname: `/profile/${user.id}`,
      }}
    />;
  }

  const getAccessToken = async (callbackURL: string) => {
    const urlParts = url.parse(callbackURL, true);
    const query = urlParts.query;
    const hasCodeProperty = Object.prototype.hasOwnProperty.call(query, 'code');

    if (hasCodeProperty) {
      if (typeof query.code === 'string') {
        try {
          const result = await loginAPI(query.code || '');
          if (result?.data) {
            handleLogin(result?.data);
            history.push(`/profile/${result?.data?.id}`);
          }
        } catch (error) {
          <Redirect
            to={{
              pathname: `/login`,
            }}
          />;
        }
      }
    }
  };

  useEffect(() => {
    (async () => {
      await getAccessToken(window.location.href);
    })();
  });

  return (
    <div className={classes.wrapperLoading}>
      <CircularProgress />
    </div>
  );
};

export default CallBackPage;
