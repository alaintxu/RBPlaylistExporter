#!/usr/bin/python
'''
Created on Dec 20, 2011

@author: Alain Perez
'''
import rb, rhythmdb
import gobject, gtk


ui_string = """
<ui>
  <menubar name="MenuBar"> 
    <menu name="MusicMenu" action="Music"> 
        <menu name="PlaylistMenu" action="Playlist">
         <separator name="ExportPlaylistSeparator1"/>
         <menuitem name="ExportPlaylistItem" action="ExportPlaylistGlobal"/>
        </menu>
    </menu>
  </menubar>
  <popup name="PlaylistSourcePopup">
    <separator name="ExportPlaylistSeparator1"/>
    <menuitem name="ExportPlaylistItem" action="ExportPlaylist"/>
  </popup>
</ui>"""

class RBPlaylistExporter (rb.Plugin):
    def __init__(self):
        rb.Plugin.__init__(self)
    
    def activate(self,shell):
        self.unique_action = gtk.Action('ExportPlaylist', _('Export tracks'),
                     _('Exports selected Playlist tracks into a folder'),
                     '')
        self.global_action = gtk.Action('ExportPlaylistGlobal', _('Export tracks'),
                     _('Exports all tracks of any Playlist into a folder'),
                     '')
        self.unique_activate_id = self.unique_action.connect('activate', self.export_playlist_unique, shell)
        self.global_activate_id = self.global_action.connect('activate', self.export_playlist_global, shell)
        
        self.action_group = gtk.ActionGroup('PlaylistExporterActionGroup')
        self.action_group.add_action(self.unique_action)
        self.action_group.add_action(self.global_action)
        
        ui_manager = shell.get_ui_manager ()
        self.ui_id = ui_manager.add_ui_from_string(ui_string)
        ui_manager.insert_action_group(self.action_group)
        ui_manager.ensure_update()
        
        print "Playlist Exporter activated!!!"
    def export_playlist_unique(self, action, shell):
        print "Function export_playlist_unique not implemented yet."
        source = shell.get_property("selected_source")
        #playlist = rb.Source.get_entry_view(source)
        #tracks = playlist.get_selected_entries()
        for treerow in source.props.base_query_model:
              entry, path = list(treerow)
              print entry
              artist = shell.props.db.entry_get(entry, rhythmdb.PROP_ARTIST)
              album = shell.props.db.entry_get(entry, rhythmdb.PROP_ALBUM)
              title = shell.props.db.entry_get(entry, rhythmdb.PROP_TITLE)
              duration = shell.props.db.entry_get(entry, rhythmdb.PROP_DURATION)
              print "%s - %s - %s" % (title, artist,path)
    def export_playlist_global(self,action,shell):
        print "Function export_playlist_global not implemented yet"
        
    def export_playlist(self,playlist,export_url):
        print "Function export_playlist not implemented yet"
    def deactivate(self,shell):
        uim = shell.get_ui_manager()
        uim.remove_ui (self.ui_id)
        uim.remove_action_group (self.action_group)

        self.action_group = None
        self.action = None
        print "Playlist Exporter deactivated"