docker exec -it oceanportaldocker_oceanportal_1 bash -c "cd /ocean-portal &&  python setup.py install --root=/opt/ocean-portal/"
docker cp js/comp/datepick oceanportaldocker_oceanportal_1:/opt/ocean-portal/usr/local/share/portal/js/comp/
docker exec -it oceanportaldocker_oceanportal_1 bash -c "chmod 777 -R /opt/data/"

