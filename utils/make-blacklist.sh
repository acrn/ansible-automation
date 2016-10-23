#!/bin/bash

echo '---'
echo 'dns_blacklisted_domains:'
curl 'http://pgl.yoyo.org/adservers/serverlist.php?hostformat=nohtml&showintro=1&startdate%5Bday%5D=&startdate%5Bmonth%5D=&startdate%5Byear%5D=&mimetype=plaintext' \
    | sed 's/^/ - /'
