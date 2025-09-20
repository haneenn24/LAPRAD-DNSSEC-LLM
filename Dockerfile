FROM ubuntu:24.04

RUN apt update && apt install -y software-properties-common 


RUN add-apt-repository ppa:isc/bind-esv && \
	apt update && apt install -y sudo debootstrap uuid-runtime iputils-ping bind9 dnsutils tcpdump man-db tshark \
	gcc-12 build-essential libncurses-dev bison flex libssl-dev libelf-dev fakeroot \
	bash-completion zstd

RUN apt install -y vim 

ARG UID=1000
ARG USERNAME=user

RUN userdel -r -f ubuntu
RUN useradd -l -u ${UID} -g users ${USERNAME}

RUN mkdir -p /etc/sudoers.d && echo "${USERNAME} ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/${USERNAME}

CMD /bin/bash

