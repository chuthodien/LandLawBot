import { createContext, useContext } from 'react';

export const initUser = {
  user: {
    access_token: '',
    expires_in: 0,
    id_token: '',
    refresh_token: '',
    scope: '',
    token_type: '',
    line_id: '',
    id: 0,
    name: ''
  },
  handleLogin: () => {},
  handleLogout: () => {},
};

export interface IUserInfo {
  access_token: string;
  expires_in: number;
  id_token: string;
  refresh_token: string;
  scope: string;
  token_type: string;
  line_id: string;
  id: number;
  name: string;
}

export interface IUser {
  user: IUserInfo | undefined;
  handleLogin: (user: IUserInfo) => void;
  handleLogout: () => void;
}

export const AuthContext = createContext<IUser>(initUser);

export function useAuth() {
  return useContext(AuthContext);
}
