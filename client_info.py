# constants for client secret info and redirects 

CLIENT_ID = '823710541896-sq5est11004asi1qbu3d5ehc7954hnrq.apps.googleusercontent.com'
CLIENT_SECRET = 'odswOXW_inMxoJnXV_pZxLzp'  # Read from a file or environmental variable in a real app
SCOPE = 'https://www.googleapis.com/auth/userinfo.profile'
# REDIRECT_URI = 'http://localhost:8080/oauth' # for when running on local, comment out when using GAE
REDIRECT_URI = 'https://hw06-wongjasp.wl.r.appspot.com/oauth' # for running on GAE, comment when using local