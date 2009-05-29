from yarara.routes import Router
import controllers

router = Router()
router.add('/', controllers.test)


