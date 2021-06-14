import React, { useState } from 'react'
import clsx from 'clsx'
import { makeStyles } from '@material-ui/core/styles'
import { AppBar, CssBaseline, Button, Toolbar, Container, Grid, Paper, Typography, MenuItem, Select, ListItem } from '@material-ui/core'
import { Link as RouterLink, BrowserRouter as Router, Route, Switch } from 'react-router-dom'
import axios from 'axios'
import { ReactComponent as XRayIcon } from '../assets/x-ray.svg'
import ResultTable from './ResultTable'
import TrainingQueueTable from './TrainingQueueTable'
import ExplainerImage from './ExplainerImage'
import Attribution from './Attribution'

const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex'
  },
  toolbarIcon: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end',
    padding: '0 8px',
    ...theme.mixins.toolbar
  },
  appBar: {
    zIndex: theme.zIndex.drawer + 1,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen
    })
  },
  title: {
    flexGrow: 1
  },
  appBarSpacer: theme.mixins.toolbar,
  content: {
    backgroundColor:
      theme.palette.type === 'light'
        ? theme.palette.grey[100]
        : theme.palette.grey[900],
    flexGrow: 1,
    height: '100vh',
    overflow: 'auto'
  },
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4)
  },
  paper: {
    padding: theme.spacing(2),
    display: 'flex',
    overflow: 'auto',
    flexDirection: 'column'
  },
  fixedHeight: {
    minHeight: 700
  }
}))

