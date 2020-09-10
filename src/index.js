#!/usr/bin/env node
const { ArgumentParser } = require('argparse')
const parser = new ArgumentParser({
  description: 'Covid-19 Classification API'
})

parser.add_argument('-c', '--model-path', {
  help: 'path to classification model',
  required: true
})
parser.add_argument('-s', '--segmentation-model-path', {
  help: 'path to segmentation model',
  required: true
})
parser.add_argument('--cache-dir-path', {
  help: 'path to cache dir',
  required: true
})
parser.add_argument('--disable-api-cache', {
  help: 'path to cache dir',
  default: false,
  action: 'store_true'
})
parser.add_argument('--api-cache-lifetime', {
  help: 'api cache lifetime in minutes',
  default: 5
})
parser.add_argument('-p', '--port', {
  help: 'api port',
  default: 3000
})
parser.add_argument('-ip', '--host', {
  help: 'api host',
  default: 'localhost'
})

const args = parser.parse_args()
const cache = !args.disable_api_cache
  ? require('apicache').middleware('5 minutes')
  : (req, res, next) => { next() }

const { spawn } = require('child_process')
const serverProcess = spawn('python', [
  'server.py',
  '-c',
  args.model_path,
  '-s',
  args.segmentation_model_path,
  '--cache-dir-path',
  args.cache_dir_path
])
const uuidv4 = require('uuid').v4
const md5 = require('md5')
const path = require('path')
const fs = require('fs')

process.on('exit', (code) => {
  serverProcess.kill()
})

const hooks = {}
const execute = (method, imageId) => {
  const id = md5(method + imageId)
  hooks[id] = {
    isResolved: false
  }
  hooks[id].promise = new Promise((resolve, reject) => {
    hooks[id].resolve = resolve
    console.log(method + ' ' + imageId)
    serverProcess.stdin.write(method + ' ' + imageId + '\n')
  })
  return hooks[id].promise
}

serverProcess.stdout.on('data', data => {
  data.toString().trim().split('\n').forEach(e => {
    e = e.trim()
    const method = e.split(' ')[0]
    const imageId = e.split(' ')[1]
    const id = md5(method + imageId)
    const result = e.substr(e.indexOf(' ', e.indexOf(' ') + 1) + 1)

    console.log([method, imageId, result])
    if (id.length > 0 && hooks[id] !== undefined) {
      hooks[id].resolve(result)
      hooks[id].isResolved = true
    }
  })
})

const app = require('express')()
var bodyParser = require('body-parser');
['png', 'jpg', 'jpeg'].forEach(e => {
  app.use(bodyParser.raw({
    type: 'image/' + e,
    limit: '10mb'
  }))
})

app.post('/v1/classifier', (req, res) => {
  const id = uuidv4()
  const data = req.body
  fs.writeFile(path.join(args.cache_dir_path, id + '.png'), data, err => {
    if (!err) {
      console.log('classifing', id)
      execute('classify', id).then(result => {
        res.send({
          id: id,
          class_probabilities: JSON.parse(result),
          _links: {
            self: {
              href: '/v1/classifier/' + id
            },
            explanation_lime: {
              href: '/v1/explainer/lime/' + id
            },
            explanation_gradcam: {
              href: '/v1/explainer/gradcam/' + id
            }
          }
        })
      })
    }
  })
})

app.get('/v1/classifier/:id', cache, (req, res) => {
  const id = req.params.id
  execute('classify', id).then(result => {
    res.send({
      id: id,
      class_probabilities: JSON.parse(result),
      _links: {
        self: {
          href: '/v1/classifier/' + id
        },
        explanation_lime: {
          href: '/v1/explainer/lime/' + id
        },
        explanation_gradcam: {
          href: '/v1/explainer/gradcam/' + id
        }
      }
    })
  })
})

app.get('/v1/explainer/gradcam/:id', cache, (req, res) => {
  const id = req.params.id
  console.log('explaining_gradcam', id)
  execute('explain_gradcam', id).then(result => {
    res.sendFile(path.join(__dirname, result))
  })
})
app.get('/v1/explainer/lime/:id', cache, (req, res) => {
  const id = req.params.id
  console.log('explaining_lime', id)
  execute('explain_lime', id).then(result => {
    res.sendFile(path.join(__dirname, result))
  })
})

app.listen(args.port, args.host)
