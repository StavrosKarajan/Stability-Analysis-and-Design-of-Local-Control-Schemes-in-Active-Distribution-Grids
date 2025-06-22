# hash:sha256:f53f57d1840af2339df9a257ed7e1849ab38e1fea6b9ace3f67594bf21277e0c
FROM registry.codeocean.com/codeocean/miniconda3:4.5.11-python3.7-ubuntu18.04

ARG DEBIAN_FRONTEND=noninteractive

RUN pip install -U --no-cache-dir \
    flake8==3.7.8 \
    matplotlib==3.1.1 \
    pandapower==2.1.0 \
    pytest==5.2.1
