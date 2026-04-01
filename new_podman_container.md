Navigate to the folder containing docker-compose.yml in your terminal.
podman-compose up -d

pip install podman-compose
podman-compose up -d

podman ps 
podman network inspect dqe-automation_tafordqenetwork 
podman compose ps