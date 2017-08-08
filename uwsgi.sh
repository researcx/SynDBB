source venv/bin/activate
source config

echo "=== Starting Server ==="
uwsgi --socket $SYNDBB_HOST:5000 --module syndbb --master --enable-threads --workers 8 --processes 8 --threads 4 --callab app
