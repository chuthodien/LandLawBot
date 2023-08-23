import React, { useState, forwardRef, PropsWithChildren } from 'react';
import logo from 'assets/images/logo.svg';
import {
  Button,
  createStyles,
  FormControl,
  makeStyles,
  MenuItem,
  Select,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Theme,
  withStyles,
} from '@material-ui/core';
import Icon from 'components/Icon/Icon';
import Loading from './../Loading/Loading';

const useStyles = makeStyles((theme) => ({
  wrapperTable: {
    overflowY: 'auto',
    maxHeight: '100%',
    scrollbarWidth: 'thin',
    scrollbarColor: '#000000',
    '&::-webkit-scrollbar': {
      width: 4,
      height: 4,
    },
    '&::-webkit-scrollbar-thumb': {
      background: 'grey',
      borderRadius: 10,
    },
    [theme.breakpoints.down('xs')]: {
      minHeight: '45vh',
      maxHeight: '50vh',
    },
  },
  stickyHeader: {
    position: 'sticky',
    top: 0,
    zIndex: 1,
  },
  wrapperLoading: {
    minHeight: 400,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    [theme.breakpoints.down('xs')]: {
      minHeight: '37vh',
    },
  },
  wrapperLoadMore: {
    height: 30,
    width: '100%',
  },
}));

interface Props {
  tableRef: any;
  handleLoadMore: () => void;
  loading: boolean;
  loadMore: boolean;
  tHeader: React.ReactNode;
  children: React.ReactNode;
}

const TableCommon = (props: Props) => {
  const classes = useStyles();

  const { tableRef, handleLoadMore, loading, loadMore, tHeader, children } = props;

  const handleOnScroll = () => {
    if (!tableRef?.current) return;
    const { scrollTop, scrollHeight, clientHeight } = tableRef.current;
    if (scrollHeight - (scrollTop + clientHeight) >= 3) return;
    handleLoadMore();
  };

  return (
    <TableContainer className={classes.wrapperTable} ref={tableRef} onScroll={handleOnScroll}>
      <Table aria-label="customized table" stickyHeader style={{ minWidth: 900 }}>
        <TableHead className={classes.stickyHeader}>
          <TableRow>{tHeader}</TableRow>
        </TableHead>
        {!loading && <TableBody>{children}</TableBody>}
      </Table>
      {(loading || loadMore) && (
        <div className={loadMore ? classes.wrapperLoadMore : classes.wrapperLoading}>
          <Loading size={loadMore ? 20 : 40} />
        </div>
      )}
    </TableContainer>
  );
};

export default forwardRef(TableCommon);
