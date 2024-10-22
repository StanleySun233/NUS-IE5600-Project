docker build -t sac .
docker run -d --restart=always --name sac -p 5555:5000 sac
