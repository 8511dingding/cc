#!/bin/zsh

cd "/Users/jianing/Ning's Git/tiktok-product-intel" || exit 1

echo "== Local files =="
pwd
ls -la orbstack-www/ning_mac
ls -la orbstack-www/ning_mac/FastMOSS-Report | head -40
echo

echo "== Docker compose config =="
docker compose -f docker-compose.fastmoss.yml config
echo

echo "== Docker containers =="
docker ps -a --filter name=fastmoss-report
echo

echo "== Recreate container =="
docker rm -f fastmoss-report 2>/dev/null || true
docker compose -f docker-compose.fastmoss.yml up -d --force-recreate
echo

echo "== Container files =="
docker exec fastmoss-report ls -la /usr/share/nginx/html || true
docker exec fastmoss-report ls -la /usr/share/nginx/html/FastMOSS-Report || true
docker exec fastmoss-report nginx -T | sed -n '1,160p' || true
echo

echo "== HTTP checks =="
curl -i http://localhost:8090/ | sed -n '1,30p'
echo
curl -i http://localhost:8090/FastMOSS-Report/ | sed -n '1,30p'
echo

echo "Done. Press any key to close."
read -k 1
