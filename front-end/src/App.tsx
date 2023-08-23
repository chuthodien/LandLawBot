import { CircularProgress, makeStyles } from "@material-ui/core";
import React from "react";
import { BrowserRouter, Redirect, Route, Switch } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./App.css";
import { AuthContext } from "./contexts/Auth";
import AuthProvider from "./contexts/AuthProvider";
import InitUserWrapper from "./templates/InitUserWrapper";

const AllCharacterPage = React.lazy(() => import("./pages/AllCharacters"));
const LoginPage = React.lazy(() => import("./pages/loginPage/LoginPage"));
const CallBackPage = React.lazy(
  () => import("./pages/loginPage/CallBackPage")
);
const CallScreenPage = React.lazy(
  () => import("./pages/callScreen/CallScreen")
);

const useStyles = makeStyles((theme) => ({
  wrapperLoading: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
}));

function App() {
  const classes = useStyles();
  return (
    <>
      <div className="App">
        <ToastContainer theme="light" />
        <React.Suspense
          fallback={
            <div className={classes.wrapperLoading}>
              <CircularProgress />
            </div>
          }
        >
          <BrowserRouter>
            <AuthProvider>
              <AuthContext.Consumer>
                {({ user }) =>
                  !user?.access_token ? (
                    <>
                      {/* <Route
                        path="/api/line/callback"
                        render={() => <CallBackPage />}
                      ></Route>
                      <Route path="/login" render={() => <LoginPage />}></Route>
                      <Route exact path="/">
                        <Redirect to="/login" />
                      </Route> */}

                      <Route
                        path="/app/call"
                        render={() => <CallScreenPage />}
                      ></Route>

                    </>
                  ) : (
                    <InitUserWrapper>
                      <Switch>
                        <Route
                          path="/call/agent/:idAgent"
                          render={() => <CallScreenPage />}
                        ></Route>
                        <Route
                          path="/profile/:id"
                          exact
                          render={() => <AllCharacterPage />}
                        ></Route>
                        <Route
                          path="/login"
                          exact
                          render={() => <LoginPage />}
                        ></Route>
                      </Switch>
                    </InitUserWrapper>
                  )
                }
              </AuthContext.Consumer>
            </AuthProvider>
          </BrowserRouter>
        </React.Suspense>
      </div>
    </>
  );
}

export default App;



