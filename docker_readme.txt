
# navigate to austenite calculator directory (flask version)

# build the new image (this may take a minute, has to download gsas, etc)
docker build -t ac_flask .

# then the new image should be built

# to run with a bind mount so that changes locally are transferred to the container
docker run -d -p 8050:8050 --name ac --mount type=bind,source="/c/Users/dtn1/OneDrive - NIST/Documents/ByScientist/AdamCreuziger/ac_flask",target=/root/AustCalc ac_flask

# note, you'll have to change the directory above to your own
# app should be running on localhost:8050