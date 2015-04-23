coloury
===
Simple flask/celery app that finds the dominant color of an image.

Demo: http://mblier.me/coloury/

Dependencies
---
```
pip install flask
pip install "celery[redis,auth,msgpack]"
pip install pillow numpy scipy
```

Start flask server
---
```
python coloury.py
```

Start celery worker
---
```
cd .. && celery -A coloury.tasks worker -l info
```
