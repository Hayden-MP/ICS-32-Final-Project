
# A GUI to facilitate a graphical means to send and recieve messages from
# the DSP server

# Hayden Powers
# powersh@uci.edu
# 56169764

import tkinter as tk
from tkinter import ttk, filedialog, TclError
from Profile import Post, Profile
from ds_messenger import DirectMessenger
import copy


"""
A subclass of tk.Frame that is responsible for drawing all of the widgets
in the body portion of the root frame.
"""
class Body(tk.Frame):
    def __init__(self, root, select_callback=None):
        tk.Frame.__init__(self, root)
        self.root = root
        self._select_callback = select_callback

        # a list of the messages available in the active DSU file
        self._messages = []

        # A list of usernames that the current profile has sent/recieved messages
        self._contacts = []

        # This is what will be tied to each username so that when a contact is clicked on the
        # TreeView widget, it will display the chat history
        self._chat_history = []
        
        # After all initialization is complete, call the _draw method to pack the widgets
        # into the Body instance 
        self._draw()
    

    """
    Nodes will have the username of all the accounts that you have sent/recieved messages to.
    Clicking on a node will open the chat history (sent and recieved messages in chronologial order)
    """
    def node_select(self, event):
        digits = self.posts_tree.selection()[0][1:]
        leading_zeros = True
        value = ''

        # The .selection()[0] method of our treeview widget returns a 4 character string as an id
        # here I just got rid of the leading zeroes and got an accurate index value by converting
        # it from hexadecimal
        for i in digits:
            if i == '0' and leading_zeros:
                continue
            elif i != '0':
                leading_zeros = False
            value = value + i
            
        index = int(value, 16) - 1
        entry = self._messages[index]['message']
        self.set_text_entry(entry)

    """
    Returns the text that is currently displayed in the message_editor widget.
    """
    def get_text_entry(self) -> str:
        return self.message_editor.get('1.0', 'end').rstrip()

    """
    Sets the text to be displayed in the message_viewer widget.
    NOTE: This method is useful for clearing the widget, just pass an empty string.
    """
    def set_text_entry(self, text:str):
        self.message_viewer.delete("1.0","end")
        self.message_viewer.insert(0.0, text)

    
    """
    Populates the self._messages attribute with messages from the active DSU file.
    """
    def set_messages(self, messages:list):
        self._messages = copy.deepcopy(messages)
        for msg in self._messages:
            try:
                self._insert_post_tree(len(self._messages), msg)
            except TclError as e:
                continue


    """
    Populates the ._contacts attribute with the users from the acive DSU file
    """
    def set_contacts(self, users: list):
        self._contacts = copy.deepcopy(users)


    """
    Inserts a single post to the post_tree widget.
    """
    def insert_post(self, message: dict):
        self._messages.append(dict)
        id = len(self._messages) - 1 #adjust id for 0-base of treeview widget
        self._insert_post_tree(id, message)


    """
    Resets all UI widgets to their default state. Useful for when clearing the UI is neccessary such
    as when a new DSU file is loaded, for example.
    """
    def reset_ui(self):
        self.set_text_entry("")
        self.message_editor.configure(state=tk.NORMAL)
        self._messages = []
        for item in self.posts_tree.get_children():
            self.posts_tree.delete(item)

    """
    Inserts a post entry into the posts_tree widget.
    """
    def _insert_post_tree(self, id, message: list):
        # Title for messages in message tree will be the username of the 'frm' variable
        contact = message['frm']
        self.posts_tree.insert('', id, text=contact)


    """
    Will run on a timer to check for incoming messages to the user.
    """
    def update_messages(self, current_user: Profile):
        # TODO: Use a timer to check for new messages from server and add them to
        # chat history
        pass

    """
    Call only once upon initialization to add widgets to the frame
    """
    def _draw(self):
        posts_frame = tk.Frame(master=self, width=250)
        posts_frame.pack(fill=tk.BOTH, side=tk.LEFT)
        self.posts_tree = ttk.Treeview(posts_frame)
        self.posts_tree.bind("<<TreeviewSelect>>", self.node_select)
        self.posts_tree.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=5, pady=5)

        entry_frame = tk.Frame(master=self, bg="green")
        entry_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)

        # NEW FRAMES ------
        view_frame = tk.Frame(master=entry_frame, bg="orange")
        view_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        
        viewer_scroll_frame = tk.Frame(master=view_frame, bg="yellow", width=10)
        viewer_scroll_frame.pack(fill=tk.BOTH, side=tk.RIGHT, expand=False)

        message_frame = tk.Frame(master=entry_frame, bg="blue")
        message_frame.pack(fill=tk.BOTH, side=tk.BOTTOM, expand=True)

        editor_scroll_frame = tk.Frame(master=message_frame, bg="red", width=10)
        editor_scroll_frame.pack(fill=tk.BOTH, side=tk.RIGHT, expand=False)
        # -----------------


        # NEW WIDGETS ------
        self.message_viewer = tk.Text(master=view_frame, height= 20, width=0)
        self.message_viewer.pack(fill=tk.BOTH, side=tk.LEFT, expand=True, padx=1, pady=1)

        self.message_editor = tk.Text(master=message_frame, height=10, width=0)
        self.message_editor.pack(fill=tk.BOTH, side=tk.TOP, expand=True)

        message_viewer_scrollbar = tk.Scrollbar(master=viewer_scroll_frame, command=self.message_viewer.yview)
        self.message_viewer['yscrollcommand'] = message_viewer_scrollbar.set
        message_viewer_scrollbar.pack(fill=tk.Y, side=tk.LEFT, expand=False, padx=0, pady=0)

        message_editor_scrollbar = tk.Scrollbar(master=editor_scroll_frame, command=self.message_editor.yview)
        self.message_editor['yscrollcommand'] = message_editor_scrollbar.set
        message_editor_scrollbar.pack(fill=tk.Y, side=tk.LEFT, expand=False, padx=0, pady=0)
        # ----------------------------------------------


