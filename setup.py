#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
import time
import datetime
import platform
import pkg_resources
from setuptools import setup, find_packages

install_requires = []
extras_requires = []
# https://github.com/mapproxy/mapproxy/blob/master/setup.py;

pygenbuildinfo = True
# Open and read the version info file in a Python 2/3 compatible way
verinfofilename = os.path.realpath("."+os.path.sep+os.path.sep+"parse_message_file.py")

# Use `with` to ensure the file is properly closed after reading
# In Python 2, open defaults to text mode; in Python 3, it’s better to specify encoding
open_kwargs = {'encoding': 'utf-8'} if sys.version_info[0] >= 3 else {}
with open(verinfofilename, "r", **open_kwargs) as verinfofile:
    verinfodata = verinfofile.read()

# Define the regex pattern for extracting version info
# We ensure the pattern works correctly in both Python 2 and 3 by escaping the strings properly
version_pattern = "__version_info__ = \(\s*(\\d+)\s*,\s*(\\d+)\s*,\s*(\\d+)\s*,\s*['\"]([\w\s]+)['\"]\s*,\s*(\\d+)\s*\)"
setuppy_verinfo = re.findall(version_pattern, verinfodata)[0]

# If version info is found, process it; handle the case where no match is found
if setuppy_verinfo:
    setuppy_verinfo_exp = setuppy_verinfo
else:
    print("Version info not found.")
    setuppy_verinfo_exp = None  # Handle missing version info gracefully

# Define the regex pattern for extracting version date info
date_pattern = "__version_date_info__ = \(\s*(\\d+)\s*,\s*(\\d+)\s*,\s*(\\d+)\s*,\s*['\"]([\w\s]+)['\"]\s*,\s*(\\d+)\s*\)"
setuppy_dateinfo = re.findall(date_pattern, verinfodata)[0]

# If date info is found, process it; handle the case where no match is found
if setuppy_dateinfo:
    setuppy_dateinfo_exp = setuppy_dateinfo
else:
    print("Date info not found.")
    setuppy_dateinfo_exp = None  # Handle missing date info gracefully

pymodule = {}
pymodule['version'] = str(setuppy_verinfo_exp[0])+"." + \
    str(setuppy_verinfo_exp[1])+"."+str(setuppy_verinfo_exp[2])
pymodule['versionrc'] = int(setuppy_verinfo_exp[4])
pymodule['versionlist'] = (int(setuppy_verinfo_exp[0]), int(setuppy_verinfo_exp[1]), int(
    setuppy_verinfo_exp[2]), str(setuppy_verinfo_exp[3]), int(setuppy_verinfo_exp[4]))
pymodule['verdate'] = str(setuppy_dateinfo_exp[0])+"." + \
    str(setuppy_dateinfo_exp[1])+"."+str(setuppy_dateinfo_exp[2])
pymodule['verdaterc'] = int(setuppy_dateinfo_exp[4])
pymodule['verdatelist'] = (int(setuppy_dateinfo_exp[0]), int(setuppy_dateinfo_exp[1]), int(
    setuppy_dateinfo_exp[2]), str(setuppy_dateinfo_exp[3]), int(setuppy_dateinfo_exp[4]))
