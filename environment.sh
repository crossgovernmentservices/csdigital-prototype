source ./environment-private.sh 2>/dev/null
export SETTINGS='application.config.DevelopmentConfig'
export SASS_PATH='.'
export SECRET_KEY='local-dev-not-secret'
export SECURITY_PASSWORD_HASH='bcrypt'
export MONGO_URI='mongodb://localhost:27017/xgs'
export EMAIL_DOMAIN='mylog.civilservice.digital'
