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
  <popup name="AutoPlaylistSourcePopup">
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
        self.playlist = shell.get_property("selected_source")
        self.proba()
        self.export_gtk_ui(shell)
    def export_playlist_global(self,action,shell):
        self.playlist = None
        self.export_gtk_ui(shell)
              
    def export_gtk_ui(self,shell):
        #self.proba(shell)
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_title("Playlist Exporter")
        window.set_default_size(512,215)
        
        vbox = gtk.VBox(False,5)
        
        #Add padding
        alignment = gtk.Alignment(xalign=0.0, yalign=0.0, xscale=1.0, yscale=1.0)
        alignment.add(vbox)
        alignment.set_padding(5,5,15,15)
        window.add(alignment)
        
        #Visual separator
        hseparator0 = gtk.HSeparator()
        vbox.add(hseparator0)
        
        #Playlist label
        pllabel = gtk.Label("Playlist")
        vbox.add(pllabel)
        
        self.playlist_combo = self.playlist_combobox(shell)
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
        button.connect("clicked",self.export,shell,self.playlist_combo)
        button.set_size_request(150,30)
        
        #Progress Bar
        self.progressbar = gtk.ProgressBar(adjustment=None)
        vbox.add(self.progressbar)
        
        alignment = gtk.Alignment(xalign=0.5, yalign=0.0, xscale=0.0, yscale=0.0)
        alignment.add(button)
        vbox.add(alignment)
        
        window.show_all()
        self.window = window
    def export(self,widget,shell,playlist_combo):
        if self.playlist_set_playlist(shell, self.playlist_combo.get_active()):
            expath = self.expfcb.get_filename()
            if self.checkbox.get_active():
                expath = expath+"/"+self.playlist_title
                os.system("mkdir '"+expath+"'")
            self.export_playlist(shell, expath)
        else:
            print "Playlist couldn't be set"
        
    def export_playlist(self,shell,expath):
        
        self.progressbar.set_fraction(0.0)
        self.noftracks = len(list(self.playlist.props.query_model))
        self.zfill = len(str(self.noftracks))
        for treerow in self.playlist.props.base_query_model:
            entry, trackn = list(treerow)
            uri = urllib.unquote(entry.get_playback_uri())
            uri = uri.replace("file://",'')
            title = shell.props.db.entry_get(entry, rhythmdb.PROP_TITLE)
            self.copy_command(expath,trackn, uri, title)
        self.window.destroy()
              
    
    def playlist_combobox(self,shell):
        index = 0
        i = 0
        combobox = gtk.combo_box_new_text()
        
        playlist_model_entries = [x for x in list(shell.props.sourcelist.props.model) if list(x)[2] == "Playlists"]
        if playlist_model_entries:
            playlist_iter = playlist_model_entries[0].iterchildren()
            for playlist_item in playlist_iter:
                combobox.append_text(playlist_item[2])
                if(playlist_item[3]==self.playlist):
                    index = i
                i=i+1
        
        combobox.set_active(index)
        return combobox
    
    def playlist_set_playlist(self,shell,index):
        i=0
        playlist_model_entries = [x for x in list(shell.props.sourcelist.props.model) if list(x)[2] == "Playlists"]
        if playlist_model_entries:
            playlist_iter = playlist_model_entries[0].iterchildren()
            for playlist_item in playlist_iter:
                if i==index:
                    self.playlist_title = playlist_item[2]
                    self.playlist = playlist_item[3]
                    return True
                i=i+1
        return False
    
    def copy_command(self,expath,trackn,uri,name):
            #Change progress bar
            self.progressbar.set_text(name+" ("+str(trackn)+" of "+str(self.noftracks)+")")
            self.progressbar.set_fraction(float(trackn)/float(self.noftracks))
            while gtk.events_pending():
                gtk.main_iteration()
            cpcommand = 'cp "'+uri+'" "'+expath+'/'+str(trackn).zfill(self.zfill)+' - '+name+'.mp3"'
            print cpcommand
            os.system(cpcommand)
            
    def proba(self):
        lista = list(self.playlist.props.query_model)
        self.noftracks = len(lista)
        print "noftracks: "+str(self.noftracks)
        i=0
        for x in lista:
            j=0
            print "Lista["+str(i)+"]: "+x.__str__()
            for y in x:
                print "Lista["+str(i)+"]["+str(j)+"]: "+y.__str__()
                j=j+1
            i=i+1
        
        
    def deactivate(self,shell):
        uim = shell.get_ui_manager()
        uim.remove_ui (self.ui_id)
        uim.remove_action_group (self.action_group)

        self.action_group = None
        self.action = None
        print "Playlist Exporter deactivated"