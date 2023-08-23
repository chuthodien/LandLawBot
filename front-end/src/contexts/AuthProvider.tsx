import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';
import { AuthContext, IUserInfo } from './Auth';
import { logoutAPI } from 'service/api/api';

const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const history = useHistory();
  const [user, setUser] = useState<IUserInfo | undefined>(
    JSON.parse(sessionStorage.getItem('user') || '{}'),
  );

  const handleLogin = (user: IUserInfo) => {
    sessionStorage.setItem('user', JSON.stringify(user));
    setUser(user);
  };

  const handleLogout = async () => {
    try {
      await logoutAPI();
    } catch (error) {
    } finally {
      setUser(undefined);
      sessionStorage.removeItem('user');
      history.push("/login")
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        handleLogin,
        handleLogout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;
