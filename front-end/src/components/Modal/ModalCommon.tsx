import React from 'react';
import { createStyles, Theme, withStyles, WithStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import MuiDialogTitle from '@material-ui/core/DialogTitle';
import MuiDialogContent from '@material-ui/core/DialogContent';
import MuiDialogActions from '@material-ui/core/DialogActions';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import Typography from '@material-ui/core/Typography';
import Flex from 'components/Flex/Flex';
import Loading from 'components/Loading/Loading';

const styles = (theme: Theme) =>
  createStyles({
    root: {
      margin: 0,
      padding: theme.spacing(2),
    },
    closeButton: {
      position: 'absolute',
      right: theme.spacing(1),
      top: theme.spacing(1),
      color: theme.palette.grey[500],
    },
  });

export interface DialogTitleProps extends WithStyles<typeof styles> {
  id: string;
  children: React.ReactNode;
  onClose: () => void;
}

const DialogTitle = withStyles(styles)((props: DialogTitleProps) => {
  const { children, classes, onClose, ...other } = props;
  return (
    <MuiDialogTitle disableTypography className={classes.root} {...other}>
      <Typography variant="h6">{children}</Typography>
      {onClose ? (
        <IconButton aria-label="close" className={classes.closeButton} onClick={onClose}>
          <CloseIcon />
        </IconButton>
      ) : null}
    </MuiDialogTitle>
  );
});

const DialogContent = withStyles((theme: Theme) => ({
  root: {
    padding: theme.spacing(2),
  },
}))(MuiDialogContent);

const DialogActions = withStyles((theme: Theme) => ({
  root: {
    margin: 0,
    padding: theme.spacing(2),
  },
}))(MuiDialogActions);

interface Props {
  title: string;
  open: boolean;
  setOpen: (v: boolean) => void;
  containerStyle?: React.CSSProperties;
  children: React.ReactNode;
  handleCloseModal: () => void;
  handleConfirm: () => void;
  disableBtnConfirm?: boolean;
  loadingConfirm?: boolean;
}

export default function CustomizedDialogs({
  title,
  open,
  setOpen,
  containerStyle = {},
  children,
  handleCloseModal,
  handleConfirm,
  disableBtnConfirm = false,
  loadingConfirm = false
}: Props) {
  const handleClose = () => {
    handleCloseModal();
    setOpen(false);
  };

  return (
    <div>
      <Dialog
        onClose={handleClose}
        aria-labelledby="customized-dialog-title"
        open={open}
        fullWidth={true}
        maxWidth="lg"
        style={{ maxHeight: "calc(100% - 100px)" }}
      >
        <DialogTitle id="customized-dialog-title" onClose={handleClose}>
          {title}
        </DialogTitle>
        <DialogContent dividers>{children}</DialogContent>
        <DialogActions>
          <Flex marginRight={2}>
            <Button onClick={handleClose} color="secondary" variant="contained">
              Close
            </Button>
            <Button
              variant="contained"
              color="primary"
              style={{
                maxWidth: "150px",
                marginLeft: 10,
                // backgroundColor: "#2196f3",
              }}
              onClick={async () => {
                handleConfirm();
              }}
              disabled={disableBtnConfirm}
            >
              {loadingConfirm ? <Loading size={22} style={{ color: 'white'}}/> : "Submit"}
            </Button>
          </Flex>
        </DialogActions>
      </Dialog>
    </div>
  );
}
