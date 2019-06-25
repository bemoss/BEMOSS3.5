# -*- coding: utf-8 -*-
'''
Copyright (c) 2016, Virginia Tech
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
 following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
The views and conclusions contained in the software and documentation are those of the authors and should not be
interpreted as representing official policies, either expressed or implied, of the FreeBSD Project.
This material was prepared as an account of work sponsored by an agency of the United States Government. Neither the
United States Government nor the United States Department of Energy, nor Virginia Tech, nor any of their employees,
nor any jurisdiction or organization that has cooperated in the development of these materials, makes any warranty,
express or implied, or assumes any legal liability or responsibility for the accuracy, completeness, or usefulness or
any information, apparatus, product, software, or process disclosed, or represents that its use would not infringe
privately owned rights.
Reference herein to any specific commercial product, process, or service by trade name, trademark, manufacturer, or
otherwise does not necessarily constitute or imply its endorsement, recommendation, favoring by the United States
Government or any agency thereof, or Virginia Tech - Advanced Research Institute. The views and opinions of authors
expressed herein do not necessarily state or reflect those of the United States Government or any agency thereof.
VIRGINIA TECH – ADVANCED RESEARCH INSTITUTE
under Contract DE-EE0006352
#__author__ = "BEMOSS Team"
#__credits__ = ""
#__version__ = "2.0"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2014-09-12 12:04:50"
#__lastUpdated__ = "2016-03-14 11:23:33"
'''


import Tkinter
import ttk
import os
import subprocess
import re
import tkMessageBox
import netifaces
from PIL import Image
from PIL import ImageTk
import shutil
import volttronFunc

