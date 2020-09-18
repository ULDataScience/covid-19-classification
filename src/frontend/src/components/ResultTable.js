import React from 'react'
import { makeStyles } from '@material-ui/core/styles'
import Table from '@material-ui/core/Table'
import TableBody from '@material-ui/core/TableBody'
import TableCell from '@material-ui/core/TableCell'
import TableContainer from '@material-ui/core/TableContainer'
import TableHead from '@material-ui/core/TableHead'
import TableRow from '@material-ui/core/TableRow'
import Paper from '@material-ui/core/Paper'

const useStyles = makeStyles({
  table: {
    minWidth: 0
  }
})
export default function ResultTable (props) {
  const classes = useStyles()
  const results = props.results
  const round = number => Math.round(number * 1000) / 1000

  return (
    <TableContainer component={Paper}>
      <Table className={classes.table} aria-label='simple table'>
        <TableHead>
          <TableRow>
            <TableCell>Class</TableCell>
            <TableCell align='right'>Probabiliy</TableCell>´
          </TableRow>
        </TableHead>
        <TableBody>
          {Object.keys(results).map(key => (
            <TableRow key={key}>
              <TableCell component='th' scope='row'>
                {key}
              </TableCell>
              <TableCell align='right'>{round(results[key])}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  )
}
