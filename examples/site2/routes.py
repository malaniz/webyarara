from yarara.routes import Router
from controllers import *

router = Router()
router.add('/', controller=index)

