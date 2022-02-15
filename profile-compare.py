#!/usr/bin/python3
#
#
# SUMA API Method: listExtraPackages, 
# SUMA API Method: schedulePackageInstallByNevra
# SUMA API Method: comparePackageProfile
#


from xmlrpc.client import ServerProxy
import datetime
import argparse
import xmlrpc.client
import sys


MANAGER_URL = "https://[SUMA FQDN]/rpc/api"
MANAGER_LOGIN = "[User]"
MANAGER_PASSWORD = "[Password]"

def fltPackages(state, profile_packages): # state can be onother=3 or newer=4 / profile_packages = complete list of packages form profile
    flt_packages = []
    if state == 'onother':
        print ("\nPackages on other system present!")
        cmp_mode = 3
    elif state == 'newer':
        print ("\nPackages newer than on other system!")
        cmp_mode = 4
    else:
        return False

    flt_packages = [package for package in profile_packages if package.get('comparison') == cmp_mode ]
    if flt_packages:
        for package in flt_packages:
            print(f"Name: {package.get('package_name'):40}\
                 Version: {package.get('package_version'):26}\
                 Release: {package.get('package_release'):15}\
                    Arch: {package.get('package_arch')}")
    return flt_packages

def scheduleInstallation(key, srvtgt, list_packages, siptime):
    print ('\nSchedule package installation')
    try:
        print ('Action ID is: ',client.system.schedulePackageInstallByNevra(key,srvtgt,list_packages,siptime))

    except xmlrpc.client.Fault as err:
        print("A fault occurred")
#        print("Fault code: %d" % err.faultCode)
        print("Fault string: %s" % err.faultString)
        print("Hint: You may need to exclude this package with paramater --noncompliant")


client = ServerProxy(MANAGER_URL)
key = client.auth.login(MANAGER_LOGIN, MANAGER_PASSWORD)

parser = argparse.ArgumentParser(description='Application parameters description')
parser.add_argument('srvtgt', type=int, help='SUSE Manager System ID of Target System')
parser.add_argument('profile', type=str, help='SUSE Manager Stored Profile Name')
parser.add_argument('stime', type=str, help='earliestOccurrence of install action: allowed value=now or future(one week from now)')
parser.add_argument('--newer', action='store_true', help='Newer package version on other system available',required=False)
parser.add_argument('--onother', action='store_true', help='Package on other system only.',required=False)
parser.add_argument('--split', action='store_true', help='Split package installation into onother and newer seperately.',required=False)
parser.add_argument('--noncompliant',type=int, help='Remove non-compliant package(s), required parameter is SystemID of profile source ',required=False)
args = parser.parse_args()

if args.stime == 'now':
    siptime = datetime.datetime.now()
if args.stime == 'future':
    siptime = datetime.datetime.now() + datetime.timedelta(days=5)

srvtgt  = (args.srvtgt)  #Target System ID
profile = (args.profile) #Profile name
non_compliant = []       #list of non-compliant packages from real system, best is the same as the source of profile
newer = []               #list of newer packages - pre-defined in case of mixing unsupport args parameters
onother = []             #list of onother packages  - pre-defined in case of mixing unsupport args parameters
list_packages = []       #list of left packages after filter, or if filter is skiped
final_list = []          #in case paramater split is not used, then add packages from onother and newer to this list together

# read all packaes from profile
try:
    list_packages_raw = client.system.comparePackageProfile(key,srvtgt,profile)
except xmlrpc.client.Fault as err:
    print("A fault occurred")
    print("Fault code: %d" % err.faultCode)
    print("Fault string: %s" % err.faultString)
    if err.faultCode == -1:
        print("Application will be terminated")
        sys.exit()
      
#in case system has non-compliat package(s) listed and these are in the pofile.
if args.noncompliant:
    print('Removing  non-compliant packages from profile')
    try:
        non_compliant = client.system.listExtraPackages(key,args.noncompliant)
    except xmlrpc.client.Fault as err:
            print("A fault occurred")
            print("Fault code: %d" % err.faultCode)
            print("Fault string: %s" % err.faultString)        

    if non_compliant:
        for each_non_compliant in non_compliant:
            pname = each_non_compliant.get('name')
            print(f"Removing package {pname} from profile list.")
# the try statement is not needed, I guess, but I leave it in ... 
            try:
                list_packages = [package for package in list_packages_raw if package.get('package_name') != each_non_compliant.get('name')]
            except:
                print("Could not delete entry from profile list. Hint: Was the profile created based on the provided System ID?")

            list_packages_raw = list_packages
else:
    print ("No Exclusion\n")
    list_packages = list_packages_raw

#collect only the requested packages (onother and/or newer)
if args.onother == True:
    onother = fltPackages('onother',list_packages)

if args.newer == True:
    newer = fltPackages('newer',list_packages)

#check if paramer split is used and call scheduler action. 
if args.split == True:
    if onother:
        scheduleInstallation(key, srvtgt, onother, siptime) 
    if newer:
        scheduleInstallation(key, srvtgt, newer, siptime) 
elif args.split == False:
    try:
        final_list = onother + newer
    except TypeError as err:
        print(f"Something is wrong here. Please validate the application parameters.")
        print(f"Hint: Maybe the provided System IDs is not valide")
    if final_list:
        scheduleInstallation(key, srvtgt, final_list, siptime) 
else:
    print ("No Packages available!")


client.auth.logout(key)
