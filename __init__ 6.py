from aiogram import Dispatcher
from .common import router as common_router
from .admin import router as admin_router
from .application import router as application_router
from .support import router as support_router

def register_routers(dp: Dispatcher):
    dp.include_router(common_router)
    dp.include_router(admin_router)
    dp.include_router(application_router)
    dp.include_router(support_router)
