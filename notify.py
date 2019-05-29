import os

def notify(mode):
    os.system('osascript -e \'display notification "Mode changed to '+mode+'." with title "Gesty"\'')