pymodule['name'] = 'PyTextArchive'
pymodule['author'] = 'Kazuki Przyborowski'
pymodule['authoremail'] = 'kazuki.przyborowski@gmail.com'
pymodule['maintainer'] = 'Kazuki Przyborowski'
pymodule['maintaineremail'] = 'kazuki.przyborowski@gmail.com'
pymodule['description'] = 'A text archive format for message boards or social media.'
pymodule['license'] = 'Revised BSD License'
pymodule['keywords'] = 'pytextarchive textarchive archive text backup'
pymodule['url'] = 'https://github.com/GameMaker2k/PyTextArchive'
pymodule['downloadurl'] = 'https://github.com/GameMaker2k/PyTextArchive/archive/master.tar.gz'
pymodule['packages'] = find_packages();
pymodule['packagedata'] = {'data': ['*.txt', '*.json', '*.yaml', '*.html']}
pymodule['longdescription'] = "" 
'''
pymodule['keywords'] = 'love loveisokifnotextreme extremeloveisnotok lovesostrong lovesostrongitscreepy lovesostrongitiscreepy extreamelove excessivelove yanderelove unbendinglove loveyoucantbelievein whydidthishappentomelove creepylove loveinabundance morelovemoreextreme weheardyoulikelovesowegotyoulove iloveyoumorethenyouknow ifyoulovethemtheywilllovebackinextreme whenyoulovetheylovebackinextreme ifonlyineverlovedagain somuchloveyoucanthandleitanddie weloveonlyforlovetheyloveforextremelove iloveyoumorethenyouknowbutyouloveinextreme isextremeloverealyinhighdemand lovesostrongitscreepy lovesostrongitiscreepy extreamelove excessivelove yanderelove unbendinglove loveyoucantbelievein whydidthishappentomelove creepylove loveinabundance isloverealyinhighdemand morelovemoreextreme weheardyoulikelovesowegotyoulove iloveyoumorethenyouknow ifyoulovethemtheywilllovebackinextreme whenyoulovetheylovebackinextreme ifonlyineverlovedagain somuchloveyoucanthandleitanddie weloveonlyforlovetheyloveforextremelove iloveyoumorethenyouknowbutyouloveinextreme willidiefromallthisextremelove extremeloveyoulldiefor whydotheylovemesoextreme ionlyloveyoubutyoutookittoextremes somuchloveitsunhealthy unhealthylove whydidmylovemakethemloveinextremeamounts cantheylovemeanymoreifitsinextremeamounts willtheyeverstoplovingmeinextremeamounts extremelovestory'
'''
pymodule['platforms'] = 'OS Independent'
pymodule['zipsafe'] = True
pymodule['pymodules'] = ['parse_message_file', 'archive_parser']
pymodule['scripts'] = ['display_message_file.py']
pymodule['classifiers'] = [
 'Development Status :: 5 - Production/Stable',
 'Intended Audience :: Developers',
 'Intended Audience :: Other Audience',
 'License :: OSI Approved',
 'License :: OSI Approved :: BSD License',
 'Natural Language :: English',
 'Operating System :: MacOS',
 'Operating System :: MacOS :: MacOS X',
 'Operating System :: Microsoft',
 'Operating System :: Microsoft :: Windows',
 'Operating System :: OS/2',
 'Operating System :: OS Independent',
 'Operating System :: POSIX',
 'Operating System :: Unix',
 'Programming Language :: Python',
 'Topic :: Utilities',
 'Topic :: Software Development',
 'Topic :: Software Development :: Libraries',
 'Topic :: Software Development :: Libraries :: Python Modules'
]

if(len(sys.argv) > 1 and (sys.argv[1] == "versioninfo" or sys.argv[1] == "getversioninfo")):
    import json
    pymodule_data = json.dumps(pymodule)
    print(pymodule_data)
    sys.exit()
if(len(sys.argv) > 1 and (sys.argv[1] == "sourceinfo" or sys.argv[1] == "getsourceinfo")):
    srcinfofilename = os.path.realpath("."+os.path.sep+pkg_resources.to_filename(
        pymodule['name'])+".egg-info"+os.path.sep+"SOURCES.txt")
    srcinfofile = open(srcinfofilename, "r")
    srcinfodata = srcinfofile.read()
    srcinfofile.close()
    srcinfolist = srcinfodata.split('\n')
    srcfilelist = ""
    srcpdir = os.path.basename(os.path.dirname(os.path.realpath(__file__)))
    for ifile in srcinfolist:
        srcfilelist = "."+os.path.sep+srcpdir+os.path.sep+ifile+" "+srcfilelist
    print(srcfilelist)
    sys.exit()
if(len(sys.argv) > 1 and sys.argv[1] == "cleansourceinfo"):
    os.system("rm -rfv \""+os.path.realpath("."+os.path.sep+"dist\""))
    os.system("rm -rfv \""+os.path.realpath("."+os.path.sep +
              pkg_resources.to_filename(pymodule['name'])+".egg-info\""))
    sys.exit()

