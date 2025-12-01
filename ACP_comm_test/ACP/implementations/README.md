# Implementations

## Overview

These directories are examples or working code for ACP purposes. They contain
miscelleneous examples or implementations of the acpcomms library. 

## File Structure

* `implementations/java/*` - Java implementation files
* `implementations/python3/*` - Python implementation files

## Use

Each file will generally require some work to get running. Generally speaking, 
in order to run each file, it needs to correctly import the acpcomms library.
To run a file, move it from `implementations/` directory to the same directory 
level as the ACP repository itself, **regardless of language** . For example, 
to run the `acp_subscriber.py` you would need to replicate the following 
directory structure:

```
working_folder (destination)
├── ACP
|   ├── acpcomms
|   |   └── ...
|   └── implementations
|       ├── java
|       |   └── ...
|       └── python
|           ├──acp_subscriber.py (copy this file to the "destination" directory)
|           └── ...
└── acp_subscriber.py (this the copied file)
```

Any other file in these directories should behave the same; any code you wish 
to run with the acpcomms dependency needs to be manually moved to a parent 
directory (in this case, it's literally called `working_folder`) at the same 
level at which the ACP repository is cloned too. 