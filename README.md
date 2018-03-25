# ABE-IN-POS
Point of service application with ABE

## Runing with docker-compose
1. Execute ```docker-compose``` command.
    ```
    docker-compose up --build -d
    ```
    A container named ````abeinpos_abe-in-pos_1``` will run in background and will automatically attach to a persistent volume.
2. Copy files/folders to the input folder.
    ```
    docker cp <files> abeinpos_abe-in-pos_1:/code/input/
    ```
3. Execute commands
    ```
    docker exec abeinpos_abe-in-pos_1 <command>
    ```
4. All files saved in /code/data will stay in /home/faculty/default

## Running with Docker
1. Build using Docker Compose:
    ```
    docker-compose build
    ```
2. Run the image ```abe-in-pos:latest``` for the first time using Docker (attach volume first!)
    ```
    docker run -td --name <container_name>  abe-in-pos:latest
    ```
    The container will run until manually terminated.
3. Copy input files to the input folder
    ```
    docker cp <filename> <container_name>:/code/input
    ```
4. Execute commands in the container.
    ```
    docker exec <container_name> <command>
    ```