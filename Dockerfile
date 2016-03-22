FROM ubuntu:14.04

# Note: FROM java and FROM r-base work too but take much longer apt-get updating

MAINTAINER Jeltje van Baren, jeltje.van.baren@gmail.com

RUN apt-get install -y \
	wget bc vim libxpm4 libXext6 libXt6 libXmu6 libXp6

RUN mkdir /home/gistic
WORKDIR /home/gistic
RUN wget ftp://ftp.broadinstitute.org/pub/GISTIC2.0/GISTIC_2_0_22.tar.gz \
	&& tar xvf GISTIC_2_0_22.tar.gz

RUN ./MCRInstaller.bin -P bean421.installLocation="/home/gistic/MATLAB_Compiler_Runtime" -silent

ADD ./run.sh /home/gistic/
	
