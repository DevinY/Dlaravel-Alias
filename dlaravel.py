import sublime, sublime_plugin, re
from subprocess import Popen, PIPE, STDOUT
from threading import Thread

class PhpArtisanCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        self.window = self.view.window()
        self.args = args
        #len(self.window.folders())
        #=====Check Project Folder===========
        try:
            file = self.window.extract_variables()['file']
            dlaravel_folder = re.sub("^(.+?)(/sites/)(.+?)/(.+?)$", "\\1", file)
            project_folder = re.sub("^(.+?)(/sites/)(.+?)/(.+?)$", "\\3", file)
            folder = "{}/sites/{}".format(dlaravel_folder, project_folder)
        except:
            folder = self.window.extract_variables()['folder']


        
        dlaravel_folder = re.sub("^(.+?)(/sites/)(.+?)$", "\\1", folder)

        try:
            dlaravel_release = open("{}/etc/dlaravel-release".format(dlaravel_folder),"r").read()
            print("Project Folder: {}".format(folder))
            print(dlaravel_release)
        except:
            print("Unable to find D-Laravel folder.")
            print("You can download it at https://github.com/DevinY/dlaravel.")
            self.window.run_command("show_panel", {"panel": "console", "toggle": True})
            self.view.set_status("Dlaravel","Unable to find D-Laravel")
            return False

        self.view.set_status("Dlaravel", "artisan command will be run in {}".format(folder))
        project_folder = re.sub("^(.+?)(/sites/)(.+?)$", "\\3", folder)
        #===============================

        def auto_complete_level2(*args):
            if("route:l\t" in list(args) or "route:li\t" in list(args)):
                self.window.show_input_panel("{} php artisan".format(project_folder),"route:list", on_done, None, None)
            if("migrate:refresh\t" in list(args)):
                self.window.show_input_panel("{} php artisan".format(project_folder),"migrate:refresh", on_done, None, None)

        def auto_complete(*args):
            #print(args)
            if("mi\t" in list(args)):
                self.window.show_input_panel("php artisan","migrate", on_done, auto_complete_level2, None)
            if("ro\t" in list(args)):
                self.window.show_input_panel("php artisan","route:", on_done, auto_complete_level2, None)
            if("vi\t" in list(args)):
                self.window.show_input_panel("php artisan","view", on_done, auto_complete_level2, None)
            if("view:c\t" in list(args)):
                self.window.show_input_panel("php artisan","view:clear", on_done, auto_complete_level2, None)

        def run_command(*args):
            dlaravel_project = re.sub(".*sites/(.+$)", "\\1", folder)
            dlaravel_basepath = re.sub("(^.*)/sites/(.+$)", "\\1", folder)

            parameter=""
            for arg in list(args):
                parameter=parameter+" {}".format(arg)
            print('Command is issued (php artisan{}), Please wait...'.format(parameter))
            command=["docker-compose","-f","{}/docker-compose.yml".format(dlaravel_basepath),"exec","-w","/var/www/html/{}".format(dlaravel_project),"-u","dlaravel","-T","php","php","artisan"]+list(args)
            proc=Popen(command ,bufsize=0, stdout=PIPE,stderr=PIPE, universal_newlines=True);
            output, error = proc.communicate()
            proc.wait()
            exit_code=proc.poll()
            if(exit_code==0):
                self.view.set_status("Dlaravel","composer{} is done.".format(parameter))
                print(output)
                print("Finished.")
            else:
                print("faild:{}".format(error))

        def on_done( command ):
            self.window.run_command("show_panel", {"panel": "console", "toggle": True})
            this_thread = Thread(target=run_command, args=command.split())
            this_thread.start()

        self.window.show_input_panel("({}) php artisan".format(project_folder),"", on_done, auto_complete, None)

class PhpArtisanMigrateCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        args="migrate"
        self.window = self.view.window()

        def run_command(*args):
            args=list(args)
            folder = self.window.extract_variables()['folder']
            dlaravel_project = re.sub(".*sites/(.+$)", "\\1", folder)
            dlaravel_basepath = re.sub("(^.*)/sites/(.+$)", "\\1", folder)
            print('Command is issued (composer '+' '.join(args)+'), Please wait...')
            command=["docker-compose","-f","{}/docker-compose.yml".format(dlaravel_basepath),"exec","-w","/var/www/html/{}".format(dlaravel_project),"-u","dlaravel","-T","php","php","artisan","migrate"]
            proc=Popen(command ,bufsize=0, stdout=PIPE,stderr=PIPE, universal_newlines=True);
            output, error = proc.communicate()
            proc.wait()
            exit_code=proc.poll()
            if(exit_code==0):
                self.view.set_status("Dlaravel","composer {} is done.".format(' '.join(args)))
                print(output)
                print("Finished.")
            else:
                print("{}".format(error))

        self.window.run_command("show_panel", {"panel": "console", "toggle": True})
        this_thread = Thread(target=run_command, args=args.split())
        this_thread.start()

class DockerComposeCommand(sublime_plugin.TextCommand):

    def run(self, edit, **args):

        self.window = self.view.window()
        folder = self.window.extract_variables()['folder']

        def run_command(*args):
            dlaravel_project = re.sub(".*sites/(.+$)", "\\1", folder)
            dlaravel_basepath = re.sub("(^.*)/sites/(.+$)", "\\1", folder)
            print("Command is issued (composer {})".format(' '.join(list(args))))
            #print(type(args))
            parameter=list(args)
            if("exec" in args):
               parameter=["exec","-T"]+parameter[1:]

            if("up" in args):
                parameter=parameter+["-d"]
            
            command=["docker-compose","--no-ansi","-f","{}/docker-compose.yml".format(dlaravel_basepath)]+parameter
            proc=Popen(command ,bufsize=0, stdout=PIPE,stderr=PIPE, universal_newlines=True);
            output, error = proc.communicate()
            proc.wait()
            if(proc.poll()==0):
                self.view.set_status("Dlaravel", "Success" % command)
                print(output)
                self.window.run_command("show_panel", {"panel": "console", "toggle": True})
            else:
                self.view.set_status("Dlaravel", "Error" % command)
                print(error)
                self.window.run_command("show_panel", {"panel": "console", "toggle": True})

        def on_done( command ):
            this_thread = Thread(target=run_command, args=command.split())
            this_thread.start()

        if args:
            run_command(*args['parameters'])
        else:
            self.window.show_input_panel("docker-compose", "", on_done, None, None)

class ComposerCommand(sublime_plugin.TextCommand):

    def run(self, edit, *args):
        #print(self.window)
        self.args = args
        self.window = self.view.window()

        #=====Check Project Folder===========
        try:
            file = self.window.extract_variables()['file']
            dlaravel_folder = re.sub("^(.+?)(/sites/)(.+?)/(.+?)$", "\\1", file)
            project_folder = re.sub("^(.+?)(/sites/)(.+?)/(.+?)$", "\\3", file)
            folder = "{}/sites/{}".format(dlaravel_folder, project_folder)
        except:
            folder = self.window.extract_variables()['folder']


        
        dlaravel_folder = re.sub("^(.+?)(/sites/)(.+?)$", "\\1", folder)

        try:
            dlaravel_release = open("{}/etc/dlaravel-release".format(dlaravel_folder),"r").read()
            print("Project Folder: {}".format(folder))
            print(dlaravel_release)
        except:
            print("Unable to find D-Laravel folder.")
            print("You can download it at https://github.com/DevinY/dlaravel.")
            self.window.run_command("show_panel", {"panel": "console", "toggle": True})
            self.view.set_status("Dlaravel","Unable to find D-Laravel")
            return False

        self.view.set_status("Dlaravel", "artisan command will be run in {}".format(folder))
        project_folder = re.sub("^(.+?)(/sites/)(.+?)$", "\\3", folder)
        #===============================

        def run_command(*args):
            dlaravel_project = re.sub(".*sites/(.+$)", "\\1", folder)
            dlaravel_basepath = re.sub("(^.*)/sites/(.+$)", "\\1", folder)
            args=list(args)
            if "composer" in args:
                del args[0]
            #print(args)
            self.window.run_command("show_panel", {"panel": "console", "toggle": True})
            msg='Command is issued (composer {}), Please wait...'.format(' '.join(list(args)))
            print(msg)
            self.view.set_status("Dlaravel", msg)
            command=["docker-compose","-f","{}/docker-compose.yml".format(dlaravel_basepath),"exec","-w","/var/www/html/{}".format(dlaravel_project),"-u","dlaravel","-T","php","composer"]+args
            proc=Popen(command ,bufsize=0, stdout=PIPE,stderr=PIPE, universal_newlines=True);
            output, error = proc.communicate()
            proc.wait()
            self.window.run_command("show_panel", {"panel": "console"})
            if(proc.poll()==0):
                self.view.set_status("Dlaravel","composer {} is done.".format(' '.join(args)))
                print(output)
                self.window.run_command("hide_panel", {"panel": "console"})
            else:
                self.window.set_status("Dlaravel", "Error" % command)
                print(error)

        def on_done( command ):
            args = command.split()
            this_thread = Thread(target=run_command, args=args)
            this_thread.start()

        #self.view.window().run_command("hide_panel", {"panel": "console"})
        self.window.show_input_panel("({}) composer".format(project_folder), "", on_done, None, None)

