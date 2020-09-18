# covid-19-classification
![Web Interface Screenshot](assets/web-interface-1.png "Web Interface")
## Install
```
pip install -r requirements.txt
npm install
cd src/frontend
npm install
```

## Usage
1. Start the backend/API:
    ```
    $ node src/index
    usage: index [-h] -c MODEL_PATH -s SEGMENTATION_MODEL_PATH --cache-dir-path
                CACHE_DIR_PATH [--disable-api-cache]
                [--api-cache-lifetime API_CACHE_LIFETIME] [-p PORT] [-ip HOST]

    Covid-19 Classification API

    optional arguments:
      -h, --help            show this help message and exit
      -c MODEL_PATH, --model-path MODEL_PATH
                            path to classification model
      -s SEGMENTATION_MODEL_PATH, --segmentation-model-path SEGMENTATION_MODEL_PATH
                            path to segmentation model
      --cache-dir-path CACHE_DIR_PATH
                            path to cache dir
      --disable-api-cache   path to cache dir
      --api-cache-lifetime API_CACHE_LIFETIME
                            api cache lifetime in minutes
      -p PORT, --port PORT  api port
      -ip HOST, --host HOST
                            api host
    ```
2. Start the frontend:
    ```
    cd src/frontend
    npm start
    ```

Python worker interface:

```
$ ./src/server.py
usage: server.py [-h] -c MODEL_PATH -s SEGMENTATION_MODEL_PATH
                 --cache-dir-path CACHE_DIR_PATH

Covid-19-Classification Server

The server accepts messages in the form of
"command image_id" e.g. "explain_lime f00091ff-cb7a"
on stdin. Once a command finished, the server
replies with the same message on stdout, 
followed by optional response parameters.
Allowed message types are: "classify", 
"explain_lime" and "explain_gradcam". 

The images have to be located in
"CACHE_DIR_PATH/IMAGE_ID.png".

optional arguments:
  -h, --help            show this help message and exit
  -c MODEL_PATH, --model-path MODEL_PATH
                        path to classification model
  -s SEGMENTATION_MODEL_PATH, --segmentation-model-path SEGMENTATION_MODEL_PATH
                        path to segmentation model
  --cache-dir-path CACHE_DIR_PATH
                        path to segmentation model

```
classify a single image:
```
echo "classify f00091ff-cb7a" | ./src/server.py
```

## Attributions

Icon made by [Freepik](https://www.flaticon.com/de/autoren/freepik) from [www.flaticon.com](https://www.flaticon.com/de/)