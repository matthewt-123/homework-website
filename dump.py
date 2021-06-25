#!/usr/bin/env python3
import requests
url = 'https://matthewshomeworkapp.herokuapp.com/refresh/feq8QLZjDmWdmJ8dE5fpPyrfzcYrzEGFthVASVz6AkHyWr3FtNkrX8XTP7LRA2EpyypSxq4nwSngHRKnBaDfrC3Ku7x9TqT9aDc9KgbuUpnG8cqKfVFkn8BdsHVH6rJpTQ6GebpEF6zYpQKGRQf2bKBqd25ambNYarwTKY67ddVQmCpBw75NHP9cVu7m4aS5K5ua9EAtRwhwEuBDKQcfPqGujvuzXxRKebUpzRbTuvHEWqpbj7ck5Rsw28dUg98e'

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cookie': 'csrftoken=FLXpckmpCatqzhlbhRBQqSyQXRSvBRZEhVvFI9qUkMWrrp7Lwn0UsWkt4KptKHZg; sessionid=7kztxpfkesfqp8i5rcq5wxqeh95iakiq;',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36',
    'Referer': 'https://matthewshomeworkapp.herokuapp.com/login?next=/',
    'Origin': 'https://matthewshomeworkapp.herokuapp.com',
    'Host': 'matthewshomeworkapp.herokuapp.com',
}


requests.get(url, headers=headers)
