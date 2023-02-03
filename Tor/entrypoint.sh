service tor start
service tor status
while [[ "$(curl --socks5 '127.0.0.1:9050' --connect-timeout 15 --max-time 30 -Ls -o /dev/null -w ''%{http_code}'' https://check.torproject.org)" != "200" ]]; do
    echo "Waiting Tor..."
    service tor start
    service tor status
    sleep 5
done
python main.py
