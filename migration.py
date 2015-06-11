import os
import sys

from rtcFunctions import ImportHandler
from rtcFunctions import WorkspaceHandler
from rtcFunctions import RTCInitializer
from gitFunctions import Initializer
from gitFunctions import Commiter
import configuration
import shouter


def initialize(config):
    directory = config.workDirectory
    if os.path.exists(directory):
        sys.exit("Configured directory already exists, please make sure to use a non-existing directory")
    os.mkdir(directory)
    os.chdir(directory)
    git = Initializer(config)
    git.initalize()
    RTCInitializer.initialize(config)
    git.initialcommitandpush()


def resume(config):
    os.chdir(config.workDirectory)
    os.chdir(config.clonedGitRepoName)
    RTCInitializer.loginandcollectstreams(config)
    WorkspaceHandler(config).load()


def migrate():
    config = configuration.read()
    rtc = ImportHandler(config)
    rtcworkspace = WorkspaceHandler(config)
    git = Commiter

    initialize(config)
    streamuuids = config.streamuuids
    for streamuuid in streamuuids:
        componentbaselineentries = rtc.getcomponentbaselineentriesfromstream(streamuuid)
        streamname = config.streamnames[streamuuids.index(streamuuid)]
        git.branch(streamname)

        history = rtc.readhistory(componentbaselineentries, streamname)
        changeentries = rtc.getchangeentriesofstreamcomponents(componentbaselineentries)

        rtc.acceptchangesintoworkspace(rtc.getchangeentriestoaccept(changeentries, history))
        shouter.shout("All changes of components of stream '%s' accepted" % streamname)
        git.pushbranch(streamname)

        rtcworkspace.setcomponentstobaseline(componentbaselineentries, streamuuid)
        rtcworkspace.load()

        changeentries = rtc.getchangeentriesofstream(streamuuid)
        rtc.acceptchangesintoworkspace(rtc.getchangeentriestoaccept(changeentries, history))
        git.pushbranch(streamname)
        shouter.shout("All changes of stream '%s' accepted - Migration of stream completed" % streamname)

        morestreamstomigrate = streamuuids.index(streamuuid) + 1 is not len(streamuuids)
        if morestreamstomigrate:
            git.checkout("master")
            rtcworkspace.recreateoldestworkspace()


migrate()
