# ACP - Autonomy Capability Platform

## Overview

This is a repository meant to hold communications files in support of the IAE 
Autonomy capability platform. These files are both the communications library 
itself (acpcomms) 

**IMPORTANT INFO**
There is a known bug for importing classes described in `acpcomms/java/*` which 
requires users of the library to change the package declarations to build their 
code. We are working to define a fully independent and importable solution. 
For now, when importing this code in java applications, ensure you copy the 
code over and change the package declarations there. **DO NOT COMMIT CHANGES TO 
THE PACKAGE DECLARATIONS IN THE ACPCOMMS DIRECTORY**.

## Folder Structure
### acpcomms
Implementations of the communication protocols supported by ACP:
* Java
* Python3

For instructions on library use, general information like class architecture 
and features can be found in `acpcomms/README.md`. Language specific 
information like installation requirements be found in the `README.md` files in 
the subsequent directories within.

### implementations
Code used for previous demos, examples and robot capabilities are stored here. 
This is a working directory for robot development. Code scripts here are not 
centrally documented as each file may differ, refer to file comments or any 
other `README.md` files within for more information. Code in these folders may 
directly inherit/implement code found in `acpcomms/[language]/*`

### uml
Plant UML diagram source code for architecture/sequence diagrams are stored 
here.