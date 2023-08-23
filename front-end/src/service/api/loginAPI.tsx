import axios from 'axios';

export const loginAPI = async (code: string) => {
  const reqConfig = {
    headers: {
      "Content-Type": "application/json",
      "ngrok-skip-browser-warning": "*",
    },
  };

  return await axios
    .post(`${process.env.REACT_APP_BASE_URL}/v1/login?code=${code}`, reqConfig)
    .then((response) => response);
};
