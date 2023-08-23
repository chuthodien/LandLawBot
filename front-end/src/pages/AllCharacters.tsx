import {
  Box,
  Button,
  Paper,
  TableCell,
  TableRow,
  Theme,
  Typography,
  createStyles,
  makeStyles,
  withStyles
} from '@material-ui/core';
import CallIcon from "@material-ui/icons/Call";
import { getAgentsByUserId } from "service/api/api";
import axios from 'axios';
import clsx from 'clsx';
import Flex from 'components/Flex/Flex';
import TableCommon from 'components/TableCommon/TableCommon';
import { useAuth } from 'contexts/Auth';
import moment from "moment";
import { useEffect, useRef, useState } from 'react';
import { useHistory } from 'react-router-dom';
import { DATE_FORMAT, EDIT_AGENT_TYPE } from "utils/util";
import ModalCreateAiagent from './modal/ModalCreateAiagent';
import EditIcon from "@material-ui/icons/Edit";
import { theme } from "theme";
import ModalEditAgent, { AiAgentEdit } from './modal/ModalEditAiagent';

export type sampleDialog = {
  id: number;
  agent_id: number;
  content: string
}

export type sampleVoice = {
  id: number;
  agent_id: number;
  file: string | File;
  type?: string;
};

export type aiAgents = {
  id: number;
  user_id: number;
  name: string;
  introduction: string;
  created_at: string;
  pdf_file: string;
  icon_file: string;
  voice_model_file: string;
  pinecone_namespace: string;
  age: string;
  first_person_pronoun: string;
  second_person_pronoun: string;
  activity: string;
  hobbies: string;
  occupation: string;
  speaking_style: string;

  sample_dialog: sampleDialog[];
  sample_voice: sampleVoice[];
};

const StyledTableCell = withStyles((theme: Theme) =>
  createStyles({
    head: {
      backgroundColor: '#121617',
      borderBottom: 'none',
      color: '#cccccc',
    },
    body: {
      fontSize: 14,
    },
  }),
)(TableCell);

const StyledTableRow = withStyles((theme: Theme) =>
  createStyles({
    root: {
      color: "#999999",
      "&:nth-of-type(odd)": {
        backgroundColor: "#1c1c21",
        position: "relative",
        "&:hover": {
          cursor: "pointer",
          opacity: 0.9,
        },
      },
      "&:nth-of-type(even)": {
        backgroundColor: "#111116",
        position: "relative",

        "&:hover": {
          cursor: "pointer",
          opacity: 0.9,
        },
      },
      "& th, td": {
        color: "#999999",
        borderBottom: "none",
      },
    },
  })
)(TableRow);

