from aiohttp import web
from os import environ

app = web.Application()
web.run_app(app, port=environ.get('PORT'))