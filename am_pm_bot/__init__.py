import logging
import sys
from os import getenv
from aiohttp import web
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode

from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# Bot settings
TOKEN = getenv("API_TOKEN")
WEBHOOK_HOST = getenv('WEBHOOK_HOST', 'https://yourdomain.com')
WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = getenv('WEBHOOK_SECRET', 'my-secret')
WEBAPP_HOST = getenv('WEBAPP_HOST', '127.0.0.1')
WEBAPP_PORT = int(getenv('PORT', 5000))

router = Router()