const useStyles = makeStyles((themes) => ({
  container: {
    padding: 50,
  },
  label: {
    minWidth: 220,
  },
  paper: {
    height: "80vh",
    padding: 20,
  },
  margin: {
    textAlign: "left",
    fontWeight: "bold",
  },
  table: {
    height: "70vh",
  },
  divHover: {
    position: "absolute",
    left: "2%",
  },
  iconHover: {
    cursor: "pointer",
    width: "20px",
    height: "20px",
    color: "white",
  },
  icon: {
    height: 40,
    width: 40,
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
  iconEdit: {
    marginTop: 8,
    marginRight: 8,
    backgroundColor: theme.palette.secondary.main,
    border: `1px solid ${theme.palette.secondary.main}`,
    "&:hover": {
      opacity: "0.9",
    },
  },
  startCall: {
    marginTop: 8,
    backgroundColor: "limegreen",
    border: "1px solid limegreen",
    "&:hover": {
      opacity: "0.9",
    },
  },
}));

const AllCharacters = () => {
  const classes = useStyles();
  const { user } = useAuth();
  const history = useHistory();
  const [data, setData] = useState<aiAgents[]>([]);
  const tableRef = useRef<any>(null);
  const [openModalCreate, setOpenModalCreate] = useState(false);
  const [openModalEdit, setOpenModalEdit] = useState(false);
  const [selectedRow, setSelectedRow] = useState<AiAgentEdit>();
  const [loading, setLoading] = useState(false);
  const [pdfFile, setPdfFile] = useState(null);
  const [voice, setVoiceFile] = useState(null);

  const [showId, setShowId] = useState(0);
  const [agent, setAgent] = useState<aiAgents>();

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        const data = await getAgentsByUserId(user?.id as number);
        setData(data || []);
      } catch (error) {
      } finally {
        setLoading(false);
      }
    })();
  }, [user?.id]);

  const handleEditAgent = (agent: any) => {
    if (!agent) return;
    setSelectedRow(agent);
    setOpenModalEdit(true);
  };

  const handleCallAgent = (agent: aiAgents) => {
    if (!agent) return;

    history.push(
      { pathname: `/call/agent/${agent.id}`, state: agent },
      "_blank"
    );
  };

  return (
    <>
      <Box className={classes.container}>
        <Paper className={classes.paper} elevation={2}>
          <Flex alignItems="center" justifyContent="space-between" mb={2}>
            <Typography variant="h4" className={classes.margin}>
              Ai agent management
            </Typography>
            <Button
              type="submit"
              variant="contained"
              color="primary"
              style={{ maxWidth: "150px" }}
              onClick={() => setOpenModalCreate(true)}
            >
              Create
            </Button>
          </Flex>
          <div className={classes.table}>
            <TableCommon
              tHeader={
                <>
                  <StyledTableCell style={{ width: "5%" }}>Id</StyledTableCell>
                  <StyledTableCell style={{ width: "15%" }}>
                    User id
                  </StyledTableCell>
                  <StyledTableCell style={{ width: "15%" }}>
                    Name
                  </StyledTableCell>
                  <StyledTableCell style={{ width: "20%" }}>
                    Introduction
                  </StyledTableCell>
                  <StyledTableCell style={{ width: "20%" }}>
                    Date
                  </StyledTableCell>
                  <StyledTableCell style={{ width: "20%" }}>
                    Pdf file
                  </StyledTableCell>
                  <StyledTableCell style={{ width: "20%" }}>
                    Icon file
                  </StyledTableCell>
                  <StyledTableCell style={{ width: "20%" }}>
                    Voice model file
                  </StyledTableCell>
                  <StyledTableCell style={{ width: "20%" }}>
                    Pinecone namespace
                  </StyledTableCell>
                  <StyledTableCell style={{ width: "20%" }}>
                    Age
                  </StyledTableCell>
                  <StyledTableCell style={{ width: "20%" }}>
                    First person pronoun
                  </StyledTableCell>
                  <StyledTableCell style={{ width: "20%" }}>
                    Second person pronoun
                  </StyledTableCell>
                  <StyledTableCell style={{ width: "20%" }}>
                    Activity
                  </StyledTableCell>
                  <StyledTableCell style={{ width: "20%" }}>
                    Hobbies
                  </StyledTableCell>
                  <StyledTableCell style={{ width: "20%" }}>
                    Occupation
                  </StyledTableCell>
                  <StyledTableCell style={{ width: "20%" }}>
                    Speaking style
                  </StyledTableCell>
                </>
              }
              tableRef={tableRef}
              handleLoadMore={() => {}}
              loading={false}
              loadMore={false}
            >
              {data.map((row, idx) => (
                <StyledTableRow
                  key={idx}
                  onClick={() => {
                    // setOpenDetail(true);
                    // setSelectedRow(row);
                  }}
                  onMouseEnter={() => {
                    setShowId(row.id);
                  }}
                  onMouseLeave={() => setShowId(0)}
                >
                  <StyledTableCell component="th" scope="row">
                    {row.id}
                  </StyledTableCell>
                  <StyledTableCell component="th" scope="row">
                    {row.user_id}
                  </StyledTableCell>
                  <StyledTableCell component="th" scope="row">
                    {row.name}
                  </StyledTableCell>
                  <StyledTableCell component="th" scope="row">
                    {row.introduction}
                  </StyledTableCell>
                  <StyledTableCell component="th" scope="row">
                    {row?.created_at
                      ? moment(row?.created_at).format(DATE_FORMAT)
                      : "N/A"}
                  </StyledTableCell>
                  <StyledTableCell component="th" scope="row">
                    {row.pdf_file}
                  </StyledTableCell>
                  <StyledTableCell component="th" scope="row">
                    {row.icon_file}
                  </StyledTableCell>
                  <StyledTableCell component="th" scope="row">
                    {row.voice_model_file}
                  </StyledTableCell>
                  <StyledTableCell component="th" scope="row">
                    {row.pinecone_namespace}
                  </StyledTableCell>
                  <StyledTableCell component="th" scope="row">
                    {row.age}
                  </StyledTableCell>
                  <StyledTableCell component="th" scope="row">
                    {row.first_person_pronoun}
                  </StyledTableCell>
                  <StyledTableCell component="th" scope="row">
                    {row.second_person_pronoun}
                  </StyledTableCell>
                  <StyledTableCell component="th" scope="row">
                    {row.activity}
                  </StyledTableCell>
                  <StyledTableCell component="th" scope="row">
                    {row.hobbies}
                  </StyledTableCell>
                  <StyledTableCell component="th" scope="row">
                    {row.occupation}
                  </StyledTableCell>
                  <StyledTableCell component="th" scope="row">
                    {row.speaking_style}
                  </StyledTableCell>
                  {row.id === showId && (
                    <Flex className={classes.divHover}>
                      <div
                        className={clsx(classes.icon, classes.iconEdit)}
                        onClick={() => {
                          handleEditAgent(row);
                        }}
                      >
                        <EditIcon className={classes.iconHover} />
                      </div>
                      <div
                        className={clsx(classes.icon, classes.startCall)}
                        onClick={() => {
                          handleCallAgent(row);
                        }}
                      >
                        <CallIcon className={classes.iconHover} />
                      </div>
                    </Flex>
                  )}
                </StyledTableRow>
              ))}
            </TableCommon>
          </div>
        </Paper>
      </Box>
      <ModalCreateAiagent
        openDetail={openModalCreate}
        setOpenDetail={setOpenModalCreate}
      />
      <ModalEditAgent
        agent={selectedRow}
        openDetail={openModalEdit}
        setOpenDetail={setOpenModalEdit}
      />
    </>
  );
};

export default AllCharacters;
