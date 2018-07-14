import sublime, sublime_plugin, time, re
from subprocess import Popen, PIPE, STDOUT, check_output,check_call, call
from threading import Thread
import os, sys

class DlaravelCommand(sublime_plugin.TextCommand):
     def run(self, edit):
         path = self.view.window().folders()[0]
         print("console up:{}".format(path))

class PhpArtisanCommand(sublime_plugin.TextCommand):
    initial_text=""
    def run(self, edit, **args):
        self.args = args
        folder = self.view.window().extract_variables()['folder']
        def auto_complete_level2(*args):
            if("route:l\t" in list(args) or "route:li\t" in list(args)):
                sublime.active_window().show_input_panel("php artisan","route:list", on_done, None, None)
            if("migrate:refresh\t" in list(args)):
                sublime.active_window().show_input_panel("php artisan","migrate:refresh", on_done, None, None)

        def auto_complete(*args):
            #print(args)
            if("mi\t" in list(args)):
                sublime.active_window().show_input_panel("php artisan","migrate", on_done, auto_complete_level2, None)
            if("ro\t" in list(args)):
                sublime.active_window().show_input_panel("php artisan","route:", on_done, auto_complete_level2, None)
            if("vi\t" in list(args)):
                sublime.active_window().show_input_panel("php artisan","view", on_done, auto_complete_level2, None)
            if("view:c\t" in list(args)):
                sublime.active_window().show_input_panel("php artisan","view:clear", on_done, auto_complete_level2, None)

        def run_command(*args):
            dlaravel_project = re.sub(".*sites/(.+$)", "\\1", folder)
            dlaravel_basepath = re.sub("(^.*)/sites/(.+$)", "\\1", folder)
            print('Command is issued (php artisan '+''.join(list(args))+'), Please wait...')
            command=["docker-compose","-f","{}/docker-compose.yml".format(dlaravel_basepath),"exec","-w","/var/www/html/{}".format(dlaravel_project),"-u","dlaravel","-T","php","php","artisan"]+list(args)
            proc=Popen(command ,bufsize=0, stdout=PIPE,stderr=PIPE, universal_newlines=True);
            output, error = proc.communicate()
            proc.wait()
            exit_code=proc.poll()
            if(exit_code==0):
                print(output)
                self.view.set_status("Dlaravel", "Done")
            else:
                print("faild:{}".format(error))

        def on_done( command ):
            sublime.active_window().run_command("show_panel", {"panel": "console", "toggle": True})
            this_thread = Thread(target=run_command, args=command.split())
            this_thread.start()

        sublime.active_window().show_input_panel("php artisan","", on_done, auto_complete, None)

class PhpArtisanMigrateCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        args="migrate"
        def run_command(*args):
            dlaravel_project = re.sub(".*sites/(.+$)", "\\1", folder)
            dlaravel_basepath = re.sub("(^.*)/sites/(.+$)", "\\1", folder)
            print('Command is issued (composer '+''.join(list(args))+'), Please wait...')
            command=["docker-compose","-f","{}/docker-compose.yml".format(dlaravel_basepath),"exec","-w","/var/www/html/{}".format(dlaravel_project),"-u","dlaravel","-T","php","php","artisan","migrate"]
            proc=Popen(command ,bufsize=0, stdout=PIPE,stderr=PIPE, universal_newlines=True);
            while 1:
                print(proc.stdout.readline()[:-1])
                if proc.stdout.readline()[:-1]=='':
                    break
        folder = self.view.window().extract_variables()['folder']
        sublime.active_window().run_command("show_panel", {"panel": "console", "toggle": True})
        this_thread = Thread(target=run_command, args=args.split())
        this_thread.start()

class ConsoleCommand(sublime_plugin.TextCommand):

    def run(self, edit, **args):
        self.args = args
        folder = self.view.window().extract_variables()['folder']

        def run_command(*args):
            dlaravel_project = re.sub(".*sites/(.+$)", "\\1", folder)
            dlaravel_basepath = re.sub("(^.*)/sites/(.+$)", "\\1", folder)
            print("composer {}".format(list(args)))
            #print(type(args))
            parameter=list(args)
            if("up" in args):
                parameter=parameter+["-d"]
            
            command=["docker-compose","--no-ansi","-f","{}/docker-compose.yml".format(dlaravel_basepath)]+parameter
            proc=Popen(command ,bufsize=0, stdout=PIPE,stderr=PIPE, universal_newlines=True);
            output, error = proc.communicate()
            proc.wait()
            if(proc.poll()==0):
                self.view.set_status("Dlaravel", "Success" % command)
            else:
                self.view.set_status("Dlaravel", "Error" % command)
                print(error)
                sublime.active_window().run_command("show_panel", {"panel": "console", "toggle": True})

        def on_done( command ):
            this_thread = Thread(target=run_command, args=command.split())
            this_thread.start()

        sublime.active_window().show_input_panel("console", "", on_done, None, None)

