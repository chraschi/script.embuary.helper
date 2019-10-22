#!/usr/bin/python
# coding: utf-8

########################

from __future__ import division

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import json
import random
import os
import locale

from resources.lib.helper import *
from resources.lib.library import *
from resources.lib.json_map import *
from resources.lib.image import *
from resources.lib.context import *
from resources.lib.cinema_mode import *

########################

''' Classes
'''
def blurimg(params):
    ImageBlur(prop=params.get('prop','output'),
              file=remove_quotes(params.get('file')),
              radius=params.get('radius',None)
              )


def playcinema(params):
    CinemaMode(dbid=params.get('dbid'),
               dbtype=params.get('type')
               )


def togglefav(params):
    Favourites(dbid=params.get('dbid'),
               dbtype=params.get('type')
               )

''' Functions
'''
def restartservice(params):
    execute('NotifyAll(%s, restart)' % ADDON_ID)


def calc(params):
    prop = remove_quotes(params.get('prop','CalcResult'))
    formula = remove_quotes(params.get('do'))
    result = eval(str(formula))
    winprop(prop, str(result))


def settimer(params):
    actions = remove_quotes(params.get('do'))
    time = params.get('time','50')
    delay = params.get('delay')
    busydialog = get_bool(params.get('busydialog','true'))

    if busydialog:
        execute('ActivateWindow(busydialognocancel)')

    xbmc.sleep(int(time))
    execute('Dialog.Close(all,true)')

    while visible('Window.IsVisible(busydialognocancel)'):
        xbmc.sleep(10)

    for action in actions.split('||'):
        execute(action)
        if delay:
            xbmc.sleep(int(delay))


def encode(params):
    string = remove_quotes(params.get('string'))
    prop = params.get('prop','EncodedString')
    winprop(prop,url_quote(string))


def decode(params):
    string = remove_quotes(params.get('string'))
    prop = params.get('prop','DecodedString')
    winprop(prop,url_unquote(string))


def createselect(params):
    selectionlist = []
    indexlist = []
    headertxt = remove_quotes(params.get('header', ''))
    splitby = remove_quotes(params.get('splitby', '||'))

    for i in range(1, 30):

        label = xbmc.getInfoLabel('Window.Property(Dialog.%d.Label)' % (i))

        if label == '':
            break
        elif label != 'none' and label != '-':
            selectionlist.append(label)
            indexlist.append(i)

    if selectionlist:
        index = DIALOG.select(headertxt, selectionlist)

        if index > -1:
            value = xbmc.getInfoLabel('Window.Property(Dialog.%d.Builtin)' % (indexlist[index]))
            for builtin in value.split(splitby):
                execute(builtin)
                xbmc.sleep(30)

    for i in range(1, 30):
        execute('ClearProperty(Dialog.%d.Builtin)' % i)
        execute('ClearProperty(Dialog.%d.Label)' % i)


def splitandcreateselect(params):
    headertxt = remove_quotes(params.get('header', ''))
    seperator = remove_quotes(params.get('seperator', ' / '))
    splitby = remove_quotes(params.get('splitby', '||'))
    selectionlist = remove_quotes(params.get('items')).split(seperator)

    if selectionlist:
        index = DIALOG.select(headertxt, selectionlist)

        if index > -1:
            value = xbmc.getInfoLabel('Window.Property(Dialog.Builtin)').replace('???',selectionlist[index])
            for builtin in value.split(splitby):
                execute(builtin)
                xbmc.sleep(30)

    execute('ClearProperty(Dialog.Builtin)')


def dialogok(params):
    headertxt = remove_quotes(params.get('header', ''))
    bodytxt = remove_quotes(params.get('message', ''))
    DIALOG.ok(heading=headertxt, line1=bodytxt)


def dialogyesno(params):
    headertxt = remove_quotes(params.get('header', ''))
    bodytxt = remove_quotes(params.get('message', ''))
    yesactions = params.get('yesaction', '').split('|')
    noactions = params.get('noaction', '').split('|')

    if DIALOG.yesno(heading=headertxt, line1=bodytxt):
        for action in yesactions:
            execute(action)
    else:
        for action in noactions:
            execute(action)


def textviewer(params):
    headertxt = remove_quotes(params.get('header', ''))
    bodytxt = remove_quotes(params.get('message', ''))
    DIALOG.textviewer(headertxt, bodytxt)


