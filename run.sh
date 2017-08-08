source venv/bin/activate
source config
echo "=== Configuration ==="
echo "HOST:" $SYNDBB_HOST
echo "DATABASE:" $SYNDBB_DB
echo "SECRET:" $SYNDBB_SECRET
echo "HASH:" $SYNDBB_HASH

echo ""

echo "=== Starting Server ==="
flask run --host=$SYNDBB_HOST
