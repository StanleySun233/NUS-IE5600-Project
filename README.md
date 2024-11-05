# IE5600 Group Project

**Group Number**: 19

**Group Member**

| Full Name    | Student Number |
|--------------|----------------|
| Sun Sijin    | A0303466H      |
| Wu Chengxi   | A0303622U      |
| Wang Xixiang | A0303526M      |
| Yang Yiying  | A0303534N      |
| Zhang Hezi   | A0303788U      |

**Project Topic**: A Novel Intelligent System for Collision Avoidance Simulation

**Project Description**:

This project presents a comprehensive system for managing and analyzing maritime Automatic Identification System (AIS)
data, aimed at improving ship tracking accuracy and collision prevention. The system integrates a robust data management
module that allows for the addition, deletion, modification, and querying of both ship and AIS data, along with
cross-referencing capabilities to facilitate data linkage. Key algorithmic contributions include implementing cubic
spline interpolation and the Piecewise Cubic Hermite Interpolating Polynomial (PCHIP) method for trajectory smoothing,
ensuring continuity and stability in dynamic ship movements, especially during maneuvers. To enhance data quality, the
system incorporates a threshold-based AIS data cleaning approach to filter out anomalies. Furthermore, five distinct
collision detection methods are implemented to provide a multi-layered collision risk assessment. The project also
includes visualization tools for generating ship trajectory diagrams and simulating collision scenarios, offering a
visual interface for risk analysis. Together, these features create a reliable framework for maritime safety management,
optimizing both real-time monitoring and post-event analysis.

It can be summary that:
* Data
    1. Implement the functions of adding, deleting, modifying and checking ship and ais data.
    2. Implement the cross-query logic of ship and ais.
* Algorithm
    1. Implement the cubic spline interpolation of `Cubic` and the segmented cubic Hermite interpolation method of
       `Pchip`.
    2. Implement the data cleaning of ais abnormal data through the threshold method.
    3. Implement five detection methods for ship collision.
    4. Generate visual trajectory diagrams and collision simulation videos.

**Key Functionalities & Test Cases**

| S/N | Description of Test Cases/Business Rules            | Test Cases(Input Parameters, Expected Outputs, Special Cases)                                     |
|-----|-----------------------------------------------------|---------------------------------------------------------------------------------------------------|
| 1   | add a new ship.                                     | MMSI=12345678, add success.                                                                       |
| 2   | add a ship appeared in data.                        | MMSI=412356358, Duplicate MMSIs are not allowed in the database                                   |
| 3   | delete a ship linked with some ais data.            | MMSI=200017675, also delete 57 AIS data.                                                          |
| 4   | create a ais data, which mmsi not appeared in data. | MMSI=1, before create this data, system first generate ship.MMSI=1                                |
| 5   | view ais trace.                                     | MMSI1=412415970, generate html successfully.                                                      |
| 6   | request to generate a non-existent ship.            | MMSI=2, return nothing.                                                                           |
| 7   | view conjection trace.                              | MMSI1=412415970, MMSI2=413457740, DATE=2021-05-05, generate html and mp4 simulation successfully. |
| 8   | view conjection trace with no-existent ship.        | MMSI1=1, MMSI2=2, return nothing.                                                                 |