# **SUBMISSION LINK MUST BE EXACTLY ONE LINE BELOW THIS** (FAILURE TO DO SO WILL RESULT IN A 0 GRADE)

(https://youtu.be/uqvpWkQGqXI)

## Video submission requirements:
 - Must clearly show the ESP 32 and Sensor working
 - Must clearly show a functioning front-end
 - Must show a webserver container and a database container running
    - Run docker ps in a terminal or show docker desktop.
 - All of the above must be included to receive credit.

# Tech Assignment 7


 - A frontend webpage that has the following:
    - A way to see and toggle the live readings from the AMG 8833 sensor:
        - Visualized readings from the sensor
        - Ambient temperature thermistor value
        - Neural network (running on ESP 32) prediction of whether or not there is a person in frame
    - A way to see data readings stored in your database
    - [EXTRA CREDIT] Good looking CSS formatting
 - Docker containers that run the following:
    - An API webserver that has the following:
        - Serves the front-end described above
        - Has an api endpoint that allows to the toggling of ESP 32 readings (get one, send continuous, stop sending continuous)
        - Has API endpoints required to add, read and delete readings from the database
        - Has a table that stores unique ESP 32 entries.
            - (Each ESP 32 has a unique MAC addres, we expect you to associate each reading from the ESP with its MAC addres in the database)
        - [EXTRA CREDIT] Store thermal readings along with the thermister readings. Include normalization relative to thermister reading in your front-end visualization.
        - [EXTRA CREDIT] Infer more information from your data come up with something extra that you can do.
    - A database that has allows all of the above to be implemented
        - [HINT] Use two tables, one table to store readings, one table to store unique ESP 32s. Associate each reading with a MAC address of an ESP that is in the "devices" table, separate from the readings "table"
