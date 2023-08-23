import React from "react";
import Dialog from "@material-ui/core/Dialog";
import DialogContent from "@material-ui/core/DialogContent";
import DialogContentText from "@material-ui/core/DialogContentText";
import { Alert, AlertTitle } from "@material-ui/lab";
import { Theme, Typography, createStyles, makeStyles } from "@material-ui/core";

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      width: "100%",
      "& > * + *": {
        marginTop: theme.spacing(2),
      },
    },
  })
);

export default function ModalNotification({
  open,
  setOpen,
  alertTitle,
  messageNotification,
  alertType,
}: {
  open: boolean;
  setOpen?: (value: boolean) => void;
  alertTitle?: string;
  messageNotification?: string;
  alertType: "error" | "info" | "success" | "warning";
}) {
  const classes = useStyles();
  return (
    <div style={{ width: "500px" }}>
      <Dialog
        open={open}
        onClose={() => {}}
        aria-labelledby="customized-dialog-title"
        maxWidth="sm"
        fullWidth={true}
      >
        <DialogContent className={classes.root} style={{ width: "100%" }}>
          <DialogContentText id="alert-dialog-description">
            <Alert severity={alertType}>
              <AlertTitle>
                <Typography variant="h5"> {messageNotification} </Typography>
              </AlertTitle>
            </Alert>
          </DialogContentText>
        </DialogContent>
      </Dialog>
    </div>
  );
}
