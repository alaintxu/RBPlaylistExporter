#!/usr/bin/python
'''
Created on Dec 20, 2011

@author: Alain Perez
'''
import rb, rhythmdb
import gobject, gtk
import os
import urllib


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

        playlist_source = shell.get_property("selected_source")
        self.export_gtk_ui(shell, playlist_source)
        '''export_url = "~/"
        self.export_playlist(shell,playlist_source, export_url)'''
    def export_playlist_global(self,action,shell):
        self.export_gtk_ui(shell,None)
              
    def export_gtk_ui(self,shell,playlist=None):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_title("Playlist Exporter")
        window.set_default_size(512,215)
        
        vbox = gtk.VBox(False,5)
        
        #Add padding
        alignment = gtk.Alignment(xalign=0.0, yalign=0.0, xscale=1.0, yscale=1.0)
        alignment.add(vbox)
        alignment.set_padding(5,5,15,15)
        window.add(alignment)
        
        self.playlist_combo = gtk.Combo()
        if(playlist!=None):
            #Playlist as an argument
            title = "Title"
            window.set_title("Playlist Exporter: "+title)
        else:
            #Visual separator
            hseparator0 = gtk.HSeparator()
            vbox.add(hseparator0)
            
            #Playlist label
            pllabel = gtk.Label("Playlist")
            vbox.add(pllabel)
            
            slist = self.playlist_list(shell)
            self.playlist_combo.set_popdown_strings(slist)
            vbox.add(self.playlist_combo)
        
        
            #Visual separator
            hseparator1 = gtk.HSeparator()
            vbox.add(hseparator1)
        
        #Export folder label
        explabel = gtk.Label("Export folder")
        vbox.add(explabel)
        
        #Export folder file chooser button
        self.expfcb = gtk.FileChooserButton("Browse")
        self.expfcb.set_title("Export folder")
        self.expfcb.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        self.expfcb.set_current_folder(os.getenv("HOME")+"/PlaylistExporter")
        vbox.add(self.expfcb)
        
        # Subfolder Checkbox
        self.checkbox = gtk.CheckButton("Create subfolder with playlist name", use_underline=True)
        self.checkbox.set_active(True) # Checked by default
        vbox.add(self.checkbox)
        
        hseparator2 = gtk.HSeparator()
        vbox.add(hseparator2)

        #Button
        button = gtk.Button("Export files")
        button.connect("clicked",self.export,shell,self.playlist_combo,playlist)
        button.set_size_request(150,30)
        
        #Progress Bar
        self.progressbar = gtk.ProgressBar(adjustment=None)
        vbox.add(self.progressbar)
        
        alignment = gtk.Alignment(xalign=0.5, yalign=0.0, xscale=0.0, yscale=0.0)
        alignment.add(button)
        vbox.add(alignment)
        
        window.show_all()
        self.window = window
    def export(self,widget,shell,playlist_combo,playlist):
        print "export function not implemented yet"
        expath = self.expfcb.get_filename()
        playlist_title = "Title"
        if self.checkbox.get_active():
            expath = expath+"/"+playlist_title
        if playlist!=None:
            self.export_playlist(shell,playlist, expath)
        
    def export_playlist(self,shell,playlist_source,expath):
        
        print "Function export_playlist not implemented yet"
        #playlist_list = list(playlist_source.props.base_query_model)
        #self.noftracks = list.count(playlist_list)#Ez dabil
        self.progressbar.set_fraction(0.0)
        self.noftracks = 36
        self.zfill = len(str(self.noftracks))
        for treerow in playlist_source.props.base_query_model:
            entry, trackn = list(treerow)
            uri = urllib.unquote(entry.get_playback_uri())
            uri = uri.replace("file://",'')
            title = shell.props.db.entry_get(entry, rhythmdb.PROP_TITLE)
            self.copy_command(expath,trackn, uri, title)
        self.window.destroy()
              
    
    def playlist_list(self,shell):
        print "playlist_list function not implemented yet"
        slist = [ "India","London","Singapore","China","Japan",
                        "France","germany","canada","UnitedStates","Mexico","Sydney","Holland"]
        return slist
    
    def copy_command(self,expath,trackn,uri,name):
            #Change progress bar
            self.progressbar.set_text(name+" ("+str(trackn)+" of "+str(self.noftracks)+")")
            self.progressbar.set_fraction(float(trackn)/float(self.noftracks))
            while gtk.events_pending():
                gtk.main_iteration()
            cpcommand = 'cp "'+uri+'" "'+expath+'/'+str(trackn).zfill(self.zfill)+' - '+name+'.mp3"'
            print cpcommand
            #os.system(cpcommand)
        
    def deactivate(self,shell):
        uim = shell.get_ui_manager()
        uim.remove_ui (self.ui_id)
        uim.remove_action_group (self.action_group)

        self.action_group = None
        self.action = None
        print "Playlist Exporter deactivated"