export default function Main () {
  const classes = useStyles()
  const fixedHeightPaper = clsx(classes.paper, classes.fixedHeight)

  const [file, setFile] = useState({
    file: null,
    preview: null
  })
  const classifyImage = e => {
    e.preventDefault()
    console.log(file.preview)
    axios({
      method: 'post',
      url: '/v1/classifier',
      headers: {
        'Content-Type': file.file.type
      },
      data: fileData
    }).then(result => {
      setResult(result.data)
    })
  }

  /* Training Queue */
  const [selectedClass, setSelectedClass] = useState('COVID-19')
  const handleClassSelect = event => {
    setSelectedClass(event.target.value)
  }
  const [trainingQueue, setTrainingQueue] = useState([])
  const [trainingQueueIsLoading, setTrainingQueueIsLoading] = useState(false)

  const loadTrainingQueue = () => {
    axios({
      method: 'get',
      url: '/v1/training/queue'
    }).then(result => {
      setTrainingQueue(result.data)
    })
  }

  if (!trainingQueueIsLoading) {
    loadTrainingQueue()
    setTrainingQueueIsLoading(true)
  }

  const handleTrainigQueueSubmit = e => {
    e.preventDefault()
    axios({
      method: 'post',
      url: '/v1/training/queue',
      data: {
        class: selectedClass
      }
    }).then(result => {
      axios({
        method: 'post',
        url: '/v1/training/queue/' + result.data.id + '/image',
        headers: {
          'Content-Type': file.file.type
        },
        data: fileData
      }).then(result => {
        loadTrainingQueue()
      })
    })
  }

  /* Handle Image Change */
  const [result, setResult] = useState(null)
  const [fileData, setFileData] = useState()
  const handleImageChange = e => {
    e.preventDefault()
    setResult(null)

    const reader = new FileReader()
    const file = e.target.files[0]

    reader.onloadend = () => {
      setFile({
        file: file,
        preview: reader.result
      })
    }

    const dataReader = new FileReader()
    dataReader.onloadend = () => {
      setFileData(dataReader.result)
    }

    reader.readAsDataURL(file)
    dataReader.readAsArrayBuffer(file)
  }

  return (

    <Router>
      <CssBaseline />
      <AppBar
        position='absolute'
        className={clsx(classes.appBar)}
      >
        <Toolbar className={classes.toolbar}>
          <Typography
            component='h1'
            variant='h6'
            color='inherit'
            noWrap
            className={classes.title}
          >
            COVID-19 Classification and Explanation Tool
          </Typography>

          <RouterLink to='/' style={{ textDecoration: 'none' }}>
            <ListItem button>
              <Button
                variant='contained'
                component='label'
              >Classification
              </Button>
            </ListItem>
          </RouterLink>
          <RouterLink to='/curation' style={{ textDecoration: 'none' }}>
            <ListItem button>
              <Button
                variant='contained'
                component='label'
              >Model curation
              </Button>
            </ListItem>
          </RouterLink>
        </Toolbar>
      </AppBar>

      <Switch>
        <Route path='/curation'>
          <main className={classes.content}>
            <div className={classes.appBarSpacer} />
            <Container maxWidth='lg' className={classes.container}>
              <Grid container spacing={3}>
                <Grid item xs={12} md={12} lg={12}>
                  <Paper className={fixedHeightPaper}>
                    <h2>Training queue</h2>
                    <Grid container spacing={3}>
                      <Grid item xs={12} md={5} lg={5}>
                        {
                          file.preview !== null
                            ? <img src={file.preview} style={{ width: '200px' }} />
                            : (
                              <div style={{
                                width: '200px',
                                height: '200px',
                                border: '2px dotted black',
                                padding: '2px'
                              }}
                              >
                                <XRayIcon style={{
                                  width: '192px',
                                  height: '192px',
                                  opacity: '0.05'
                                }}
                                />
                              </div>
                            )
                        }
                      </Grid>
                      <Grid item xs={12} md={7} lg={7}>
                        <form onSubmit={handleClassSelect}>
                          <Button
                            variant='contained'
                            component='label'
                          >
                Select X-Ray image
                            <input
                              type='file'
                              style={{ display: 'none' }}
                              onChange={handleImageChange}
                            />
                          </Button>
                          <br />
                          <br />
                            Class:
                          <Select
                            labelId='demo-simple-select-label'
                            id='demo-simple-select'
                            value={selectedClass}
                            onChange={handleClassSelect}
                          >
                            <MenuItem value='COVID-19'>Covid-19</MenuItem>
                            <MenuItem value='NO FINDING'>No finding</MenuItem>
                          </Select>
                          <br />
                          <br />
                          <Button
                            type='submit'
                            onClick={handleTrainigQueueSubmit}
                            variant='contained'
                            disabled={file.file === null}
                          >Upload Image
                          </Button>
                        </form>
                      </Grid>
                      <Grid item xs={6} md={6} lg={6}>
                        <TrainingQueueTable queue={trainingQueue} />
                      </Grid>
                    </Grid>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={12} lg={12}>
                  <Attribution />
                </Grid>
              </Grid>
            </Container>
          </main>
        </Route>
        <Route path='/'>
          <main className={classes.content}>
            <div className={classes.appBarSpacer} />
            <Container maxWidth='lg' className={classes.container}>
              <Grid container spacing={3}>
                {/* Chart */}
                <Grid item xs={12} md={12} lg={12}>
                  <Paper className={fixedHeightPaper}>
                    <h2>Upload x-ray image:</h2>
                    <Grid container spacing={3}>
                      <Grid item xs={12} md={5} lg={5}>
                        {
                          file.preview !== null
                            ? <img src={file.preview} style={{ width: '200px' }} />
                            : (
                              <div style={{
                                width: '200px',
                                height: '200px',
                                border: '2px dotted black',
                                padding: '2px'
                              }}
                              >
                                <XRayIcon style={{
                                  width: '192px',
                                  height: '192px',
                                  opacity: '0.05'
                                }}
                                />
                              </div>
                            )
                        }
                      </Grid>
                      <Grid item xs={12} md={7} lg={7}>
                        <form onSubmit={classifyImage}>
                          <Button
                            variant='contained'
                            component='label'
                          >
                            Select X-Ray image
                            <input
                              type='file'
                              style={{ display: 'none' }}
                              onChange={handleImageChange}
                            />
                          </Button>
                          <br />
                          <br />
                          <Button
                            type='submit'
                            onClick={classifyImage}
                            variant='contained'
                            disabled={file.file === null}
                          >Upload Image
                          </Button>
                        </form>
                      </Grid>
                    </Grid>
                    <br />
                    {result !== null ? (
                      <Grid container spacing={3}>
                        <Grid item xs={12} md={4} lg={4}>
                          <ResultTable results={result.class_probabilities} />
                        </Grid>
                        <Grid item xs={12} md={4} lg={4}>
                          <ExplainerImage name='LIME' src={'/v1/explainer/lime/' + result.id} />
                        </Grid>
                        <Grid item xs={12} md={4} lg={4}>
                          <ExplainerImage name='GradCAM' src={'/v1/explainer/gradcam/' + result.id} />
                        </Grid>
                      </Grid>
                    ) : ''}
                  </Paper>
                </Grid>
                <Grid item xs={12} md={12} lg={12}>
                  <Attribution />
                </Grid>
              </Grid>
            </Container>
          </main>
        </Route>
      </Switch>
      <Container maxWidth='lg' className={classes.container} />
    </Router>

  )
}
