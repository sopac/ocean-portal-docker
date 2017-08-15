for i in {1..10}
do
    /opt/ocean-portal/update.sh &> /opt/data/debug_$(date +%s).txt
    sleep 300
done