def getaddonsetting(params):
    addon_id = params.get('addon')
    addon_setting = params.get('setting')
    prop = addon_id + '-' + addon_setting

    try:
        setting = xbmcaddon.Addon(addon_id).getSetting(addon_setting)
        winprop(prop,str(setting))
    except Exception:
        winprop(prop, clear=True)


def togglekodisetting(params):
    settingname = params.get('setting', '')
    value = False if visible('system.getbool(%s)' % settingname) else True

    json_call('Settings.SetSettingValue',
                params={'setting': '%s' % settingname, 'value': value}
                )


def getkodisetting(params):
    setting = params.get('setting')
    strip = params.get('strip')

    json_query = json_call('Settings.GetSettingValue',
                params={'setting': '%s' % setting}
                )

    try:
        result = json_query['result']
        result = result.get('value')

        if strip == 'timeformat':
            strip = ['(12h)', ('(24h)')]
            for value in strip:
                if value in result:
                    result = result[:-6]

        result = str(result)
        if result.startswith('[') and result.endswith(']'):
           result = result[1:-1]

        winprop(setting,result)

    except Exception:
        winprop(setting, clear=True)


def setkodisetting(params):
    settingname = params.get('setting', '')
    value = params.get('value', '')

    try:
        value = int(value)
    except Exception:
        if value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False

    json_call('Settings.SetSettingValue',
                params={'setting': '%s' % settingname, 'value': value}
                )


def toggleaddons(params):
    addonid = params.get('addonid').split('+')
    enable = get_bool(params.get('enable'))

    for addon in addonid:

        try:
            json_call('Addons.SetAddonEnabled',
                params={'addonid': '%s' % addon, 'enabled': enable}
                )
            log('%s - enable: %s' % (addon, enable))
        except Exception:
            pass


def playsfx(params):
    xbmc.playSFX(remove_quotes(params.get('path', '')))


def stopsfx(params):
    xbmc.stopSFX()


def imginfo(params):
    prop = remove_quotes(params.get('prop','img'))
    img = remove_quotes(params.get('img'))
    if img:
        width,height,ar = image_info(img)
        winprop(prop + '.width',str(width))
        winprop(prop + '.height',str(height))
        winprop(prop + '.ar',str(ar))


def playitem(params):
    clear_playlists()

    dbtype = params.get('dbtype')
    dbid = params.get('dbid')

    if dbtype =='episode':
        itemtype = 'episodeid'
    elif dbtype =='song':
        itemtype = 'songid'
    else:
        itemtype = 'movieid'

    execute('Dialog.Close(all,true)')

    if dbid:
        json_call('Player.Open',
                    item={itemtype: int(dbid)}
                    )
    else:
        PLAYER.play(remove_quotes(params.get('item')))


def playfolder(params):
    clear_playlists()

    dbid = int(params.get('dbid'))
    shuffled = get_bool(params.get('shuffle'))

    if shuffled:
        winprop('script.shuffle.bool', True)

    if params.get('type') == 'season':
        json_query = json_call('VideoLibrary.GetSeasonDetails',
                                properties=['title','season','tvshowid'],
                                params={'seasonid': dbid}
                                )
        try:
            result = json_query['result']['seasondetails']
        except Exception as error:
            log('Play folder error getting season details: %s' % error)
            return

        json_query = json_call('VideoLibrary.GetEpisodes',
                                properties=episode_properties,
                                query_filter={'operator': 'is', 'field': 'season', 'value': '%s' % result['season']},
                                params={'tvshowid': int(result['tvshowid'])}
                                )
    else:
        json_query = json_call('VideoLibrary.GetEpisodes',
                            properties=episode_properties,
                            params={'tvshowid': dbid}
                            )

    try:
        result = json_query['result']['episodes']
    except Exception as error:
        log('Play folder error getting episodes: %s' % error)
        return

    for episode in result:
        json_call('Playlist.Add',
                item={'episodeid': episode['episodeid']},
                params={'playlistid': 1}
                )

    execute('Dialog.Close(all)')

    json_call('Player.Open',
            item={'playlistid': 1, 'position': 0},
            options={'shuffled': shuffled}
            )


