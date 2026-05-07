## WIR

### about 

* WIR was founded in 1934. 
* WIR created a credit system which issues credit in WIR francs to its members, with credit lines secured by members pledging assets. This ensures the currency is asset-backed. 
* The WIR franc is pegged 1:1 to the Swiss franc

WIR functions as a closed-loop ledger. Every "creation" of currency is balanced by an equal and opposite debt.
* Zero-Sum Balance: At any given moment, the sum of all positive balances in the WIR network exactly equals the sum of all negative balances (debts).
* The Ledger Entry: If Business A (with a zero balance) buys $1,000$ CHW worth of supplies from Business B, the system records:
    * Business A: $-1,000$ CHW (Debt/Liability)
    * Business B: $+1,000$ CHW (Asset/Credit)
* New Liquidity: $1,000$ "new" units of currency have now entered the circulation of the network to facilitate that trade.

### load test

```bash
$ locust
```

### configuration

For local development:

```bash
cp .env.example .env
bash run.sh
python manage.py runserver
```

## production deployment

```
$ vim /etc/systemd/system/wir.socket

[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/wir.sock

[Install]
WantedBy=sockets.target
```

```ini
$ vim /etc/systemd/system/wir.service
[Unit]
Description=Gunicorn daemon for Django
Requires=wir.socket
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/WIR
ExecStart=/var/www/WIR/env/bin/gunicorn \
    --workers 2 \
    --bind unix:/run/wir.sock \
    mysite.wsgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable wir
sudo systemctl start wir
sudo systemctl status wir
```

nginx settings:
```
$ vim /etc/nginx/sites-available/wir
server {
    listen 80;
    server_name wir.jaradtrading.com;
    location /static/ {
        alias /var/www/WIR/staticfiles/;
    }
    location / {
        proxy_pass http://unix:/run/wir.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable it:
```
sudo ln -s /etc/nginx/sites-available/wir /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```
