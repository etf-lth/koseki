#!/bin/bash

if [ ! -f "signing_key.pem" ]; then
    echo "signing_key.pem does not exist. Generating..."
    openssl genrsa -out signing_key.pem 4096
fi

cat > /etc/logrotate.d/koseki <<'EOF'
/srv/koseki/access.log {
    size 100M
    rotate 5
    missingok
    notifempty
    copytruncate
}
EOF

# jag bashar mitt huve i väggen snart
source .venv/bin/activate
gunicorn -w 1 \
    --timeout 60 \
    -b 0.0.0.0:5000 \
    --access-logfile access.log \
    --access-logformat '%(t)s %({x-forwarded-for}i)s "%(r)s" status=%(s)s size=%(b)sB time=%(L)ssec user=%({KOSEKI_USER_ID}e)s' \
    "koseki:run_prod()"