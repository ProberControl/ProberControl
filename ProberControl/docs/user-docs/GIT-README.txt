The configuration file should not be commited as it is only dependent on the stages connected to the machine.

This will tell git you want to start ignoring the changes to the file
git update-index --assume-unchanged path/to/file

When you want to start keeping track again
git update-index --no-assume-unchanged path/to/file