class ConsoleUpCommand(sublime_plugin.TextCommand):

     def run(self, edit):
        def run_command(*args):
            folder = self.window.extract_variables()['folder']
            arg = "up -d --remove-orphans".split()
            dlaravel_project = re.sub(".*sites/(.+$)", "\\1", folder)
            dlaravel_basepath = re.sub("(^.*)/sites/(.+$)", "\\1", folder)
            command=["docker-compose","-f","{}/docker-compose.yml".format(dlaravel_basepath)]+arg
            print(command)
            proc=Popen(command ,bufsize=1, stdout=PIPE,stderr=PIPE, universal_newlines=True);
            output, error = proc.communicate()
            proc.wait()
            if(proc.poll()==0):
                self.view.set_status("Dlaravel", "console up success" % command)
                arg = "ps".split()
                command=["docker-compose","-f","{}/docker-compose.yml".format(dlaravel_basepath)]+arg
                proc=Popen(command ,bufsize=1, stdout=PIPE,stderr=PIPE, universal_newlines=True);
                output = proc.communicate()[0]
                print(output)
                self.window.run_command("show_panel", {"panel": "console", "toggle": True})
            else:
                self.view.set_status("Dlaravel", "Error" % command)
                print(error)
                self.window.run_command("show_panel", {"panel": "console", "toggle": True})
        self.window = self.view.window() 
        this_thread = Thread(target=run_command)
        this_thread.start()

class ConsoleDownCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.window = self.view.window() 
        def run_command():
            folder = self.window.extract_variables()['folder']
            arg = "down".split()
            dlaravel_project = re.sub(".*sites/(.+$)", "\\1", folder)
            dlaravel_basepath = re.sub("(^.*)/sites/(.+$)", "\\1", folder)
            command=["docker-compose","--no-ansi","-f","{}/docker-compose.yml".format(dlaravel_basepath)]+arg
            proc=Popen(command ,bufsize=1, stdout=PIPE,stderr=PIPE, universal_newlines=True);
            output, error = proc.communicate()
            proc.wait()
            print(error)
            if(proc.poll()==0):
                self.view.set_status("Dlaravel", "console down Success" % command)
                arg = "ps".split()
                command=["docker-compose","-f","{}/docker-compose.yml".format(dlaravel_basepath)]+arg
                proc=Popen(command ,bufsize=1, stdout=PIPE,stderr=PIPE, universal_newlines=True);
                output = proc.communicate()[0]
                print(output)
                self.window.run_command("show_panel", {"panel": "console", "toggle": True})
            else:
                self.view.set_status("Dlaravel", "Error" % command)
                print(error)
                self.window.run_command("show_panel", {"panel": "console", "toggle": True})
        self.window = self.view.window() 
        this_thread = Thread(target=run_command)
        this_thread.start()