class GUI:
    def __init__(self):

        self.passwd = None
        self.do_update = False

        # current working directory
        self.gui_file = os.path.realpath(__file__)
        self.gui_path = self.gui_file.replace('/GUI.py','')
        self.project_path = self.gui_path.replace('/GUI', '')
 
        # logoimage
        img_path = self.find_img()
        self.logo = ImageTk.PhotoImage(Image.open(img_path).resize((350, 125)))
        self.img = ttk.Label(root, image=self.logo, justify='center')
        self.img.pack(fill=Tkinter.Y, expand=True, padx=5, pady=30)

        # IP
        self.ip_addr = self.getIPs()
        self.ipframe = Tkinter.LabelFrame(root, text='Your IP address:')
        self.ip_label = Tkinter.Label(self.ipframe, text=self.ip_addr, font=('Courier', 12, 'bold'))
        self.ip_label.pack()
        self.ipframe.pack(fill=Tkinter.X, expand=True, padx=15)

        # buttons
        self.button_quit = ttk.Button(root, text='Run BEMOSS', command=self.run_software)
        self.button_quit.pack(side=Tkinter.LEFT, fill=Tkinter.BOTH, expand=True, pady=15, padx=10)
        self.button_adv = ttk.Button(root, text='Advanced Setting', command=self.adv_set)
        self.button_adv.pack(side=Tkinter.LEFT, fill=Tkinter.BOTH, expand=True, pady=15, padx=10)

    def find_img(self):

        path = self.gui_path + '/BEMOSS_logo.png'
        return path

    def getIPs(self):
        IPs = []
        ip_string = ''
        interfaces = netifaces.interfaces()
        for i in interfaces:
            if i == 'lo':
                continue
            iface = netifaces.ifaddresses(i).get(netifaces.AF_INET)
            if iface is not None:
                for j in iface:
                    IPs.append(j['addr'])
                    ip_string += str(j['addr'])
        return ip_string

    def detect_bemoss(self):
        ui_path = self.project_path+'/Web_Server'
        cassandra_path = self.project_path + '/cassandra/bin'
        env_path = self.project_path + '/env/bin'
        bemoss_is_installed = os.path.isdir(ui_path) and os.path.isdir(cassandra_path) and os.path.isdir(env_path)

        if bemoss_is_installed is False:
            tmp = tkMessageBox.askokcancel(title='Please install BEMOSS at first',
                                           message='You computer does not have BEMOSS installed, do you want to install BEMOSS right now?',
                                           parent=root)
            if tmp is True:
                self.install_bemoss()
                return
            else:
                return False
        else:
            return True


    def run_software(self):
        bemoss_installed = self.detect_bemoss()
        if bemoss_installed: self.run_bemoss()

    def install_bemoss(self):
        path = 'nohup x-terminal-emulator -e "bash -c \'./bemoss_install_v3.5.sh; bash\'"'
        subprocess.Popen(path, shell=True)

    def run_bemoss(self):
        path = 'nohup x-terminal-emulator -e "bash -c \'./runBEMOSS.sh; bash\'"'
        subprocess.Popen(path, cwd=self.project_path, shell=True)

    def adv_set(self):
        bemoss_installed = self.detect_bemoss()
        if bemoss_installed: self.new_win()

    def new_win(self):
        # advanced setting window
        window = Tkinter.Toplevel(root)
        window.title('Advanced Setting')
        x = root.winfo_rootx()
        y = root.winfo_rooty()
        window.geometry('+%d+%d' % (x+150, y+100))
        window.resizable(True, True)
        window.minsize(height=550, width=530)
        window.lift(root)

        # add 4 tabs in advanced setting window(Setting,VOLTTRON,Database,System Montior)
        notebook = ttk.Notebook(window)
        notebook.pack(fill=Tkinter.BOTH, expand=True)
        self.frame1 = ttk.Frame(notebook)
        self.frame2 = ttk.Frame(notebook)
        self.frame3 = ttk.Frame(notebook)
        # notebook.add(self.frame1, text='Setting')
        notebook.add(self.frame1, text='VOLTTRON')
        notebook.add(self.frame2, text='Database')
        notebook.add(self.frame3, text='System Monitor')
    
        #tab1 VOLTTRON
        self.frame1.config(height=550, width=530)
        textframe = ttk.Frame(self.frame1)
        textframe.pack(fill=Tkinter.BOTH, expand=True, padx=7, pady=4)
        scrollbar = ttk.Scrollbar(textframe)
        scrollbar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
        self.VOL_text = Tkinter.Text(textframe, bg='white',
                                yscrollcommand=scrollbar.set, wrap='word')
        self.VOL_text.pack(side=Tkinter.LEFT, expand=True, fill=Tkinter.BOTH)
        scrollbar.config(command=self.VOL_text.yview)
        view_but = ttk.Button(self.frame1, text='View Agent Status', command=self.check_agent_status)
        view_but.pack(padx=5, pady=5)
        butframe1 = ttk.Frame(self.frame1)
        butframe1.pack()
        stop_but = ttk.Button(butframe1, text='Stop Agent', command=self.agent_stop)
        stop_but.pack(side=Tkinter.RIGHT, padx=5, pady=2.5)
        start_but = ttk.Button(butframe1, text='Start Agent', command=self.agent_start)
        start_but.pack(side=Tkinter.RIGHT, padx=5, pady=2.5)
        self.agent = Tkinter.StringVar()
        VOL_entry = ttk.Entry(butframe1, width=15, textvariable=self.agent)
        VOL_entry.pack(side=Tkinter.RIGHT, padx=5, pady=2.5)
        agid = ttk.Label(butframe1, text='Agent ID:')
        agid.pack(side=Tkinter.RIGHT, padx=5, pady=2.5)
        butframe2 = ttk.Frame(self.frame1)
        butframe2.pack()

        #tab2 Database
        self.frame2.config(height=550, width=530)
        postframe = Tkinter.LabelFrame(self.frame2, text='Postgresql')
        postframe.pack(fill=Tkinter.BOTH, expand=True, padx=7, pady=5)
        ACS_but= ttk.Button(postframe, text='Open Configure File', command=self.open_pg_config)
        LP_but = ttk.Button(postframe, text='Launch PgAdmin3', command=self.start_pgadm)
        ACS_but.pack(fill=Tkinter.BOTH, expand=True, padx=5, pady=3)
        LP_but.pack(fill=Tkinter.BOTH, expand=True, padx=5, pady=3)
        casframe = Tkinter.LabelFrame(self.frame2, text='Cassandra')
        casframe.pack(fill=Tkinter.BOTH, expand=True, padx=7, pady=5)
        DSF_but= ttk.Button(casframe, text='Delete Setting File', command=self.del_cas)
        DD_but = ttk.Button(casframe, text='Delete Data', command=self.del_dat)
        LIT_but = ttk.Button(casframe, text='Launch in Terminal', command=self.start_cas)
        DSF_but.pack(side=Tkinter.LEFT, fill=Tkinter.BOTH, expand=True, padx=3, pady=5)
        DD_but.pack(side=Tkinter.LEFT, fill=Tkinter.BOTH, expand=True, padx=3, pady=5)
        LIT_but.pack(side=Tkinter.LEFT, fill=Tkinter.BOTH, expand=True, padx=3, pady=5)

        # tab3 System monitor
        self.frame3.config(height=550, width=530)
        self.frame3.rowconfigure(0, weight=1)
        self.frame3.rowconfigure(1, weight=1)
        self.frame3.rowconfigure(2, weight=1)
        self.frame3.rowconfigure(3, weight=1)
        self.frame3.rowconfigure(4, weight=1)
        self.frame3.rowconfigure(5, weight=1)
        self.frame3.rowconfigure(6, weight=1)
        self.frame3.rowconfigure(7, weight=1)
        self.frame3.columnconfigure(0, weight=2)
        self.frame3.columnconfigure(1, weight=1)
        self.frame3.columnconfigure(2, weight=1)
        self.frame3.columnconfigure(3, weight=1)
        self.frame3.columnconfigure(4, weight=1)
        self.frame3.columnconfigure(5, weight=1)
        LA_lab = ttk.Label(self.frame3, text='LOAD AVERAGE')
        LA_lab.grid(row=1, column=1, columnspan=2, sticky='w')
        self.var_LA = Tkinter.StringVar()
        LA_lab_Entry = Tkinter.Entry(self.frame3, width=35, state='readonly',
                                     textvariable=self.var_LA)
        LA_lab_Entry.grid(row=1, column=3, columnspan=2, sticky='w')
        CPU_UU = ttk.Label(self.frame3, text='CPU(USER USED)')
        CPU_UU.grid(row=2, column=1, columnspan=2, sticky='w')
        self.var_UU = Tkinter.StringVar()
        CPU_UU_Entry = Tkinter.Entry(self.frame3, width=35, state='readonly',
                                     textvariable=self.var_UU)
        CPU_UU_Entry.grid(row=2, column=3, columnspan=2, sticky='w')
        CPU_SU = ttk.Label(self.frame3, text='CPU(SYSTEM USED)')
        CPU_SU.grid(row=3, column=1, columnspan=2, sticky='w')
        self.var_SU = Tkinter.StringVar()
        CPU_SU_Entry = Tkinter.Entry(self.frame3, width=35, state='readonly',
                                     textvariable=self.var_SU)
        CPU_SU_Entry.grid(row=3, column=3, columnspan=2, sticky='w')
        CPU_IDLE= ttk.Label(self.frame3, text='CPU(IDLE)')
        CPU_IDLE.grid(row=4, column=1, columnspan=2, sticky='w')
        self.var_IDLE = Tkinter.StringVar()
        CPU_IDLE_Entry = Tkinter.Entry(self.frame3, width=35,state='readonly',
                                       textvariable=self.var_IDLE)
        CPU_IDLE_Entry.grid(row=4, column=3, columnspan=2, sticky='w')
        MEM_T = ttk.Label(self.frame3, text='MEMORY(TOTAL)')
        MEM_T.grid(row=5, column=1,  columnspan=2, sticky='w')
        self.var_MT = Tkinter.StringVar()
        MEM_T_Entry = Tkinter.Entry(self.frame3, width=35, state='readonly',
                                    textvariable=self.var_MT)
        MEM_T_Entry.grid(row=5, column=3, columnspan=2, sticky='w')
        MEM_F = ttk.Label(self.frame3, text='MEMORY(USED)')
        MEM_F.grid(row=6, column=1,  columnspan=2, sticky='w')
        self.var_MF = Tkinter.StringVar()
        MEM_F_Entry = Tkinter.Entry(self.frame3, width=35, state='readonly',
                                    textvariable=self.var_MF)
        MEM_F_Entry.grid(row=6, column=3, columnspan=2, sticky='w')
        Get_data = ttk.Button(self.frame3, text='Get Data', command=self.sys_monitor)
        Get_data.grid(row=7, column=4, sticky='e', padx=5)
        self.auto = Tkinter.BooleanVar()
        auto_update = Tkinter.Checkbutton(self.frame3, text='Auto-update', variable=self.auto,
                                          onvalue=True, offvalue=False, command=self.updateonoroff)
        auto_update.grid(row=7, column=4, sticky='w')



    # Frame1 functions
    def check_agent_status(self):
        output = volttronFunc.agent_status(self.project_path)
        if output == '':
            tkMessageBox.showerror(title="Notification", message='Sorry, volttron is not running in your virtual environment.', parent=self.frame1)
            return
        else:
            self.VOL_text.configure(state='normal')
            self.VOL_text.delete('1.0', Tkinter.END)
            self.VOL_text.insert('1.0', output)
            self.VOL_text.configure(state='disabled')

    def agent_stop(self):
        volttronFunc.stop_agent(self.project_path, self.agent.get())
        self.VOL_text.after(5000, self.check_agent_status)

    def agent_start(self):
        volttronFunc.start_agent(self.project_path, self.agent.get())
        self.VOL_text.after(3000, self.check_agent_status)


    def search_running_agent(self, target):
        output = volttronFunc.agent_status(self.project_path)
        try:
            output1 = output.split('\n')

            running_agent = list()
            target += 'agent'
            platform_agent = None

            for item in output1:
                item_decom = item.split(' ')
                item_decom_short = [id for id in item_decom if id]
                if target in item:
                    running_agent.append(item_decom_short)
                if 'platformmonitoragent' in item:
                    platform_agent = item_decom_short[0]
            return running_agent, platform_agent
        except Exception as er:
            print er

    # Frame2 functions
    def get_passwd_ocf(self):
        self.passwd_window_ocf = Tkinter.Toplevel(self.frame2)
        self.passwd_window_ocf.title('Postgres Auth(System Password)')
        x = self.frame2.winfo_rootx()
        y = self.frame2.winfo_rooty()
        self.passwd_window_ocf.geometry('350x130+%d+%d' % (x+150, y+100))
        self.passwd_window_ocf.lift()
        self.passwd_window_ocf.columnconfigure(0, weight=1)
        self.passwd_window_ocf.columnconfigure(1, weight=1)
        self.passwd_window_ocf.columnconfigure(2, weight=1)
        self.passwd_window_ocf.columnconfigure(3, weight=2)
        self.passwd_window_ocf.columnconfigure(4, weight=2)
        self.passwd_window_ocf.columnconfigure(5, weight=1)
        self.passwd_window_ocf.rowconfigure(0, weight=1)
        self.passwd_window_ocf.rowconfigure(1, weight=2)
        self.passwd_window_ocf.rowconfigure(2, weight=2)
        self.passwd_window_ocf.rowconfigure(3, weight=2)
        self.passwd_window_ocf.rowconfigure(4, weight=1)
        self.passwd_window_ocf.resizable(False, False)
        reminder = ttk.Label(self.passwd_window_ocf, text='Please input the system password.')
        reminder.grid(row=1, column=1, columnspan=4, sticky='w')
        self.pswd_ocf = Tkinter.StringVar()
        pwentry = Tkinter.Entry(self.passwd_window_ocf, textvariable=self.pswd_ocf, width=30)
        pwentry.focus_set()
        pwentry.grid(row=2, column=3, columnspan=2, sticky='w', padx=10)
        pwentry.config(show='*')
        pswdlabel = ttk.Label(self.passwd_window_ocf, text='Password:')
        pswdlabel.grid(row=2, column=2, sticky='e', padx=10)
        confirm_but = ttk.Button(self.passwd_window_ocf, text='Confirm', command=self.pwconfirm_ocf)
        confirm_but.grid(row=3, column=4, sticky='w', padx=5)
        clear_but = ttk.Button(self.passwd_window_ocf, text='Clear',
                               command=lambda: pwentry.delete(0, Tkinter.END))
        clear_but.grid(row=3, column=3, sticky='e', padx=5)
        self.passwd_window_ocf.bind('<Return>', self.shortcut3)

    def shortcut3(self, event):
        self.pwconfirm_ocf()

    def pwconfirm_ocf(self):
        password_ocf = self.pswd_ocf.get()
        self.open_pg_config_func(password_ocf)
        self.passwd_window_ocf.state('withdrawn')

    def open_pg_config(self):
        # First check postgresql version
        if self.passwd is None or self.passwd == 'nosudo':
            self.get_passwd_ocf()
        else:
            self.open_pg_config_func(self.passwd)

    def open_pg_config_func(self, sys_password):
        version = os.listdir('/etc/postgresql')
        # look for available text editors
        softwares = os.listdir('/usr/bin')
        if 'gedit' in softwares:
            editor = 'gedit '
        elif ('leafpad' in softwares):
            editor = 'leafpad '
        # using text editor to open configure file
        try:
            cmd = 'echo \'' + str(sys_password) + '\' |sudo -S ' + editor + '/etc/postgresql/' + version[0] + '/main/postgresql.conf'
            subprocess.Popen(cmd, shell=True)
            cmd = 'echo \'' + str(sys_password) + '\' |sudo -S ' + editor + '/etc/postgresql/' + version[0] + '/main/pg_hba.conf'
            subprocess.Popen(cmd, shell=True)
        except Exception as er:
            print er
            print('No gedit or leafpad editor installed.')

    def start_pgadm(self):
        cmd = 'nohup x-terminal-emulator -e pgadmin3'
        subprocess.Popen(cmd, shell=True)

    def del_dat(self):
        cnt = tkMessageBox.askokcancel(title='Reconfirmation',
                                       message='Are you sure to delete the data?',
                                       parent=self.frame2)
        if cnt is True:
            cas_data_dir = os.path.join(self.project_path, 'cassandra/data')
            shutil.rmtree(cas_data_dir)
        else:
            return

    def del_cas(self):
        cnt = tkMessageBox.askokcancel(title='Reconfirmation',
                                       message='Are you sure to delete the file?',
                                       parent=self.frame2)
        if cnt is True:
            path = self.project_path + '/cassandra_settings.txt'
            os.remove(path)
        else:
            return

    def start_cas(self):
        # add log in pop up here to let the user to input the username and password. Save then in cas_usr and cas_pw
        self.login_window = Tkinter.Toplevel(root)
        self.login_window.title('Cassandra Log in')
        self.login_window.lift()
        x = self.frame2.winfo_rootx()
        y = self.frame2.winfo_rooty()
        self.login_window.geometry('300x170+%d+%d' % (x+150, y+100))
        self.login_window.rowconfigure(0, weight=1)
        self.login_window.rowconfigure(1, weight=1)
        self.login_window.rowconfigure(2, weight=1)
        self.login_window.rowconfigure(3, weight=1)
        self.login_window.rowconfigure(4, weight=1)
        self.login_window.columnconfigure(0, weight=1)
        self.login_window.columnconfigure(1, weight=1)
        self.login_window.columnconfigure(2, weight=1)
        self.login_window.columnconfigure(3, weight=1)
        self.login_window.resizable(False, False)
        unlabel = ttk.Label(self.login_window, text='Username:')
        unlabel.grid(row=1, column=1)
        pwlabel = ttk.Label(self.login_window, text='Password:')
        pwlabel.grid(row=2, column=1)
        self.username_cas = Tkinter.StringVar()
        self.password_cas = Tkinter.StringVar()
        unentry = ttk.Entry(self.login_window, textvariable=self.username_cas, width=20)
        unentry.focus_set()
        unentry.grid(row=1, column=2)
        pwentry = ttk.Entry(self.login_window, textvariable=self.password_cas, width=20)
        pwentry.grid(row=2, column=2)
        pwentry.configure(show='*')
        conf_but = ttk.Button(self.login_window, text='Confirm', command=self.checkuser)
        conf_but.grid(row=3, column=2, sticky='e')
        self.login_window.bind('<Return>', self.shortcut2)

    def shortcut2(self, event):
        self.checkuser()

    def checkuser(self):
        cas_usr = self.username_cas.get()
        cas_pw = self.password_cas.get()
        cmd = 'nohup x-terminal-emulator -e '+self.project_path+'/cassandra/bin/cqlsh ' \
              + str(self.ip_addr) + ' -u ' + str(cas_usr) + ' -p ' + str(cas_pw)
        subprocess.Popen(cmd, shell=True)
        self.login_window.withdraw()

    # Frame3 functions
    def updateonoroff(self):
        self.do_update = self.auto.get()
        self.update()

    def update(self):
        if self.do_update == True:
            #print('test')
            self.sys_monitor()
            root.after(1000, self.update)

    def sys_monitor(self):
        cmd = ['top -b -n 2']
        result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()[0]
        reg = 'load average: (.*?)\nTasks:.*?Cpu\(s\): (.*?)us, (.*?)sy,.*?ni, ' \
              '(.*?)id.*?Mem : (.*?) total,.*?free,  (.*?) used'
        pattern = re.compile(reg, re.S)
        data = re.findall(pattern, result)
        if len(data) == 2:
            idx = 1
        else:
            idx = 0
        self.var_LA.set(data[idx][0])
        self.var_UU.set(data[idx][1])
        self.var_SU.set(data[idx][2])
        self.var_IDLE.set(data[idx][3])
        self.var_MT.set(data[idx][4])
        self.var_MF.set(data[idx][5])

def main():
    global root
    root = Tkinter.Tk()
    root.geometry('380x380+500+100')
    root.resizable(True, True)
    root.minsize(width=580, height=380)
    root.title('BEMOSS (Virginia Tech)')
    app = GUI()
    root.mainloop()

if __name__ == '__main__':
    main()