"""
A subclass of tk.Frame that is responsible for drawing all of the widgets
in the footer portion of the root frame.
"""
class Footer(tk.Frame):
    def __init__(self, root, send_callback=None, add_callback=None):
        tk.Frame.__init__(self, root)
        self.root = root
        self._send_callback = send_callback
        self._add_callback = add_callback

        # IntVar is a variable class that provides access to special variables
        # for Tkinter widgets. is_online is used to hold the state of the chk_button widget.
        # The value assigned to is_online when the chk_button widget is changed by the user
        # can be retrieved using he get() function:
        # chk_value = self.is_online.get()
        self.is_online = tk.IntVar()
        # After all initialization is complete, call the _draw method to pack the widgets
        # into the Footer instance 
        self._draw()
    

    """
    Calls the callback function specified in the online_callback class attribute, if
    available, when the chk_button widget has been clicked.
    """
    def add_click(self):
        if self._add_callback is not None:
            self._add_callback()


    """
    Calls the callback function specified in the save_callback class attribute, if
    available, when the save_button has been clicked.
    """
    def send_click(self):
        if self._send_callback is not None:
            self._send_callback()
    

    """
    Call only once upon initialization to add widgets to the frame
    """
    def _draw(self):
        send_button = tk.Button(master=self, text="Send Message", width=20)
        send_button.configure(command=self.send_click)
        send_button.pack(fill=tk.BOTH, side=tk.RIGHT, padx=5, pady=5)

        # ADD USER BUTTON INSTEAD OF READY LABEL
        add_user_button = tk.Button(master=self, text="Add User", width=10)
        add_user_button.configure(command=self.add_click)
        add_user_button.pack(fill=tk.BOTH, side=tk.LEFT, padx=10, pady=5)


