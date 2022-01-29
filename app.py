import os

import requests
from dotenv import load_dotenv
from flask import Flask, request, Response

load_dotenv('.env')

app = Flask(__name__)


def download_file(url: str) -> Response:
    r = requests.get(url, stream=True)
    return Response(r.iter_content(chunk_size=10 * 1024), content_type=r.headers['Content-Type'])


def proxy(url: str) -> Response:
    resp = requests.request(
        method=request.method,
        url=url,
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
    )

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    response = Response(resp.content, resp.status_code, headers)
    return response


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def url_dispatcher(path: str):
    url = request.url.replace(request.host_url, os.getenv('SITE_URL'))
    if path.startswith('b/'):
        return download_file(url)
    else:
        return proxy(url)


if __name__ == '__main__':
    app.run()