if(pygenbuildinfo):
    mycurtime = datetime.datetime.now()
    mycurtimetuple = mycurtime.timetuple()
    mycurtimestamp = int(time.mktime(mycurtimetuple))
    '''verinfodata = verinfodata.replace('__build_time__ = {"timestamp": None, "year": None, "month": None, "day": None, "hour": None, "minute": None, "second": None};', '__build_time__ = {"timestamp": '+str(mycurtimestamp)+', "year": '+str(mycurtimetuple[0])+', "month": '+str(mycurtimetuple[1])+', "day": '+str(mycurtimetuple[2])+', "hour": '+str(mycurtimetuple[3])+', "minute": '+str(mycurtimetuple[4])+', "second": '+str(mycurtimetuple[5])+'};');'''
    verinfodata = re.sub("__build_time__ \= \{.*\}\;", '__build_time__ = {"timestamp": '+str(mycurtimestamp)+', "year": '+str(mycurtimetuple[0])+', "month": '+str(
        mycurtimetuple[1])+', "day": '+str(mycurtimetuple[2])+', "hour": '+str(mycurtimetuple[3])+', "minute": '+str(mycurtimetuple[4])+', "second": '+str(mycurtimetuple[5])+'};', verinfodata)
    utccurtime = datetime.datetime.utcnow()
    utccurtimetuple = utccurtime.timetuple()
    utccurtimestamp = int(time.mktime(utccurtimetuple))
    '''verinfodata = verinfodata.replace('__build_time_utc__ = {"timestamp": None, "year": None, "month": None, "day": None, "hour": None, "minute": None, "second": None};', '__build_time_utc__ = {"timestamp": '+str(utccurtimestamp)+', "year": '+str(utccurtimetuple[0])+', "month": '+str(utccurtimetuple[1])+', "day": '+str(utccurtimetuple[2])+', "hour": '+str(utccurtimetuple[3])+', "minute": '+str(utccurtimetuple[4])+', "second": '+str(utccurtimetuple[5])+'};');'''
    verinfodata = re.sub("__build_time_utc__ \= \{.*\}\;", '__build_time_utc__ = {"timestamp": '+str(utccurtimestamp)+', "year": '+str(utccurtimetuple[0])+', "month": '+str(
        utccurtimetuple[1])+', "day": '+str(utccurtimetuple[2])+', "hour": '+str(utccurtimetuple[3])+', "minute": '+str(utccurtimetuple[4])+', "second": '+str(utccurtimetuple[5])+'};', verinfodata)
    linuxdist = None
    try:
        linuxdist = platform.linux_distribution()
    except AttributeError:
        linuxdist = None
    if(sys.version[0] == "2"):
        '''verinfodata = verinfodata.replace('__build_python_info__ = {"python_branch": None, "python_build": None, "python_compiler": None, "python_implementation": None, "python_revision": None, "python_version": None, "python_version_tuple": None, "release": None, "system": None, "uname": None, "machine": None, "node": None, "platform": None, "processor": None, "version": None, "java_ver": None, "win32_ver": None, "mac_ver": None, "linux_distribution": None, "libc_ver": None};', '__build_python_info__ = '+str({'python_branch': platform.python_branch(), 'python_build': platform.python_build(), 'python_compiler': platform.python_compiler(), 'python_implementation': platform.python_implementation(), 'python_revision': platform.python_revision(), 'python_version': platform.python_version(), 'python_version_tuple': platform.python_version_tuple(), 'release': platform.release(), 'system': platform.system(), 'uname': platform.uname(), 'machine': platform.machine(), 'node': platform.node(), 'platform': platform.platform(), 'processor': platform.processor(), 'architecture': platform.architecture(), 'version': platform.version(), 'java_ver': platform.java_ver(), 'win32_ver': platform.win32_ver(), 'mac_ver': platform.mac_ver(), 'linux_distribution': linuxdist, 'libc_ver': platform.libc_ver()})+';');'''
        verinfodata = re.sub("__build_python_info__ \= \{.*\}\;", '__build_python_info__ = '+str({'python_branch': platform.python_branch(), 'python_build': platform.python_build(), 'python_compiler': platform.python_compiler(), 'python_implementation': platform.python_implementation(), 'python_revision': platform.python_revision(), 'python_version': platform.python_version(), 'python_version_tuple': platform.python_version_tuple(), 'release': platform.release(
        ), 'system': platform.system(), 'uname': platform.uname(), 'machine': platform.machine(), 'node': platform.node(), 'platform': platform.platform(), 'processor': platform.processor(), 'architecture': platform.architecture(), 'version': platform.version(), 'java_ver': platform.java_ver(), 'win32_ver': platform.win32_ver(), 'mac_ver': platform.mac_ver(), 'linux_distribution': linuxdist, 'libc_ver': platform.libc_ver()})+';', verinfodata)
    if(sys.version[0] == "3"):
        '''verinfodata = verinfodata.replace('__build_python_info__ = {"python_branch": None, "python_build": None, "python_compiler": None, "python_implementation": None, "python_revision": None, "python_version": None, "python_version_tuple": None, "release": None, "system": None, "uname": None, "machine": None, "node": None, "platform": None, "processor": None, "version": None, "java_ver": None, "win32_ver": None, "mac_ver": None, "linux_distribution": None, "libc_ver": None};', '__build_python_info__ = '+str({'python_branch': platform.python_branch(), 'python_build': platform.python_build(), 'python_compiler': platform.python_compiler(), 'python_implementation': platform.python_implementation(), 'python_revision': platform.python_revision(), 'python_version': platform.python_version(), 'python_version_tuple': platform.python_version_tuple(), 'release': platform.release(), 'system': platform.system(), 'uname': (platform.uname()[0], platform.uname()[1], platform.uname()[2], platform.uname()[3], platform.uname()[4], platform.uname()[5]), 'machine': platform.machine(), 'node': platform.node(), 'platform': platform.platform(), 'processor': platform.processor(), 'architecture': platform.architecture(), 'version': platform.version(), 'java_ver': platform.java_ver(), 'win32_ver': platform.win32_ver(), 'mac_ver': platform.mac_ver(), 'linux_distribution': linuxdist, 'libc_ver': platform.libc_ver()})+';');'''
        verinfodata = re.sub("__build_python_info__ \= \{.*\}\;", '__build_python_info__ = '+str({'python_branch': platform.python_branch(), 'python_build': platform.python_build(), 'python_compiler': platform.python_compiler(), 'python_implementation': platform.python_implementation(), 'python_revision': platform.python_revision(), 'python_version': platform.python_version(), 'python_version_tuple': platform.python_version_tuple(), 'release': platform.release(), 'system': platform.system(), 'uname': (
            platform.uname()[0], platform.uname()[1], platform.uname()[2], platform.uname()[3], platform.uname()[4], platform.uname()[5]), 'machine': platform.machine(), 'node': platform.node(), 'platform': platform.platform(), 'processor': platform.processor(), 'architecture': platform.architecture(), 'version': platform.version(), 'java_ver': platform.java_ver(), 'win32_ver': platform.win32_ver(), 'mac_ver': platform.mac_ver(), 'linux_distribution': linuxdist, 'libc_ver': platform.libc_ver()})+';', verinfodata)
    '''verinfodata = verinfodata.replace('__build_python_is_set__ = False;', '__build_python_is_set__ = True;');'''
    verinfodata = re.sub("__build_python_is_set__ \= .*\;",
                         '__build_python_is_set__ = True;', verinfodata)
    '''
    verinfofile = open(verinfofilename, "w")
    verinfofile.write(verinfodata)
    verinfofile.close()
    '''

