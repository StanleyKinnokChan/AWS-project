# Real-Time Data Streaming with Kafka using EC2 as Server

## Overview:
This scenario involves receiving live data from a source, which is streamed using an EC2 instance functioning as a Kafka server. A Python-based producer client is employed to transmit the data to the server. The data is received by consumer clients, which subsequently input it as JSON files into an S3 bucket, creating a data lake. This data can then undergo crawling and storage to generate a metatable. The resulting metatable can be visualized and analyzed in Amazon Athena.
![My Remote Image](https://i.imgur.com/cJM1Wyn.png)

## Content
- [Setup & Dependencies]( )
- [Data source]( )
- [Launch the EC2 instance]( )
- [Connect to EC2 instance]( )
- [Download Kafka and Java in the EC2 instance]( )
- [Starting Zoo-keeper and Kafka server]( )
- [Create Topic & Start the Producer and Consumer]( )
- [Set up S3 bucket and connection to AWS]( )
- [Use python as producer and consumer clients]( )
- [Crawler, Data Catalog & Athena]( )

### Setup & Dependencies
This project requires the utilization of an AWS account for cloud services.WSL (Windows Subsystem for Linux) is employed to enable Linux command usage within the Windows operating system. AWS CLI is also required to set up the connection from local machine to AWS

The following software version are adopted in this project:
- Python 3.8.0
- Kafka 3.6.1
- openjdk 1.8.0_392

### Data source
The availble live streaming APIs require payment. In this demo, therefore, data are sampled from a stock data dataframe and send to the cluster with a endless loop in python, which can mimic the on-going data production from the API.

### Launch the EC2 instance
- Amazon Machine Image (AMI): Ubuntu server 22.04 LTS (HVM) SSD Vollume type
- Instance type: t2.micro
- Enable auto-assign public IP
- Create key pair for SSH connection (optional) and save the key to the project folder
- Add Inbound Security Group Rules to allow local machine connecting to the instance

### Connect to EC2 instance
The EC2 instance is directly connected via **EC2 Instance Connect**. It can also be connect via SSH client if key pair is generated in the previous step. If SSH is the method, the key file has to be set as not publicly viewable via: `chmod 400 "<key_name>.pem"`. 

>If WLS is used, the chmod command would not be working as expected, use the following code instead:
```
cp <key_name>.pem ~/.ssh/
chmod 600 ~/.ssh/<key_name>.pem
eval `ssh-agent -s`
ssh-add ~/.ssh/<key_name>.pem
```
Afterall, use the command  `ssh -i "<key_name>.pem" <Username>@<Public DNS:>` connect to EC2 instance. The command can be copied directly from EC2 connection page.

### Download Kafka and Java in the EC2 instance
```
wget https://downloads.apache.org/kafka/3.6.1/kafka_2.12-3.6.1.tgz
tar -xvf kafka_2.12-3.6.1.tgz

sudo add-apt-repository ppa:openjdk-r/ppa
sudo apt-get update
sudo apt-get install openjdk-8-jre
java -version
```

### Starting Zoo-keeper and Kafka server
ZooKeeper is a centralized service for maintaining configuration information, naming, providing distributed synchronization, and providing group services. It provides an in-sync view of the Kafka cluster.
```
cd kafka_2.12-3.6.1
bin/zookeeper-server-start.sh config/zookeeper.properties
```
Open new connection to EC2. As Kafka server is defaulted pointing to the pivate server, it has to be set as public first. Use `sudo nano config/server.properties` - change ADVERTISED_LISTENERS to public IPv4 of the EC2 instance. 
![My Remote Image](https://i.imgur.com/QshjUxw.png)

With an increase the allowed memory usage of Kafka, the server can be started. If sucessful, you will see the server are running with the public IPv4 address.
```
export KAFKA_HEAP_OPTS="-Xmx256M -Xms128M"
cd kafka_2.12-3.6.1
bin/kafka-server-start.sh config/server.properties
```
![My Remote Image](https://i.imgur.com/WLyT4k9.png)

### Create Topic & Start the Producer and Consumer
Create the topic by:
```
cd kafka_2.12-3.6.1
bin/kafka-topics.sh --create --topic demo_testing --bootstrap-server {Put the Public IP of your EC2 Instance:9092} --replication-factor 1 --partitions 1
```

Open new connection to EC2. Start a producer with the created topic by:
```
cd kafka_2.12-3.6.1
bin/kafka-console-producer.sh --topic demo_testing --bootstrap-server {Put the Public IP of your EC2 Instance:9092} 
```
Open new connection to EC2. Start a consumer with the created topic by:
```
cd kafka_2.12-3.6.1
bin/kafka-console-consumer.sh --topic demo_testing --bootstrap-server {Put the Public IP of your EC2 Instance:9092}
```
After starting both producer and consumer, we can test check whether they work properly. If successful, when you type something on the producer, the same text message will be shown on the consumer. 
![My Remote Image](https://i.imgur.com/iLRF7P0.png)

### Set up S3 bucket and connection to AWS
S3 bucket is set up for the recieving the Json file produced in python.
To connect local machine to AWS, an user is created with policy **AdministratorAccess** attached. The access credential is generated for the user. Use `AWS configure` in the command line to input the **AWS access Key ID** and  **AWS Secrete Access Key** for the AWS connection.

### Use python as producer and consumer clients
Please refer to the .py files for the details of the code. 

Simply put, after setting up a producer client with specifying the endpoint, we can send the messages to the Kafka cluster. 
![My Remote Image](https://i.imgur.com/SQ1cvXI.png)

As explained in [Data source]( ) section, the endless data stream generated from the API is stimulated by creating an endless loop to sample the data and send data to the cluster. The consumer will keep recieving the data from the python producer client. 
![My Remote Image](https://i.imgur.com/44OnbD4.png)

Similarly, after setting up a consumer client with specifying the endpoint, we can recieve the messages to the Kafka cluster as well. 
![My Remote Image](https://i.imgur.com/KZnACYJ.png)

After starting the data generation from the producer, by iterating the consumer and using S3FileSystem, the data are streamed to S3 as Json files, with the timestamp in the file name as an unique identifier for each process.
![My Remote Image](https://i.imgur.com/h7rpIGs.png)
![My Remote Image](https://i.imgur.com/HL19Dv5.png)

The data can be queried via S3 Select:
![My Remote Image](https://i.imgur.com/KcTTnJ8.png)

### Crawler, Data Catalog & Athena
To view all the data that are streamed into the S3 bucket, we use crawler to create the matatable that consolidate all the JSON files in the bucket. 
![My Remote Image](https://i.imgur.com/9uvn2qv.png)

The table can be then queried in Athena:
![My Remote Image](https://i.imgur.com/CukiVWC.png)
![My Remote Image](https://i.imgur.com/YpDs8hw.png)
