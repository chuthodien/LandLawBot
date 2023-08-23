export const getLocalAccessToken = () => {
  const user = JSON.parse(sessionStorage.getItem("user") || 'null');
  return user?.access_token;
}

export const getLocalRefreshToken = () => {
  const user = JSON.parse(sessionStorage.getItem("user") || "null");
  return user?.refresh_token;
};

export const updateLocalAccessToken = (accessToken : string, refreshToken: string) => {
    let user = JSON.parse(sessionStorage.getItem("user") as string);
    user.access_token = accessToken;
    user.refresh_token = refreshToken;
    sessionStorage.setItem("user", JSON.stringify(user));
  }