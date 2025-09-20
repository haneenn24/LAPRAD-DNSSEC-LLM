Build:
docker build --network=host --build-arg USERNAME=${USER} --build-arg UID=$(id -u ${USER}) -t bind9-18-31:latest .

Run:
docker run --name sp-build --rm  --privileged -v /home/${USER}:/home/${USER}  -u $(id -u ${USER}) --network=host -it bind9-18-31:latest