class ComposerCommand(sublime_plugin.TextCommand):

    def run(self, edit, **args):
        self.args = args
        folder = self.view.window().extract_variables()['folder']

        def run_command(*args):
            dlaravel_project = re.sub(".*sites/(.+$)", "\\1", folder)
            dlaravel_basepath = re.sub("(^.*)/sites/(.+$)", "\\1", folder)
            print('Command is issued (composer '+''.join(list(args))+'), Please wait...')
            command=["docker-compose","-f","{}/docker-compose.yml".format(dlaravel_basepath),"exec","-w","/var/www/html/{}".format(dlaravel_project),"-u","dlaravel","-T","php","composer"]+list(args)
            proc=Popen(command ,bufsize=0, stdout=PIPE,stderr=PIPE, universal_newlines=True);
            while 1:
                print(proc.stdout.readline()[:-1])
                if proc.stdout.readline()[:-1]=='':
                    break

        def on_done( command ):
            sublime.active_window().run_command("show_panel", {"panel": "console", "toggle": True})
            this_thread = Thread(target=run_command, args=command.split())
            this_thread.start()

        sublime.active_window().show_input_panel("composer", "", on_done, None, None)

class ConsoleUpCommand(sublime_plugin.TextCommand):
     def run(self, edit):
         folder = self.view.window().extract_variables()['folder']
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
         else:
             self.view.set_status("Dlaravel", "Error" % command)
             print(error)
             sublime.active_window().run_command("show_panel", {"panel": "console", "toggle": True})



class ConsoleDownCommand(sublime_plugin.TextCommand):
     def run(self, edit):
         folder = self.view.window().extract_variables()['folder']
         arg = "down".split()
         dlaravel_project = re.sub(".*sites/(.+$)", "\\1", folder)
         dlaravel_basepath = re.sub("(^.*)/sites/(.+$)", "\\1", folder)
         command=["docker-compose","-f","{}/docker-compose.yml".format(dlaravel_basepath)]+arg
         proc=Popen(command ,bufsize=1, stdout=PIPE,stderr=PIPE, universal_newlines=True);
         output, error = proc.communicate()
         proc.wait()
         if(proc.poll()==0):
             self.view.set_status("Dlaravel", "console down Success" % command)
         else:
             self.view.set_status("Dlaravel", "Error" % command)
             print(error)
             sublime.active_window().run_command("show_panel", {"panel": "console", "toggle": True})

class ConsolePsCommand(sublime_plugin.TextCommand):
     def run(self, edit):
         folder = self.view.window().extract_variables()['folder']
         arg = "ps".split()
         dlaravel_project = re.sub(".*sites/(.+$)", "\\1", folder)
         dlaravel_basepath = re.sub("(^.*)/sites/(.+$)", "\\1", folder)
         command=["docker-compose","-f","{}/docker-compose.yml".format(dlaravel_basepath)]+arg
         proc=Popen(command ,bufsize=1, stdout=PIPE,stderr=PIPE, universal_newlines=True);
         output, error = proc.communicate()
         proc.wait()
         if(proc.poll()==0):
             print(output)
             self.view.set_status("Dlaravel", "Success" % command)
             sublime.active_window().run_command("show_panel", {"panel": "console", "toggle": True})
         else:
             self.view.set_status("Dlaravel", "Error" % command)
             print(error)
             sublime.active_window().run_command("show_panel", {"panel": "console", "toggle": True})

class CreateDbCommand(sublime_plugin.TextCommand):
     def run(self, edit):
        self.view.set_status("Dlaravel", "This feature is not implemented.")

class CreateHostCommand(sublime_plugin.TextCommand):
     def run(self, edit):
        self.view.set_status("Dlaravel", "This feature is not implemented.")
