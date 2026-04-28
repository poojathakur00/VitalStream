VitalStream is a realtime patient monitoring system that tracks vital signs of patients in a hospital and alters medical professionals if these vital signs go out of the normal range.

We start building this project by initializing the docker-file and installing the dependencies.
Kafka- Zookeeper- Postgres are loaded in docker-compose.yml in the root directory.
Load the container images from docker registry and declare the ports. 
Create a custom generator container that simulates a hospital environment by creating patient data.

Run the containers to check if the setup works.
Command : docker-compose up --build

Once the containers have been built successfully, start the containers.
Command: docker-compose up -d

Create generator scripts to generate patient data. In folder generator, create src, tests, Dockerfile and requirements.txt
In a real hospital sceanario, there would be multiple sensors attached to a patient that monitors the data per second.

Dockerfile is for starting that particular container.
In the src directory, 