if(len(sys.argv) > 1 and (sys.argv[1] == "buildcfg" or sys.argv[1] == "makecfg")):
    outcfgvar = """[project]
    name = "{}"
    version = "{}"
    readme = "README.md"
    license = {{ text = "BSD-3-Clause" }}
    keywords = []
    description = "{}"
    authors = [
        {{ name = "{}", email = "{}" }},
    ]
    """.format(pymodule['name'], pymodule['version'], pymodule['description'], pymodule['author'], pymodule['authoremail'])
    mytoml = open("./pyproject.toml", "w")
    mytoml.write(outcfgvar)
    mytoml.flush()
    if(hasattr(os, "sync")):
        os.fsync(mytoml.fileno())
    mytoml.close()
    sys.exit()

setup(
 name = pymodule['name'],
 version = pymodule['version'],
 author = pymodule['author'],
 author_email = pymodule['authoremail'],
 maintainer = pymodule['maintainer'],
 maintainer_email = pymodule['maintaineremail'],
 description = pymodule['description'],
 license = pymodule['license'],
 keywords = pymodule['keywords'],
 url = pymodule['url'],
 download_url = pymodule['downloadurl'],
 long_description = pymodule['longdescription'],
 platforms = pymodule['platforms'],
 zip_safe = pymodule['zipsafe'],
 py_modules = pymodule['pymodules'],
 scripts = pymodule['scripts'],
 classifiers = pymodule['classifiers']
)
