import { Box, Button, HStack, Select, Spinner } from "@chakra-ui/react";
import React, { useEffect, useRef, useState } from "react";
import { AudioDeviceConfig, ConversationConfig } from "vocode";
import MicrophoneIcon from "./MicrophoneIcon";
import AudioVisualization from "./AudioVisualization";
import { isMobile } from "react-device-detect";
import { useConversation } from "./useConversation";
import CallEndIcon from "@material-ui/icons/CallEnd";
import Flex from "./Flex/Flex";
import { CircularProgress, Typography, makeStyles } from "@material-ui/core";
import MicIcon from "@material-ui/icons/Mic";
import MicOffIcon from "@material-ui/icons/MicOff";
import VideocamIcon from "@material-ui/icons/Videocam";
import VolumeUpSharpIcon from "@material-ui/icons/VolumeUpSharp";
import CallIcon from "@material-ui/icons/Call";
import clsx from 'clsx'
import avatar from'../assets/images/avatar.png'
import { useLocation } from "react-router-dom";
import { aiAgents } from "pages/AllCharacters";
import { verifyTokenToCall } from "service/api/api";
import ModalNotification from "./Modal/ModalNotification";

const useStyles = makeStyles((theme) => ({
  root: {
    flex: 1,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    height: "100%",
  },
  container: {
    width: 400,
    height: 700,
    margin: "0 auto",
    border: "1px solid",
  },
  avatar: {
    height: "40%",
  },
  img: {
    height: "100%",
    width: "100%",
  },
  name: {
    marginTop: 20,
  },
  time: {
    marginTop: 20,
    height: 10,
  },
  iconCall: {
    height: "35%",
    paddingBottom: "60px",
    justifyContent: "center",
    alignItems: "self-end",
  },
  startCall: {
    backgroundColor: "limegreen",
    border: "1px solid limegreen",
    "&:hover": {
      opacity: "0.9",
    },
  },
  endCall: {
    backgroundColor: "red",
    border: "1px solid red",
    "&:hover": {
      opacity: "0.9",
    },
  },
  icon: {
    height: 50,
    width: 50,
    margin: "0 auto",
    alignItems: "center",
    display: "flex",
    justifyContent: "center",
    borderRadius: "50%",
    cursor: "pointer",
    "&:hover": {
      opacity: "0.7",
    },
  },
  wrapperLoading: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  pageTokenExpired: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
}));

const Conversation = () => {
  const classes = useStyles();
  const location = useLocation();
  const [hours, setHours] = useState(0);
  const [minutes, setMinutes] = useState(0);
  const [seconds, setSeconds] = useState(0);
  const intervalRef = useRef<any>(null);
  const [isCall, setIscall] = useState(false);
  const [loading, setLoading] = useState(false);
  const [hasExpired, setHasExpired] = useState(false);

  const urlParams = new URLSearchParams(window.location.search);
  const token = urlParams.get("token");
  console.log("urlParams", urlParams);
  console.log("token", token);
  console.log("hasExpired", hasExpired);

  useEffect(() => {

    if (token) {
        (async () => {
          setLoading(true)
          await verifyTokenToCall(token)
          .then(() => setHasExpired(false))
          .catch(() => setHasExpired(true))
          .finally(() => setLoading(false));
        })();
    }
  }, [token]);
  
  const { status, start, stop, analyserNode } = useConversation({
    backendUrl: process.env.REACT_APP_BASE_URL as string,
    audioDeviceConfig: {},
  });

  useEffect(() => {
    if (status === "error" || status === "idle") {
      handleStop();
      setIscall(false);
    }
  }, [status]);

  //handle call time
  const handleStart = () => {
    intervalRef.current = setInterval(() => {
      setSeconds((seconds) => {
        if (seconds === 59) {
          setMinutes((minutes) => {
            if (minutes === 59) {
              setHours((hours) => hours + 1);
              return 0;
            }
            return minutes + 1;
          });
          return 0;
        }
        return seconds + 1;
      });
    }, 1000);
  };

  const handleStop = () => {
    clearInterval(intervalRef.current);
    setSeconds(0);
    setMinutes(0)
    setHours(0)
  };

  return (
    <>
      {loading ? (
        <div className={classes.wrapperLoading}>
          <CircularProgress />
        </div>
      ) : (
        <Box className={classes.container}>
          <Box className={classes.avatar}>
            <img src={avatar} alt="avatar" className={classes.img} />
          </Box>
          {/* <Box className={classes.name}>{nameAgent}</Box> */}
          <Box className={classes.time}>
            {isCall && (
              <>
                {hours.toString().padStart(2, "0")}:
                {minutes.toString().padStart(2, "0")}:
                {seconds.toString().padStart(2, "0")}
              </>
            )}
          </Box>
          <Flex className={classes.iconCall}>
            <div
              className={clsx(classes.icon)}
              style={{ border: "1px solid gray" }}
            >
              <MicIcon />
            </div>
            {/* <MicOffIcon /> */}
            <div
              className={clsx(classes.icon)}
              style={{ border: "1px solid gray" }}
            >
              <VideocamIcon />
            </div>
            <div
              className={clsx(classes.icon)}
              style={{ border: "1px solid gray" }}
            >
              <VolumeUpSharpIcon />
            </div>
          </Flex>
          <Box>
            {!isCall ? (
              <div
                className={clsx(classes.icon, classes.startCall)}
                onClick={() => {
                  setIscall(true);
                  handleStart();
                  start();
                }}
              >
                <CallIcon
                  style={{
                    cursor: "pointer",
                    width: "30px",
                    height: "30px",
                    color: "white",
                  }}
                />
              </div>
            ) : (
              <div
                className={clsx(classes.icon, classes.endCall)}
                onClick={() => {
                  setIscall(false);
                  handleStop();
                  stop();
                }}
              >
                <CallEndIcon
                  style={{
                    cursor: "pointer",
                    width: "30px",
                    height: "30px",
                    color: "white",
                  }}
                />
              </div>
            )}
          </Box>
        </Box>
      )}
      <ModalNotification
        open={hasExpired}
        alertType="error"
        alertTitle="Error"
        messageNotification="This call has expired"
      />
      {/* {analyserNode && <AudioVisualization analyser={analyserNode} />} */}
    </>
  );
};

export default Conversation;
