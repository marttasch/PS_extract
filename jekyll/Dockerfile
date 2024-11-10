FROM ubuntu:24.04

# Install Dependencies
RUN apt update
RUN apt install -y ruby-full
RUN apt install -y build-essential zlib1g-dev
RUN gem install jekyll bundler

ENV HOME=/home/user
ENV GEM_HOME=/home/user/gems
ENV PATH=/home/user/gems/bin:$PATH
RUN mkdir -p /home/user/

#RUN ruby --version
#RUN gem --version

# install git
RUN apt install -y git
RUN git config --global --add safe.directory /srv/jekyll

# Expose the default Jekyll port
EXPOSE 4000
EXPOSE 35729 

#RUN jekyll new my-awesome-site
#RUN ls /home/user
#WORKDIR /home/user/my-awesome-site

# Set the working directory inside the container
WORKDIR /srv/jekyll
# set permissions
RUN chown -R ${PUID}:${PGID} /srv/jekyll

# Define the default command to run when starting the container
CMD [ "bundle", "exec", "jekyll", "serve", "--force_polling", "-H", "0.0.0.0", "-P", "4000" ]
