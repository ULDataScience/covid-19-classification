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
parser.add_argument('--training-dir-path', {
  help: 'path to training queue dir',
  required: true
})
parser.add_argument('--disable-api-cache', {
  help: 'disable api cache',
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
const uuidv4 = require('uuid').v4
const md5 = require('md5')
const fs = require('fs')

const cache = !args.disable_api_cache
  ? require('apicache').middleware('50 minutes')
  : (req, res, next) => { next() }

var uploadCache = (req, res, next) => { next() }
if (!args.disable_api_cache) {
  const instance = require('apicache').newInstance()
  instance.options({
    appendKey: (req, res) => {
      return req.method + md5(req.body)
    }
  })
  uploadCache = instance.middleware('50 minutes')
}

const { spawn } = require('child_process')
const path = require('path')
const serverProcess = spawn('python', [
  path.join(__dirname, 'server.py'),
  '-c',
  args.model_path,
  '-s',
  args.segmentation_model_path,
  '--cache-dir-path',
  args.cache_dir_path
])

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
    limit: '20mb'
  }))
})
app.use(bodyParser.json())

app.post('/v1/classifier', uploadCache, (req, res) => {
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
    res.sendFile(path.join(process.cwd(), result))
  })
})
app.get('/v1/explainer/lime/:id', cache, (req, res) => {
  const id = req.params.id
  console.log('explaining_lime', id)
  execute('explain_lime', id).then(result => {
    res.sendFile(path.join(process.cwd(), result))
  })
})

if (!fs.existsSync(path.join(__dirname, args.training_dir_path, 'queue.json'))) {
  fs.writeFileSync(path.join(__dirname, args.training_dir_path, 'queue.json'),
    JSON.stringify([], null, 2)
  )
}
const queue = JSON.parse(fs.readFileSync(path.join(__dirname, args.training_dir_path, 'queue.json')))
app.get('/v1/training/queue', (req, res) => {
  res.send(queue)
})

app.get('/v1/training/queue/:id', cache, (req, res) => {
  const items = queue.filter(item => item.id === req.params.id)
  if (items.length > 0) {
    res.send(items[0])
  } else {
    res.status(404).send('Queue item not found')
  }
})

app.get('/v1/training/queue/:id/image', cache, (req, res) => {
  res.sendFile(path.join(__dirname, args.training_dir_path, req.params.id + '.png'))
})

app.post('/v1/training/queue', (req, res) => {
  const item = req.body
  item.id = uuidv4()
  queue.push(item)
  fs.writeFileSync(path.join(__dirname, args.training_dir_path, 'queue.json'),
    JSON.stringify(queue, null, 2)
  )
  res.send(item)
})
app.post('/v1/training/queue/:id/image', (req, res) => {
  const data = req.body
  fs.writeFile(path.join(__dirname, args.training_dir_path, req.params.id + '.png'), data, err => {
    if (!err) {
      res.send('ok')
    }
  })
})

app.listen(args.port, args.host)
