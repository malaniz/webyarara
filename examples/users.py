from yarara import *
from md5 import md5
import datetime
# PLUGABLE

#settings 
DEFAULT_URL='/movimiento'


# BEGIN User account app -----------------------------------------------------

User = model('User',
  login      = 'string',
  password   = 'string',
  role       = 'unicode',
#  email      = 'string',
  __repr__   = lambda self: '%s' % self.login,
)


@route('/login')
def login(web):
  if web.input().has_key('user') and web.input().has_key('password'):
    user = find(User).filter_by(
        login=web.input('user'),
        password=md5(web.input('password')).hexdigest()
    )
    if len(list(user)) > 0:
      user = user[0]
      web.session['user_id'] = user.id
      if user.role == 'admin': web.session['is_admin'] = True
      web.session.save()
      redirect(DEFAULT_URL)
    else: user = None
    messages = ['Usuario y/o contrase&ntilde;a incorrectos']
  return template('account/login.html', locals())

@route('/logout')
def logout(web):
  web.session.invalidate()
  return redirect('/login')

#decorator
def login_required(view):
  def _wrapper(web, **kw):
    if 'user_id' in web.session: 
      return view(web, **kw)
    else:
      return redirect('/login')
  return _wrapper


def admin_required(view):
  def _wrapper(web, **kw):
    if 'is_admin' in web.session: 
      return view(web, **kw)
    else:
      return redirect('/login')
  return _wrapper
#
#end deco


@route('/change-password')
@login_required
def change(web):
  user = find(User).filter_by(id=web.session['user_id'])[0]
  _input = web.input()
  if 'new' in _input and 'renew' in _input:
    if _input['new'] == _input['renew']:
      user.password=md5(_input['new']).hexdigest()
      user.save()
      messages = ['Tu clave ha sido actualizada']
    else:
      messages = [u'Error al ingresar de nuevo tu contrase&ntilde;a']
  return template('account/change-password.html', locals())

# END   User account app -----------------------------------------------------


@route('/init')
def init(web):
    User(login='admin', password=md5('admin1234').hexdigest(),
        codename='admin', role='admin').save()
    return " Todo listo !!!"


