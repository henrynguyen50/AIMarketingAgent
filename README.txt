every morning run
python scripts/getevents.py
python models/encode.py 

uvicorn backend.app:app 

then gen tweet 