import os
import shlex
import subprocess
import sublime
import sublime_plugin

class GenerateCommand(sublime_plugin.WindowCommand):
    def __init__(self, *args, **kwargs):
        super(GenerateCommand, self).__init__(*args, **kwargs)

        settings = sublime.load_settings('fuelgenerator.sublime-settings')
        self.php_path = settings.get('php_path', 'php')

    def run(self, *args, **kwargs):
        self.command = kwargs.get('generate', None)
        self.fill_in = kwargs.get('fill_in', 'Enter the resource name')
        self.accept_fields = kwargs.get('fields', False)
        self.fields_label = kwargs.get('fields_label', 'Enter the fields')

        try:
            # The first folder needs to be the Fuel Project
            self.PROJECT_PATH = self.window.folders()[0]
            self.args = [self.php_path, os.path.join(self.PROJECT_PATH, 'oil'), 'generate %s' % self.command]

            if os.path.isfile("%s" % os.path.join(self.PROJECT_PATH, 'oil')):
                if self.command in ['model', 'config', 'controller', 'task', 'migration', 'scaffold']:
                    # call function to do the work
                    self.window.show_input_panel(self.fill_in, '', self.append, None, None)
                else:
                    sublime.status_message("Generator command not supported")
            else:
                sublime.status_message("oil not found")
        except IndexError:
            sublime.status_message("Please open a Fuel Project")

    def append(self, arg):
        self.args.append(arg)
        if self.accept_fields:
            self.accept_fields = False
            self.window.show_input_panel(self.fields_label, '', self.append, None, None)
        else:
            self.oil()

    def oil(self):
        self.args = ' '.join(map(str, self.args))
        if os.name == 'posix':
            self.args = shlex.split(str(self.args))
        try:
            proc = subprocess.Popen(self.args, cwd=self.PROJECT_PATH, shell=False, stdout=subprocess.PIPE)
            self.proc(proc)
        except IOError:
            sublime.status_message('IOError - command aborted')

    def proc(self, proc):
        if proc.poll() is None:
            sublime.set_timeout(lambda: self.ran(proc), 200)
        else:
            output = proc.communicate()[0].decode('utf-8')
            if output:
                sublime.status_message("%s generated successfully" % self.command)
            else:
                sublime.status_message("%s generation failed" % self.command)

class OilCommand(sublime_plugin.WindowCommand):
    def __init__(self, *args, **kwargs):
        super(OilCommand, self).__init__(*args, **kwargs)

        settings = sublime.load_settings('fuelgenerator.sublime-settings')
        self.php_path = settings.get('php_path', 'php')

    def run(self, *args, **kwargs):
        try:
            # The first folder needs to be the Fuel Project
            self.PROJECT_PATH = self.window.folders()[0]

            if os.path.isfile("%s" % os.path.join(self.PROJECT_PATH, 'oil')):
                self.window.show_input_panel('Enter an oil command', '', self.oil, None, None)
            else:
                sublime.status_message("Oil not found")
        except IndexError:
            sublime.status_message("Please open a Fuel Project")

    def oil(self, command):
        self.args = '%s %s %s' % (self.php_path, os.path.join(self.PROJECT_PATH, 'oil'), command)
        if os.name == 'posix':
            self.args = shlex.split(str(self.args))

        if command:
            try:
                proc = subprocess.Popen(self.args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.proc(proc, command)
            except IOError:
                sublime.status_message('IOError - command aborted')
        else:
            sublime.status_message('Command not set')

    def proc(self, proc, command):
        if proc.poll() is None:
            sublime.set_timeout(lambda: self.ran(proc), 200)
        else:
            output = proc.communicate()[0].decode('utf-8')
            if output:
                sublime.status_message("oil %s executed successfully" % command)
            else:
                sublime.status_message("oil %s execution failed" % command)
