import imp
import webiopi.utils.logger as logger
import webiopi.utils.thread as thread
SCRIPTS = {}

def loadScript(name, source, handler = None):
    logger.info("Loading %s from %s" % (name, source))
    script = imp.load_source(name, source)
    SCRIPTS[name] = script

    if hasattr(script, "setup"):
        script.setup()
    if handler:
        for aname in dir(script):
            attr = getattr(script, aname)
            if callable(attr) and hasattr(attr, "macro"):
                handler.addMacro(attr)
    if hasattr(script, "loop"):
        thread.runLoop(script.loop, True)

def unloadScripts():
    for name in SCRIPTS:
        script = SCRIPTS[name]
        if hasattr(script, "destroy"):
            script.destroy()
    