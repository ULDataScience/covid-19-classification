import React from 'react'
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper
} from '@material-ui/core'

export default function TrainingQueueTable (props) {
  const queue = props.queue

  return (
    <TableContainer component={Paper}>
      <Table aria-label='simple table'>
        <TableHead>
          <TableRow>
            <TableCell align='right'>#</TableCell>
            <TableCell>Class</TableCell>
            <TableCell align='right'>X-Ray Image</TableCell>´
          </TableRow>
        </TableHead>
        <TableBody>
          {queue.map((obj, id) => (
            <TableRow key={'row' + id}>
              <TableCell align='right'>{id}</TableCell>
              <TableCell component='th' scope='row'>
                {obj.class}
              </TableCell>
              <TableCell align='right'>
                <img
                  src={'/v1/training/queue/' + obj.id + '/image'}
                  style={{ width: '150px' }}
                />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  )
}