"""
A subclass of tk.Frame that is responsible for drawing all of the widgets
in the main portion of the root frame. Also manages all method calls for
the Profile class.
"""
class MainApp(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root

        # Initialize a new Profile and assign it to a class attribute.
        self._current_profile = Profile()

        # After all initialization is complete, call the _draw method to pack the widgets
        # into the root frame
        self._draw()


    """
    Takes the message from the message editor and sends it through the DSP server 
    to the specified username
    """
    def send_message(self):
        # May need to plan this to accept an index from a contacts list instead of
        # passing in a username. 
        message = self.body.get_text_entry()
        print("MESSAGE SENT: ", message)

        # Need to figure out what user we are looking at to send message to
        dm_user = DirectMessenger(username = self._current_profile.username, 
                                            password = self._current_profile.username)
                                            


    """
    Creates a new DSU file when the 'New' menu item is clicked.
    """
    def new_profile(self):
        filename = tk.filedialog.asksaveasfile(filetypes=[('Distributed Social Profile', '*.dsu')], defaultextension='.dsu')
        try:
            self._profile_filename = filename.name
            self._current_profile = Profile()
            self.body.reset_ui()
        except AttributeError as e:
            print("New profile operation interrupted.")

        # Opens a new popup window for user to enter their own username and password
        if self._profile_filename is False:
            print("No filename provided")
            return    
        else:
            self.popup_window()
        

    """
    A popup window that will prompt the user for username and password when creating a new file
    """
    def popup_window(self):
        self.popup = tk.Toplevel()

        user_label = tk.Label(master=self.popup, text="Username")
        user_label.pack(fill='x', padx=50, pady=5)
        self.user_input = tk.Text(master=self.popup, height=1, width=20)
        self.user_input.pack(fill='x', padx=50, pady=5)

        password_label = tk.Label(master=self.popup, text="Password")
        password_label.pack(fill='x', padx=50, pady=5)
        self.password_input= tk.Text(master=self.popup, height=1, width=20)
        self.password_input.pack(fill='x', padx=50, pady=5)

        button_submit = tk.Button(master=self.popup, text="Submit", width=5, command=lambda: self.submit_info())
        button_submit.pack(fill='x')


    """
    The command used by the submit button in the popup window to set the current profile username
    and password and save profile to the dsu file
    """
    def submit_info(self):            
        self._current_profile.username = self.user_input.get("1.0",'end-1c')
        self._current_profile.password = self.password_input.get("1.0",'end-1c')

        # If either text field is empty after clicking submit - set to default values
        if self._current_profile.username == '':
            self._current_profile.username = "dusername123"
        if self._current_profile.password == '':
            self._current_profile.password = "dpassword123"

        self._current_profile.save_profile(self._profile_filename)
        self.popup.destroy()


    """
    Opens an existing DSU file when the 'Open' menu item is clicked and loads the profile
    data into the UI.
    """
    def open_profile(self):
        filename = tk.filedialog.askopenfile(filetypes=[('Distributed Social Profile', '*.dsu')])
        try:
            self._profile_filename = filename.name
            self._current_profile = Profile()
            self._current_profile.load_profile(self._profile_filename)
            self.body.reset_ui() # Reset UI
            self.body.set_messages(self._current_profile._messages)
            self.body.set_contacts(self._current_profile._users)

        except AttributeError as e:
            print("Open operation interrupted.")
         

    """
    Closes the program when the 'Close' menu item is clicked.
    """
    def close(self):
        self.root.destroy()


    """
    Saves the text currently in the message_editor widget to the active DSU file.
    """
    def save_profile(self):
        # Check for filename
        if self._profile_filename is False:
            print("No filename provided")
            return            
        
        # NEED TO FIGURE OUT HOW TO SAVE CHAT HISTORY TO DSU
    

    """
    A callback function for responding to the add_user button. Will connect with the body
    to insert an empty chat history with a given username supplied by the message editor
    """
    def add_user(self):
        contact_username = self.body.get_text_entry()
        print("USER ADDED: ", contact_username)

    
    """
    Call only once, upon initialization to add widgets to root frame
    """
    def _draw(self):
        # Build a menu and add it to the root frame.
        menu_bar = tk.Menu(self.root)
        self.root['menu'] = menu_bar
        menu_file = tk.Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_file, label='File')
        menu_file.add_command(label='New', command=self.new_profile)
        menu_file.add_command(label='Open...', command=self.open_profile)
        menu_file.add_command(label='Close', command=self.close)

        # The Body and Footer classes must be initialized and packed into the root window.
        self.body = Body(self.root, self._current_profile)
        self.body.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        self.footer = Footer(self.root, send_callback=self.send_message, add_callback=self.add_user)
        self.footer.pack(fill=tk.BOTH, side=tk.BOTTOM)



if __name__ == "__main__":
    # All Tkinter programs start with a root window. We will name ours 'main'.
    main = tk.Tk()

    # 'title' assigns a text value to the Title Bar area of a window.
    main.title("ICS 32 Distributed Social Demo")

    # This is just an arbitrary starting point. You can change the value around to see how
    # the starting size of the window changes. I just thought this looked good for our UI.
    main.geometry("720x480")

    # adding this option removes some legacy behavior with menus that modern OSes don't support. 
    # If you're curious, feel free to comment out and see how the menu changes.
    main.option_add('*tearOff', False)

    # Initialize the MainApp class, which is the starting point for the widgets used in the program.
    # All of the classes that we use, subclass Tk.Frame, since our root frame is main, we initialize 
    # the class with it.
    MainApp(main)

    # When update is called, we finalize the states of all widgets that have been configured within the root frame.
    # Here, Update ensures that we get an accurate width and height reading based on the types of widgets
    # we have used.
    # minsize prevents the root window from resizing too small. Feel free to comment it out and see how
    # the resizing behavior of the window changes.
    main.update()
    main.minsize(main.winfo_width(), main.winfo_height())
    # And finally, start up the event loop for the program (more on this in lecture).
    main.mainloop()