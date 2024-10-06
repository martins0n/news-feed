#!/bin/bash

# Start the first process
poetry run fastapi run server.py &

# Start the second process
poetry run streamlit run app.py &

wait -n

exit $?