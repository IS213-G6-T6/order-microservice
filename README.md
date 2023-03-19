# order-microservice

1. place the Dockerfile, order.py, requirments.txt in the same folder

2. build the container, enter the following command into cmd (replace <dockerid> with your docker id):
docker build -t <dockerid>/order:1.0 ./

3. run the container, enter the following command into cmd (replace <dockerid> with your docker id): 
docker run -p 5000:5000 -e dbURL=mysql+mysqlconnector://is213@host.docker.internal:3306/orderdb <dockerid>/order:1.0
  
  
To create order [post] (example input in input example.txt): http://localhost:5000/order
  example input in input example.txt

To update order [post] (example input in input example.txt): http://localhost:5000/order/<string:orderID>
  

To get order [get]: http://localhost:5000/order/<int:orderID>
