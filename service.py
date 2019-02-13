#!/usr/bin/python

from resources.lib.utils import log, grabfanart, ADDON_ID
from resources.lib.kodi_monitor import KodiMonitor
import xbmc
import xbmcgui
import xbmcaddon
import time
import random

WIN = xbmcgui.Window(10000)
ADDON = xbmcaddon.Addon(ADDON_ID)
PLAYER = xbmc.Player()
MONITOR = KodiMonitor(win=WIN, addon=ADDON, player=PLAYER)

task_interval = 300
cache_interval = 150
bg_task_interval = 200
bg_interval = 10
master_lock = "None"

log('Service started')

while not MONITOR.abortRequested():

	# Master lock reload logic for widgets
	if xbmc.getCondVisibility("System.HasLocks"):

		if master_lock == "None":
			master_lock = True if xbmc.getCondVisibility("System.IsMaster") else False
			log("Master mode: %s" % master_lock)

		if master_lock == True and not xbmc.getCondVisibility("System.IsMaster"):
			log("Left master mode. Reload skin.")
			master_lock = False
			xbmc.executebuiltin("ReloadSkin()")

		elif master_lock == False and xbmc.getCondVisibility("System.IsMaster"):
			log("Entered master mode. Reload skin.")
			master_lock = True
			xbmc.executebuiltin("ReloadSkin()")

	elif not master_lock == "None":
		master_lock = "None"

	# Grab fanarts
	if bg_task_interval >= 200:
		log("Start new fanart grabber process")
		fanarts = grabfanart()
		bg_task_interval = 0
	else:
		bg_task_interval += 10

	# Set fanart property
	if fanarts and bg_interval >=10:
		random.shuffle(fanarts)
		WIN.setProperty("EmbuaryBackground", fanarts[0])
		bg_interval = 0
	else:
		bg_interval += 10

	# Refresh widgets
	if task_interval >= 300:
		log("Update widget reload property")
		WIN.setProperty("EmbuaryWidgetUpdate", time.strftime("%Y%m%d%H%M%S", time.gmtime()))
		task_interval = 0
	else:
		task_interval += 10

	# Refresh cache
	if cache_interval >= 150:
		log("Update cache reload property")
		WIN.setProperty("EmbuaryCacheTime", time.strftime("%Y%m%d%H%M%S", time.gmtime()))
		cache_interval = 0
	else:
		cache_interval += 10

	MONITOR.waitForAbort(10)

del MONITOR
del WIN
del ADDON
log('Service stopped')