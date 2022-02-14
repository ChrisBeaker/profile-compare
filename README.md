# profile-compare
Compare packages from SUMA Profile against a real system.

profile-compare can be used to compare pre-saved package information, captured in a SUMA Profile, against a real system. The result of the compare can then be used as a new package installation.

The following parameter were supported:

required - positional parameter:

srvtgt = SystemID of the server

profile = SUMA Profile Name

stime = Time when the installation should be started. Allowed parameters are now (meaning package installation starts immediately)
or future (means in one week from now). The future value is good for testing, because it allows you to cancel the package installation.

Required switches (actions):

--newer = Schedule package installation, if the profile has newer package(s) listed than the system specified with srvtgt.

--onother = Schedule package installation, if the profile has package(s) listed which are not on the system specified with srvtgt


Optional switches:

--split = if --newer and --onother is used, then the schedule packages installation job can be submited as individial task. 

--noncompliant NONCOMPLIANT = NONCOMPLIANT (SystemID of a real system, ideally the same where the profile was taken from.

If the SUMA profile was taken with non-compliant package. Then the profile can most likely not be use as a reference.
By schedule a package installation, the SUMA API checks if the provided package can be installed with the assigned repositories.
The non-compliant packages are packages which were not installed via SUMA or the package was originally installed with a lower support packs level. If packages can not be found on the given system (srvtgt), then the package installation will deny.
Therefore, the switch --noncompliant can be used followed by a SUMA System ID (NONCOMPLIANT) to exclude these package.

Example:

python3 profile-compare.py 1000010893 profile1 future --onother --newer --noncompliant 1000010164

python3 profile-compare.py 1000010893 profile1 future --onother --newer --noncompliant 1000010164 --split

python3 profile-compare.py 1000010893 profile1 future --newer --noncompliant 1000010164

python3 profile-compare.py 1000010893 profile1 now --onother



Before you start:

Please replace the URL of the SUMA server and enter your credentials:

MANAGER_URL = "https://[SUMA FQDN]/rpc/api"

MANAGER_LOGIN = "[User]"

MANAGER_PASSWORD = "[Password]"



P.S.:
I am new to Python, be patient with me ;-)
