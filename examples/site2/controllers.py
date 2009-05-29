from yarara.templates import render 
from datetime import datetime

def index(req):
    t = datetime.now()
    return render('index.html', locals())


