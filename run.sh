# USAGE:
# ./run.sh install - install into python virtual environment (does not currently create a virtual environment on windows)
# ./run.sh socket - run as uwsgi socket (for production use)
# ./run.sh http - run as http (for development use)
# ./run.sh windows - run as http (for development use) on windows [MUST MANUALLY `source ./config`]

for arg in "$@"
do
    if [ "$arg" == "install" ]
    then
        virtualenv --python=python3 venv
        source venv/bin/activate
        pip3 install -e .
        mkdir -p syndbb/static/data/
        mkdir -p syndbb/static/data/avatars/
        mkdir -p syndbb/static/data/emoticons/
        mkdir -p syndbb/static/data/threadimg/
        mkdir -p syndbb/static/data/threadimg/grid/
        mkdir -p syndbb/static/data/uploads/
        mkdir -p syndbb/static/data/uploads/.thumbnails
        mkdir -p logs/
        touch logs/global.log
        touch logs/summary.log
        break
    fi

    if [ "$arg" == "make-release" ]
    then
        break
    fi

    if [ "$arg" != "windows" ]
    then
        source venv/bin/activate
        source config
    fi

    echo "=== Configuration ==="
    echo "Host:" $HOST
    echo "Port:" $PORT

    echo "=== Starting Server ==="
    if [ "$arg" == "socket" ]
    then
        echo "Running in socket mode..."
        echo "Attempting to set up socket on $HOST:$PORT..."
        uwsgi --socket $HOST:$PORT --module syndbb --master --enable-threads --workers $WORKERS --processes $PROCESSES --threads $THREADS --callab app -H venv
    elif [ "$arg" == "http" ] || [ -z "$arg" ]
    then
        echo "Running in http mode..."
        flask run --host=$HOST --port=$PORT
    fi
    if [ "$arg" == "windows" ]
    then
        echo "Running in http mode (WINDOWS)..."
        flask run --host=$HOST --port=$PORT
    fi
done
