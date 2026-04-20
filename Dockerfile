FROM python:3.9-slim
RUN apt-get update && apt-get install -y smbclient && rm -rf /var/lib/apt/lists/*
RUN pip install requests pycryptodome
COPY exploit_smb.py /exploit.py
ENTRYPOINT ["python", "/exploit.py"]
