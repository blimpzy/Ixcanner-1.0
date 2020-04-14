from distutils.core import setup

#This is a list of files to install, and where
#(relative to the 'root' dir, where setup.py is)
#You could be more specific.
files = [""]

setup(name = "Ixcanner",
    version = "100",
    description = "A minimalist program that scan things from your printer!",
    author = "Igor Pontes",
    author_email = "igoppop@gmail.com",
    url = "https://github.com/blimpzy",
    #Name the folder where your packages live:
    #(If you have other packages (dirs) or modules (py files) then
    #put them into the package directory - they will be found 
    #recursively.)
    packages = ['ixcanner10'],
    #'package' package must contain files (see list above)
    #I called the package 'package' thus cleverly confusing the whole issue...
    #This dict maps the package name =to=> directories
    #It says, package *needs* these files.
    package_data = {'ixcanner10' : files },
    #'runner' is in the root.
    scripts = ["ixcanner"],
    long_description = """A program containing a very simple GUI so people can scan things in a easier and faster(hopefully) way. Made for noob linux users (like my father :D). THIS THING USES 'scanimage' TERMINAL COMMAND""" 
    #
    #This next part it for the Cheese Shop, look a little down the page.
    #classifiers = []     
) 