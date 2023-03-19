# order-microservice

1. place the three file in the same folder

2. build the container, enter the following command into cmd (replace <dockerid> with your docker id):
docker build -t <dockerid>/order:1.0 ./

3. run the container, enter the following command into cmd (replace <dockerid> with your docker id): 
docker run -p 5000:5000 -e dbURL=mysql+mysqlconnector://is213@host.docker.internal:3306/orderdb <dockerid>/order:1.0
  
  
To create order [post] http://localhost:5000/order
example input:
{
   "customerID": "9",
   "customer_name": "Bob",
   "phone_no": "94208576",
   "total_price": "10000.00",
   "status": "testing",
    "order_items": [
      {
        "item_name": "bak chor mee",
        "itemID": 9,
        "quantity": 100
      },
      {
        "item_name": "prawn mee",
        "itemID": 10,
        "quantity": 200
      }
    ]
}

To update order [post] http://localhost:5000/order/<string:orderID>
example input:
{
   "status": "PROCESSING"
}

To get order [get] http://localhost:5000/order/<int:orderID>
