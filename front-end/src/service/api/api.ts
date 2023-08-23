import axios from 'axios';
import queryString from 'query-string';
import { getLocalAccessToken, getLocalRefreshToken, updateLocalAccessToken } from 'service/token';

function createAxios() {
  const axiosInstant = axios.create();

  axiosInstant.defaults.baseURL = process.env.REACT_APP_BASE_URL;
  axiosInstant.defaults.timeout = 40000;
  axiosInstant.defaults.headers = {
    "Content-Type": "application/json",
    "ngrok-skip-browser-warning": "*",
    "access-control-allow-origin": "*",
  };

  axiosInstant.interceptors.request.use(
    async (config) => {
      const token = getLocalAccessToken();
      if (token) {
        config.headers["Authorization"] = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error),
  );

  axiosInstant.interceptors.response.use(
    (response) => {
      return response;
    },
    async (error) => {
      const originalConfig = error.config;
      if (error.response.status === 401) {
        try {
          const refreshToken = getLocalRefreshToken();
          const { access_token, refresh_token } = await refreshTokenAPI(
            refreshToken
          );
          updateLocalAccessToken(access_token, refresh_token);
          return axiosInstant(originalConfig);
        } catch (error) {
          return Promise.reject(error);
        }
      }
      return Promise.reject(error);
    }
  );

  return axiosInstant;
}

export const getAxios = createAxios();

export type IPayload = queryString.StringifiableRecord | undefined;

// function handleUrl(url: string, query: queryString.StringifiableRecord | undefined) {
//   return queryString.stringifyUrl({ url: url, query });
// }

export const ApiClient = {
  // get: (url: string, payload: IPayload) => handleResult(getAxios.get(handleUrl(url, payload))),
  post: (url: string, payload: IPayload) => handleResult(getAxios.post(url, payload)),
  put: (url: string, payload: IPayload) => handleResult(getAxios.put(url, payload)),
  path: (url: string, payload: IPayload) => handleResult(getAxios.patch(url, payload)),
  delete: (url: string, payload: IPayload) => handleResult(getAxios.delete(url, { data: payload })),
};

/* Support function */
function handleResult<T>(api: Promise<T>) {
  return api
    .then((res: any) => {
      // if (res?.data?.status !== 1) {
      //   if (res?.data?.code === 403) {
      //     // Cookie.remove('SESSION_ID');
      //   }
      //   return Promise.reject(res?.data);
      // }
      return Promise.resolve(res?.data);
    })
    .catch((error) => {
      return Promise.reject(error);
    });
}

export const loginWithLine = () => {
  return handleResult(getAxios.get('/api/line/authorize'));
};

export const getAllCharacters = () => {
  return handleResult(getAxios.get('/aiagents'));
};

export const getAgentsByUserId = (userId: number) => {
  return handleResult(getAxios.get(`/aiagents/user/${userId}`));
};

export const updateAgentAPI = (agentID: number, payload: IPayload) => {
  return handleResult(getAxios.get(`/aiagents/update/${agentID}`, payload));
};

export const logoutAPI = () => {
  return handleResult(getAxios.post(`/v1/logout`));
};

export const refreshTokenAPI = (refreshToken: string) => {
  return handleResult(
    getAxios.get(`/v1/refreshToken/${refreshToken}`)
  );
};

// Webhook call
export const verifyTokenToCall = (token: string) => {
  return handleResult(getAxios.get(`/webhook/verifyTokenToCall/${token}`));
};