from fastapi import APIRouter
from app.api.v1 import users, enterprises, roles, resources, permissions, debug

router = APIRouter(prefix="/v1")

router.include_router(users.router)
router.include_router(enterprises.router)
router.include_router(roles.router)
router.include_router(resources.router)
router.include_router(permissions.router)
router.include_router(debug.router) 