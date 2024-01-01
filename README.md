• Orchestrated a microservices architecture comprising authentication, authorization, upload, and conversion services using Python, Flask, Docker, and Kubernetes.
• Employed asynchronous communication using RabbitMQ queues to facilitate seamless video processing and conversion to MP3, ensuring efficient task distribution among services.
• Implemented MongoDB with GridFS for efficient storage and retrieval of large video files, overcoming MongoDB's 16MB size limit.
• Managed video and audio file storage, handling, and conversion while ensuring data integrity and secure storage mechanisms.
• Utilized Docker for containerization, Kubernetes for orchestration, and Minikube for local development, ensuring consistent and scalable deployment across environments.


Lets deep dive a little more : 

1. Setting Up Virtual Environment
  Utilize Python 3's  env module to create a virtual environment->  python3 -m venv venv-env
  Activate the created virtual environment -> source venv-env/bin/activate
2. Install Dependency
   For Someone using the repo : pip install -r requirements.txt
   What I did : install the requirements normally using pip and then used pip3 freeze > requirement.txt to write them in file
3. Database Setup
   We are using MySql for authentication and MongoDB for storing video/audio.
   MySQL : Install MySQL , Start the Server using brew services start mysql. Run the init.sql script.
   MongoDb : MongoDB installation - https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-os-x/
            To start —>  brew services start mongodb-community@7.0
            To stop -> brew services stop mongodb-community@7.0
4.JWT (JSON Web Token) Implementation:

  JWT is used for user authentication. It consists of three parts: header, payload, and signature. The header contains information about the token, such as the type and signing algorithm.
  The payload holds user data, like name, email, and additional details.
  We implement JWT using a symmetric signing algorithm, specifically HS-256. This involves a single private key kept secret and shared between two parties: the server and the client.

Token Creation:
  When a user logs in, the server generates a JWT by signing it with the secret key. This creates a unique token containing user-specific information.
  Token Usage:
  When the user sends a request, they include this JWT in the request headers.
  The server validates the incoming JWT using the shared secret key. This ensures the authenticity and integrity of the token.
  Token Decoding:
  Upon receiving the JWT, the server decodes it using the same secret key used for signing. This allows extraction of user data and enables verification of the token's legitimacy.

5. To ensure accessibility within the Docker container, we configure the host to 0.0.0.0. This setting allows the Flask application to listen on all network interfaces.
   Without this configuration, the default setup uses the local address, which, in the case of Docker, becomes a loopback request.

6. Dockerfile Build Process
  In our Dockerfile, we begin by constructing a Docker image using a base image, specifically Python 3.10 slim bullseye. Each instruction in the Dockerfile represents a layer in the image.
  Docker optimizes the build process by utilizing caching mechanisms, rebuilding only the layers that have changed.
  The Docker build process is initiated using the command "docker build ." This command assembles the image according to the instructions defined in the Dockerfile,
  ensuring that each step, including the installation of Python dependencies, is executed systematically.

  Upon successful build completion, we tag the resulting image with a unique identifier using docker tag <build_id> <username>/<reponame>:latest. This tag serves as a versioned reference to our Docker image.

  Finally, to share the built image, we push it to a Docker repository. This is achieved by executing docker push <username>/<reponame>:latest, making the image accessible for deployment across environments or to other developers.

