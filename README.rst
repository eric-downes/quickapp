
## Simplest QuickApp application ##

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
     
     