def playall(params):
    clear_playlists()

    container = params.get('id')
    method = params.get('method')

    playlistid = 0 if params.get('type') == 'music' else 1
    shuffled = get_bool(method,'shuffle')

    if shuffled:
        winprop('script.shuffle.bool', True)

    if method == 'fromhere':
        method = 'Container(%s).ListItemNoWrap' % container
    else:
        method = 'Container(%s).ListItemAbsolute' % container

    for i in range(int(xbmc.getInfoLabel('Container(%s).NumItems' % container))):

        if visible('String.IsEqual(%s(%s).DBType,movie)' % (method,i)):
            media_type = 'movie'
        elif visible('String.IsEqual(%s(%s).DBType,episode)' % (method,i)):
            media_type = 'episode'
        elif visible('String.IsEqual(%s(%s).DBType,song)' % (method,i)):
            media_type = 'song'
        else:
            media_type = None

        dbid = xbmc.getInfoLabel('%s(%s).DBID' % (method,i))
        url = xbmc.getInfoLabel('%s(%s).Filenameandpath' % (method,i))

        if media_type and dbid:
            json_call('Playlist.Add',
                        item={'%sid' % media_type: int(dbid)},
                        params={'playlistid': playlistid}
                        )
        elif url:
            json_call('Playlist.Add',
                        item={'file': url},
                        params={'playlistid': playlistid}
                        )

    json_call('Player.Open',
                item={'playlistid': playlistid, 'position': 0},
                options={'shuffled': shuffled}
                )


def playrandom(params):
    clear_playlists()

    container = params.get('id')

    i = random.randint(1,int(xbmc.getInfoLabel('Container(%s).NumItems' % container)))

    if visible('String.IsEqual(Container(%s).ListItemAbsolute(%s).DBType,movie)' % (container,i)):
        media_type = 'movie'
    elif visible('String.IsEqual(Container(%s).ListItemAbsolute(%s).DBType,episode)' % (container,i)):
        media_type = 'episode'
    elif visible('String.IsEqual(Container(%s).ListItemAbsolute(%s).DBType,song)' % (container,i)):
        media_type = 'song'
    else:
        media_type = None

    item_dbid = xbmc.getInfoLabel('Container(%s).ListItemAbsolute(%s).DBID' % (dbid,i))
    url = xbmc.getInfoLabel('Container(%s).ListItemAbsolute(%s).Filenameandpath' % (dbid,i))

    playitem({'dbtype': media_type, 'dbid': item_dbid, 'item': url})


def jumptoshow_by_episode(params):
    episode_query = json_call('VideoLibrary.GetEpisodeDetails',
                    properties=['tvshowid'],
                    params={'episodeid': int(params.get('dbid'))}
                    )
    try:
        tvshow_id = str(episode_query['result']['episodedetails']['tvshowid'])
    except Exception:
        log('Could not get the TV show ID')
        return

    go_to_path('videodb://tvshows/titles/%s/' % tvshow_id)


def goto(params):
    go_to_path(remove_quotes(params.get('path')),params.get('target'))


def resetposition(params):
    containers = params.get('container').split('||')
    only_inactive_container = get_bool(params.get('only'),'inactive')
    current_control =xbmc.getInfoLabel('System.CurrentControlID')

    for item in containers:

        try:
            if current_control == item and only_inactive_container:
                raise Exception

            current_item = int(xbmc.getInfoLabel('Container(%s).CurrentItem' % item))
            if current_item > 1:
                current_item -= 1
                execute('Control.Move(%s,-%s)' % (item,str(current_item)))

        except Exception:
            pass


def details_by_season(params):
    season_query = json_call('VideoLibrary.GetSeasonDetails',
                        properties=season_properties,
                        params={'seasonid': int(params.get('dbid'))}
                        )

    try:
        tvshow_id = str(season_query['result']['seasondetails']['tvshowid'])
    except Exception:
        log('Show details by season: Could not get TV show ID')
        return

    tvshow_query = json_call('VideoLibrary.GetTVShowDetails',
                        properties=tvshow_properties,
                        params={'tvshowid': int(tvshow_id)}
                        )

    try:
        details = tvshow_query['result']['tvshowdetails']
    except Exception:
        log('Show details by season: Could not get TV show details')
        return

    episode = details['episode']
    watchedepisodes = details['watchedepisodes']
    unwatchedepisodes = get_unwatched(episode,watchedepisodes)

    winprop('tvshow.dbid', str(details['tvshowid']))
    winprop('tvshow.rating', str(round(details['rating'],1)))
    winprop('tvshow.seasons', str(details['season']))
    winprop('tvshow.episodes', str(episode))
    winprop('tvshow.watchedepisodes', str(watchedepisodes))
    winprop('tvshow.unwatchedepisodes', str(unwatchedepisodes))


