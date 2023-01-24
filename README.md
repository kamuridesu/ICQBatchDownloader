# ICQBatchDownloader

Download all files from all chats in ICQ

## Usage

### Bare metal

Clone this repository. Run the following command:

```
pip install -r requirements.txt
```

Then export all your environment variables:

```bash
export BOT_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
export USER_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

And just run the main command:

```
python3 main.py
```

### Docker

#### Building

```
docker build --name ICQDownloader .
```

#### Running

Just run the following command:

```
docker run --rm -it -e USER_TOKEN=$USER_TOKEN -e BOT_TOKEN=$BOT_TOKEN -v $(pwd)/logs:/app/logs -v $(pwd)/downloaded:/app/downloaded -v $(pwd)/data:/app/data ICQDownloader
```

You can set the folders to be anywhere on your system.


## Options

You can specify the `TOR=enabled` environment variable to use the Tor network.
