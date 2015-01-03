QuickApp
========

QuickApp is a library that composes the functionality of Compmake, Reprep 
in high-level constructs for extremely rapid development of scientific applications.

Simplest QuickApp application
-----------------------------

This is an example of the simplest QuickApp application.
It does not use Compmake functionality. ::


     from quickapp import QuickAppBase

     class VideoMaker(QuickAppBase):
         """ Basic example of a QuickApp (no Compmake support) """
         def define_program_options(self, params):
             params.add_int('param_name', default=1)
         
         def go(self):
             self.info('you passed: %s' % self.get_options().param_name)

     main = VideoMaker.get_sys_main()
     
     
Here's an example that uses Compmake to define jobs: ::


     #!/usr/bin/env python  
     from quickapp import QuickApp

     class AppExample(QuickApp):
         """ Simplest app example """
     
         def define_options(self, params):
             params.add_int('x', default=1)
     
         def define_jobs_context(self, context):
             options = self.get_options()
             # create a job
             context.comp(f, options.x)
     
     def f(x):
         print('x = %s' % x)        
     
     app_example_main = AppExample.get_sys_main()
     
     if __name__ == '__main__':
         app_example_main()


     
