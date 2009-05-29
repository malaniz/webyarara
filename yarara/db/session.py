import elixir
import md5, base64, string

def commit():
    return elixir.session.flush()

def encode_cookie(secret, user, field, roles):
    import md5, base64, string
    str_roles = ""
    for x in roles:
        str_roles += ",%s" % x 
    str_roles = str_roles[1:]
    digest = md5.new(secret + user + secret).hexdigest()
    token = user + '/' + digest + '/' + str_roles
    print token
    print 
    token = string.strip(base64.encodestring(token))
    return '%(field)s=%(token)s; path=/' % locals()

def decode_cookie(cookie):
    import md5, base64, string
    data = cookie.split(';')
    d = dict()
    for x in data:
        y = x.split('=', 1)
        d[y[0].strip()] = y[1].strip()
    return d

