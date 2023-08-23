import {
  FormControl,
  TextField,
  Typography,
  makeStyles
} from '@material-ui/core';
import AddIcon from "@material-ui/icons/Add";
import RemoveIcon from "@material-ui/icons/Remove";
import axios from 'axios';
import Flex from 'components/Flex/Flex';
import ModalCommon from 'components/Modal/ModalCommon';
import { useAuth } from 'contexts/Auth';
import React, { useState } from 'react';
import { getLocalAccessToken } from 'service/token';
import { notifyFail, notifySuccess } from 'utils/notify';


const useStyles = makeStyles(() => ({
  container: {
    padding: 100,
  },
  label: {
    minWidth: 400,
    textAlign: "left",
  },
  paper: {
    padding: 20,
  },
  inputTxt: {
    minWidth: 400,
    marginRight: 20,
    width: "100%",
  },
  form: {
    // alignItems: 'center',
    display: "flex",
    flexDirection: "column",
  },
  row: {
    // marginRight: 20,
  },
  iconConversation: {
    alignItems: "center",
    display: "flex",
    justifyContent: "center",
    cursor: "pointer",
    "&:hover": {
      opacity: 0.7,
    },
  },
}));

export const initAgent = {
  name: "",
  introduction: "",
  age: "",
  firstPersonPronoun: "",
  secondPersonPronoun: "",
  activity: "",
  hobbies: "",
  occupation: "",
  speakingStyle: "",

  iconFile: null,
  pdfFile: null,
  voice: [],
  sampleDialogs: [{ content: "" }],
};

export interface IAgentInfo {
  name: string;
  introduction: string;
  age: string;
  firstPersonPronoun: string;
  secondPersonPronoun: string;
  activity: string;
  hobbies: string;
  occupation: string;
  speakingStyle: string;

  iconFile: any;
  pdfFile: any;
  voice: any[];
  sampleDialogs: { content: string }[];
}

