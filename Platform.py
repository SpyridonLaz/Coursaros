from pathlib import Path

from edx.Urls import EdxUrls as const


class Platform(const):
    _headers = {
        'Host': const.HOSTNAME,
        'accept': '*/*',
        'x-requested-with': 'XMLHttpRequest',
        'user-agent': None,
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': const.PROTOCOL_URL,
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': const.LOGIN_URL,
        'accept-language': 'en-US,en;q=0.9',
    }