7. Kubernetes Deployment Process

   We organize our Kubernetes configurations by creating a dedicated directory within the project.
   We initiate Minikube, a local Kubernetes environment, by executing minikube start. This establishes a local Kubernetes cluster for testing and development.
   Using YAML files, we define configurations for Kubernetes resources such as deployments, services, or pods. These files outline how our application should be deployed within the Kubernetes cluster.
   The deployment configurations are applied to the Kubernetes cluster using the command "kubectl apply -f ./" within the YAML directory.

 8. Cluster Monitoring and Management:

    k9s Tool Usage: We utilize the k9s tool, an efficient Kubernetes dashboard, to visually inspect and manage resources within the Minikube cluster. 
    This offers an alternative to the command-line interface for navigating and monitoring Kubernetes resources.
    Using kubectl, the Kubernetes command-line tool: 
          kubectl get pods: Fetches a list of pods along with their status within the cluster, allowing us to view their current state.
          kubectl describe pod <pod-name>: Provides detailed information about a specific pod, aiding in debugging or troubleshooting.
          kubectl logs <pod-name> -c <container-name>: Retrieves logs from a particular container within a pod, aiding in diagnosing issues or observing container behavior.

  9. Scaling Replicas and Debugging in Kubernetes:
    Use kubectl scale to adjust replicas. For instance, kubectl scale deployment --replicas=0 gateway stops all instances. Modify the --replicas value to scale up or down.
    Scaling to --replicas=1 helps isolate issues. It's a focused way to debug individual instances, streamlining the troubleshooting process.
  10. MongoDB and GridFS
    MongoDB has a 16MB limit, so we use GridFS for larger files by dividing them into chunks of 255KB.
    It employs two collections—one for file chunks and one for metadata—to manage and reconstruct files.
    Our API gateway is synchronous, but the gateway and converter services are asynchronous. Instead of waiting, the gateway stores videos in MongoDB and sends a message to a queue for downstream processing.
    This method allows convenient processing by downstream services like conversion and notification at their own pace.

  11. Gateway Service and Ingress:

      The gateway service is configured using an ingress.yaml file, enabling traffic to access the gateway endpoint.
      A service, which is a group of pods, is created to scale up the service for increased traffic. It aggregates all gateway instances using a selector, abstracting the need to manage individual pod IPs or load balancing.
      Requests to the cluster IP are routed to the pods via this service.
      Ingress allows external requests to reach services within the cluster. It comprises a load balancer serving as the entry point to the cluster and a set of rules defining traffic distribution to different services. 
      For instance, mapping mp3converter.com to our gateway ensures any request to mp3converter.com reaches our gateway service.
      To map our services to localhost, we modify the /etc/hosts file to associate loopback addresses with specific services. This mapping allows requests to mp3converter.com to resolve to our local Kubernetes Docker setup.
      In Minikube, enabling the ingress addon is necessary using "minikube addons enable ingress". Subsequently, running minikube tunnel ensures that requests to our loopback address are directed to the Minikube cluster via ingress.
  12.  RabbitMQ and Queueing System:

        RabbitMQ serves as our message queue system. Instead of producers directly publishing to the queue, they send messages through an exchange. 
        This setup allows for multiple queues where the exchange routes messages to the correct queue. Our implementation uses a default exchange, specifically a direct exchange, which creates routing queues mirroring their queue names.
        
        Our RabbitMQ setup is managed as a stateful set, ensuring data persistence. Each pod is identified by a persistent identifier, easing volume matching, and utilizes physical storage for data persistence. 
        We maintain one master pod and several slave pods that synchronize with the master.
        
        To maintain data integrity, we mount physical storage to the container instance, ensuring data availability even if the container instance fails. 
        The flow involves Persistence Volume Claims (PVC) connecting to Persistent Volumes (PV), which finally connect to physical storage.
        
        Similar to other services, we route all domains to the loopback address. Leveraging RabbitMQ's management console (rabbitmq-manager.com), we facilitate queue management.
        Using Minikube tunneling enables access to .com domains.
        
        Utilizing the management console, we create two queues: one for videos uploaded by users and another for MP3 files sent to users. These queues are named based on the routing keys specified in util.py. 
        Maintaining PVC:
        
        As PVCs are immutable, any changes require deleting the deployed files using kubectl delete -f ./ and reapplying the configurations.

  13. Testing
      To test functionality:
          Execute curl -X POST http://mp3converter.com/login -u ayuranjan@gmail.com:Admin123 to obtain the JWT token.
          Use the acquired token to authenticate the upload: curl -X POST -F 'file=@./song.mp4' -H 'Authorization: Bearer <token>' http://mp3converter.com/upload

      Now our video will be converted to mp3 and will be in MongoDB. Now to download and check the mp3 we can use Below command. We can get the id from database or from the mp3 queue. 
       mongofiles —db= mp3 get_id —local= test.mp3 ‘{$oid”: “<string version of id>”}’

 14 . Good Luck !! 



   
