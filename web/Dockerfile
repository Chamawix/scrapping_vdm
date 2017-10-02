# Set the base image to Ubuntu
FROM ubuntu

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

#Encoding utf8
ENV PYTHONIOENCODING UTF-8

# Update the sources list
RUN apt-get update

# Install basic applications
RUN apt-get install -y tar git curl net-tools build-essential

# Install Python and Basic Python Tools
RUN apt-get install -y python python-dev python-distribute python-pip

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 5000 and 80 available to the world outside this container
EXPOSE 5000
EXPOSE 80


#Entry point & command :
ENTRYPOINT ["python"]
CMD ["app.py"]