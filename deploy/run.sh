sudo docker build -t "sfuzz" .
sudo docker rm -f sfuzz
sudo docker run -it "sfuzz"
