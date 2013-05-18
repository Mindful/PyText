from cx_Freeze import setup, Executable
 
exe = Executable(
    script="PyText.pyw",
    base="Win32GUI",
    )
 
setup(
    name = "PyText",
    version = "0.1",
    description = "A Python program that wraps email to text portals. See: https://github.com/Mindful/PyText",
    executables = [exe]
    )