def txtfile(params):
    prop = params.get('prop')
    path = xbmc.translatePath(remove_quotes(params.get('path')))

    if os.path.isfile(path):
        log('Reading file %s' % path)

        file = open(path, 'r')
        text = file.read()
        file.close()

        if prop:
            winprop(prop,text)
        else:
            DIALOG.textviewer(remove_quotes(params.get('header')),text)

    else:
        log('Cannot find %s' % path)
        winprop(prop, clear=True)


def fontchange(params):
    font = params.get('font')
    fallback_locales = params.get('locales').split('+')

    try:
        defaultlocale = locale.getdefaultlocale()
        shortlocale = defaultlocale[0][3:].lower()

        for value in fallback_locales:
            if value == shortlocale:
                setkodisetting({'setting': 'lookandfeel.font', 'value': params.get('font')})
                DIALOG.notification('%s %s' % (value.upper(),ADDON.getLocalizedString(32004)), '%s %s' % (ADDON.getLocalizedString(32005),font))
                log('Locale %s is not supported by default font. Change to %s.' % (value.upper(),font))
                break

    except Exception:
        log('Auto font change: No system locale found')


def setinfo(params):
    dbid = params.get('dbid')
    dbtype = params.get('type')
    value = remove_quotes(params.get('value'))

    try:
        value = int(value)
    except Exception:
        value = eval(value)
        pass

    if dbtype == 'movie':
        method = 'VideoLibrary.SetMovieDetails'
        key = 'movieid'
    elif dbtype == 'episode':
        method = 'VideoLibrary.SetEpisodeDetails'
        key = 'episodeid'
    elif dbtype == 'tvshow':
        method = 'VideoLibrary.SetTVShowDetails'
        key = 'tvshowid'

    json_call(method,
            params={key: int(dbid), params.get('field'): value}
            )


def split(params):
    value =  remove_quotes(params.get('value'))
    prop = params.get('prop')
    separator = remove_quotes(params.get('separator'))

    if value:
        if separator:
            value = value.split(separator)
        else:
            value = value.splitlines()

        i = 0
        for item in value:
            winprop('%s.%s' % (prop,i), item)
            i += 1

        for item in range(i,30):
            winprop('%s.%s' % (prop,i), clear=True)
            i += 1


def lookforfile(params):
    file = remove_quotes(params.get('file'))
    prop = params.get('prop','FileExists')

    if xbmcvfs.exists(file):
        winprop('%s.bool' % prop, True)
        log('File exists: %s' % file)
    else:
        winprop(prop, clear=True)
        log('File does not exist: %s' % file)


def getlocale(params):
    try:
        defaultlocale = locale.getdefaultlocale()
        shortlocale = defaultlocale[0][3:].upper()
        winprop('SystemLocale', shortlocale)
    except Exception:
        winprop('SystemLocale', clear=True)


def deleteimgcache(params,path=ADDON_DATA_IMG_PATH,delete=False):
    if not delete:
        if DIALOG.yesno(heading=ADDON.getLocalizedString(32003), line1=ADDON.getLocalizedString(32019)):
            delete = True

    if delete:
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            if os.path.isfile(full_path):
                os.remove(full_path)
            else:
                deleteimgcache(params,full_path,True)


def selecttags(params):
    tags = get_library_tags()

    if tags:
        setting = xbmc.getSkinDir() + '_' + 'library_tags'
        try:
            whitelist = eval(addon_data('tags_whitelist.' + xbmc.getSkinDir() +'.data'))
        except Exception:
            sync_library_tags(tags)
            whitelist = eval(addon_data('tags_whitelist.' + xbmc.getSkinDir() +'.data'))
        except Exception:
            whitelist = []

        indexlist = {}
        selectlist = []
        preselectlist = []

        index = 0
        for item in sorted(tags):
            selectlist.append(item)
            indexlist[index] = item
            if item in whitelist:
                preselectlist.append(index)
            index += 1

        selectdialog = DIALOG.multiselect(ADDON.getLocalizedString(32026), selectlist, preselect=preselectlist)

        if selectdialog is not None and not selectdialog:
            set_library_tags(tags,[],clear=True)

        elif selectdialog is not None:
            whitelist_new = []
            for item in selectdialog:
                whitelist_new.append(indexlist[item])

            if whitelist != whitelist_new:
                set_library_tags(tags,whitelist_new)

    elif params.get('silent') != 'true':
        DIALOG.ok(heading=ADDON.getLocalizedString(32000), line1=ADDON.getLocalizedString(32024))


def whitelisttags(params):
    sync_library_tags(recreate=True)