const ModalCreateAiagent = ({
  openDetail,
  setOpenDetail,
}: {
  openDetail: boolean,
  setOpenDetail : (value: boolean) => void
}) => {
  const { user } = useAuth();
  const classes = useStyles();
  const [agent, setAgent] = useState<IAgentInfo>(initAgent);
  const [loading, setLoading] = useState(false)
  const token = getLocalAccessToken()

  // sample dialog
  function handleChange(i: number, event: any) {
    const newValues = [...agent.sampleDialogs];
    newValues[i].content = event.target.value;
    setAgent((prev) => ({ ...prev, sampleDialogs: newValues }));
  }

  function handleAdd() {
    const newValues = [...agent.sampleDialogs, { content: "" }];
    setAgent((prev) => ({ ...prev, sampleDialogs: newValues }));
  }

  function handleRemove(i: number) {
    const newValues = agent.sampleDialogs.filter((___, index) => index !== i);
    setAgent((prev) => ({ ...prev, sampleDialogs: newValues }));
  }

  const handleSubmit = async() => {
    setLoading(true)

    const formData = new FormData();
    formData.append("user_id", user?.id as any);
    formData.append("name", agent.name);
    formData.append("introduction", agent.introduction);
    formData.append("pdf_file", agent.pdfFile as any);
    formData.append("icon_file", agent.iconFile as any);
    // formData.append("voice_model_file", voice?.[0] as any);
    formData.append("pinecone_namespace", "" as any);
    formData.append(
      "sample_dialogs",
      JSON.stringify(agent.sampleDialogs) as any
    );
    for (let i = 0; i < agent.voice.length; i++) {
      formData.append("sample_voices", agent.voice?.[i]);
    }
    formData.append("age", agent.age as any);
    formData.append("first_person_pronoun", agent.firstPersonPronoun as any);
    formData.append("second_person_pronoun", agent.secondPersonPronoun as any);
    formData.append("activity", agent.activity as any);
    formData.append("hobbies", agent.hobbies as any);
    formData.append("occupation", agent.occupation as any);
    formData.append("speaking_style", agent.speakingStyle as any);

    axios
      .post(
        `${process.env.REACT_APP_BASE_URL}/aiagents/create/${user?.id}`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
            "access-control-allow-origin": "*",
            "ngrok-skip-browser-warning": "*",
            Authorization: `Bearer ${token}`,
          },
        }
      )
      .then((response) => {
        notifySuccess("Create agent successfully");
      })
      .catch((error) => {
        notifyFail("Create agent fail");
      })
      .finally(() => {
        setLoading(false);
      });
  };

  return (
    <>
      <ModalCommon
        open={openDetail}
        setOpen={setOpenDetail}
        title="Create Ai agent"
        handleCloseModal={() => {
          setAgent(initAgent);
        }}
        handleConfirm={handleSubmit}
      >
        <form  className={classes.form}>
          <Flex className={classes.row}>
            <TextField
              size="small"
              required
              margin="normal"
              id="name"
              value={agent.name}
              variant="outlined"
              label="Name"
              onChange={(e) =>
                setAgent((prev) => ({ ...prev, name: e.target.value }))
              }
              className={classes.inputTxt}
            />
            <TextField
              type="number"
              required
              size="small"
              margin="normal"
              id="age"
              label="Age"
              value={agent.age}
              variant="outlined"
              onChange={(e) =>
                setAgent((prev) => ({ ...prev, age: e.target.value }))
              }
              className={classes.inputTxt}
            />
          </Flex>
          <Flex>
            <TextField
              required
              size="small"
              margin="normal"
              id="age"
              label="First person pronoun"
              value={agent.firstPersonPronoun}
              variant="outlined"
              onChange={(e) =>
                setAgent((prev) => ({
                  ...prev,
                  firstPersonPronoun: e.target.value,
                }))
              }
              className={classes.inputTxt}
            />
            <TextField
              required
              size="small"
              margin="normal"
              id="age"
              label="Second person pronoun"
              value={agent.secondPersonPronoun}
              variant="outlined"
              onChange={(e) =>
                setAgent((prev) => ({
                  ...prev,
                  secondPersonPronoun: e.target.value,
                }))
              }
              className={classes.inputTxt}
            />
          </Flex>
          <Flex>
            <TextField
              required
              size="small"
              margin="normal"
              id="age"
              label="Activity"
              value={agent.activity}
              variant="outlined"
              onChange={(e) =>
                setAgent((prev) => ({
                  ...prev,
                  activity: e.target.value,
                }))
              }
              className={classes.inputTxt}
            />
            <TextField
              required
              size="small"
              margin="normal"
              id="age"
              label="Hobbies"
              value={agent.hobbies}
              variant="outlined"
              onChange={(e) =>
                setAgent((prev) => ({
                  ...prev,
                  hobbies: e.target.value,
                }))
              }
              className={classes.inputTxt}
            />
          </Flex>
          <Flex>
            <TextField
              required
              size="small"
              margin="normal"
              id="age"
              label="Occupation"
              value={agent.occupation}
              variant="outlined"
              onChange={(e) =>
                setAgent((prev) => ({
                  ...prev,
                  occupation: e.target.value,
                }))
              }
              className={classes.inputTxt}
            />
            <TextField
              required
              size="small"
              margin="normal"
              id="age"
              label="Speaking style"
              value={agent.speakingStyle}
              variant="outlined"
              onChange={(e) =>
                setAgent((prev) => ({
                  ...prev,
                  speakingStyle: e.target.value,
                }))
              }
              className={classes.inputTxt}
            />
          </Flex>
          <Flex>
            <TextField
              size="small"
              required
              multiline
              rows={4}
              margin="normal"
              id="description"
              label="Introduction"
              value={agent.introduction}
              variant="outlined"
              onChange={(e) =>
                setAgent((prev) => ({
                  ...prev,
                  introduction: e.target.value,
                }))
              }
              className={classes.inputTxt}
            />
          </Flex>
          {agent.sampleDialogs.map((value, i) => (
            <Flex>
              <TextField
                size="small"
                required
                multiline
                rows={2}
                margin="normal"
                id="conversation"
                value={value.content}
                variant="outlined"
                label="Conversation"
                onChange={(e) => handleChange(i, e)}
                className={classes.inputTxt}
                style={{ width: "92%" }}
              />
              {i === 0 && (
                <div onClick={handleAdd} className={classes.iconConversation}>
                  <AddIcon />
                </div>
              )}
              {i > 0 && (
                <div
                  onClick={() => handleRemove(i)}
                  className={classes.iconConversation}
                >
                  <RemoveIcon />
                </div>
              )}
            </Flex>
          ))}

          <Flex flexDirection="column" style={{ marginTop: 15 }}>
            <Typography className={classes.label}>Icon file</Typography>
            <FormControl margin="normal">
              {/* <label htmlFor="image_uploads">Choose images to upload (PNG, JPG)</label> */}
              {/* <InputLabel htmlFor="memoryFileLabel"></InputLabel> */}
              <input
                type="file"
                id="image_uploads"
                accept=".jpg,.fbx,.obj,.dae"
                name="image_uploads"
                onChange={(e) =>
                  setAgent((prev) => ({
                    ...prev,
                    iconFile: e.target.files?.[0] as any,
                  }))
                }
              />
            </FormControl>
          </Flex>

          <Flex flexDirection="column" style={{ marginTop: 15 }}>
            <Typography className={classes.label}>PDF file</Typography>
            <FormControl margin="normal">
              {/* <label htmlFor="image_uploads">Choose images to upload (PNG, JPG)</label> */}
              {/* <InputLabel htmlFor="memoryFileLabel"></InputLabel> */}
              <input
                type="file"
                id="samplecoives"
                accept=".pdf"
                name="samplecoives"
                onChange={(e) =>
                  setAgent((prev) => ({
                    ...prev,
                    pdfFile: e.target.files?.[0] as any,
                  }))
                }
              />
            </FormControl>
          </Flex>
          
          <Flex flexDirection="column" style={{ marginTop: 15 }}>
            <Typography className={classes.label}>Voice file</Typography>
            <FormControl margin="normal">
              {/* <InputLabel id="voiceFileLabel" htmlFor="voiceFileLabel"></InputLabel> */}
              <input
                type="file"
                multiple
                id="voiceFileLabel"
                accept="audio/*"
                name="voiceFileLabel"
                onChange={(e) =>
                  setAgent((prev) => ({
                    ...prev,
                    voice: e.target.files as any,
                  }))
                }
              />
            </FormControl>
          </Flex>

          {/* <Button
            type="submit"
            variant="contained"
            color="primary"
            style={{ marginTop: 15, maxWidth: "150px", margin: "0 auto" }}
          >
            Submit
          </Button> */}
        </form>
      </ModalCommon>
    </>
  );
};

export default ModalCreateAiagent;
