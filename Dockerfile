FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
        nano python3-pip python3-mock libpython3-dev \
        libpython3-all-dev python-is-python3 wget \
        software-properties-common sudo \
    && sed -i 's/# set linenumbers/set linenumbers/g' /etc/nanorc \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install pip -U \
    && pip install -U onnx \
    && pip install -U onnx-simplifier \
    && python3 -m pip install -U onnx_graphsurgeon --index-url https://pypi.ngc.nvidia.com \
    && pip install -U simple_onnx_processing_tools \
    && pip install -U onnx2tf \
    && pip install tensorflow==2.10.0 \
    && python -m pip cache purge

ENV USERNAME=user
RUN echo "root:root" | chpasswd \
    && adduser --disabled-password --gecos "" "${USERNAME}" \
    && echo "${USERNAME}:${USERNAME}" | chpasswd \
    && echo "%${USERNAME}    ALL=(ALL)   NOPASSWD:    ALL" >> /etc/sudoers.d/${USERNAME} \
    && chmod 0440 /etc/sudoers.d/${USERNAME}
USER ${USERNAME}
ARG WKDIR=/workdir
WORKDIR ${WKDIR}
RUN sudo chown ${USERNAME}:${USERNAME} ${WKDIR}

RUN echo 'export CUDA_VISIBLE_DEVICES=-1' >> ${HOME}/.bashrc \
    && echo 'export TF_CPP_MIN_LOG_LEVEL=3' >> ${HOME}/.bashrc
