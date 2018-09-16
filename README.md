# Dlaravel-Alias
## D-Laravel alias for Sublime3.

This package make D-Laravel users easy to run artisan and composer command inside of the container.

alt+super+i for php artisan.

super+shift+c for composer.


## D-Laravel Requements

https://github.com/DevinY/dlaravel

Please make sure your compose version in your local machine.
version 3.2 is required.

<pre>
head docker-compose.yml
version: '3.6'
services:
#=== 網頁伺服器的container ======================
 web:
  image: nginx
  dns: 8.8.8.8
  ports:
    # 使用隨機的port 80
    - "80"
    - "443"
</pre>

You may get error when version is lower than 3.2.

ERROR: Setting workdir for exec is not supported in API < 1.35 (1.25)
