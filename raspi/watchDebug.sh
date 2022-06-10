echo What is the latest file you want to read?

read fileName

tail -f ./logging/$fileName
