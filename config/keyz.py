import plistlib, glob, re, sys, cStringIO as StringIO
def importOldStuff():
    iDeviceKeys = plistlib.readPlist('iDeviceKeys.plist')
    for device, data1 in iDeviceKeys.items():
        for version, data2 in data1.items():
            string = device + '_' + version
            if data2.has_key('RootFilesystem'):
                print string + '.fs: ' + data2['RootFilesystem']['RootFilesystemKey']
            for img3, data3 in data2.items():
                if not data3.has_key('IV'): continue
                print string + '.' + img3 + ': ' + data3['Key'] + ' ' + data3['IV']
            print
    for thing in glob.glob('FirmwareBundles/*/Info.plist'):
        data = plistlib.readPlistFromString(open(thing).read().replace('=1.0', '="1.0"').replace('=UTF-8', '="UTF-8"').replace(' -//Apple Computer//DTD PLIST 1.0//EN', ' "-//Apple Computer//DTD PLIST 1.0//EN"').replace(' http://www.apple.com/DTDs/PropertyList-1.0.dtd', ' "http://www.apple.com/DTDs/PropertyList-1.0.dtd"'))
        string = re.sub('_[^_]*$', '', data['Name'])
        print string + '.fs: ' + data['RootFilesystemKey']
        for img3, data3 in data['FirmwarePatches'].items():
            if not hasattr(data3, 'has_key') or not data3.has_key('IV'): continue
            print string + '.' + img3 + ': ' + data3['Key'] + ' ' + data3['IV']
        print
thingsICareAbout = {
    'applelogo': 'AppleLogo',
    'batterycharging0': 'BatteryCharging0',
    'batterycharging1': 'BatteryCharging1',
    'batteryfull': 'BatteryFull',
    'batterylow0': 'BatteryLow0',
    'batterylow1': 'BatteryLow1',
    'devicetree': 'DeviceTree',
    'glyphcharging': 'GlyphCharging',
    'glyphplugin': 'GlyphPlugin',
    'ibec': 'iBEC',
    'iboot': 'iBoot',
    'ibss': 'iBSS',
    'kernelcache': 'KernelCache',
    'llb': 'LLB',
    'recoverymode': 'RecoveryMode',
    'devicetree': 'DeviceTree',
}
def importWiki(data, string):
    # I don't know if these capitalizations mean anything, but "KernelCache" is used by the other plists and I need to pick one
    f = StringIO.StringIO(data.strip())
    def readline():
        while True:
            line = f.readline()
            if line == '': return line
            line = line.lower().replace("'''", '').replace('[[', '').replace(']]', '').strip()
            if line: return line
    while True:
        line = readline()
        if line == '': break
        if 'root filesystem' in line or 'main filesystem' in line:
            line2 = readline()
            print string + '.fs: ' + re.search('vfdecrypt( key)?:\s*([a-zA-Z0-9]*)', line2).group(2)
            continue
        for k, v in thingsICareAbout.items():
            if k in line:
                ivline = readline()
                if 'not encrypted' in ivline:
                    print string + '.' + v + ': X'
                    continue
                if 'kbag' in ivline: ivline = readline()
                keyline = readline()
                print string + '.' + v + ': ' + re.search('k(ey)?:\s*([a-zA-Z0-9]*)', keyline).group(2) + ' ' + re.search('iv:\s*([a-zA-Z0-9]*)', ivline).group(1)
                break
    print

def importGenpass(data, string):
    for line in data.split('\n'):
        line = line.lower()
        for k, v in thingsICareAbout.items():
            if k in line:
                print string + '.' + v + ': ' + re.search('-k(ey)? ([a-zA-Z0-9]*)', line).group(2) + ' ' + re.search('-iv ([a-zA-Z0-9]*)', line).group(1)

def importMultilineGenpass(data, string):
    m = None
    for line in data.split('\n'):
        line = line.lower()
        if m:
            print string + '.' + m + ': ' + re.search('-k ([a-zA-Z0-9]*)', line).group(1) + ' ' + re.search('-iv ([a-zA-Z0-9]*)', line).group(1)
            m = None
        for k, v in thingsICareAbout.items():
            if k in line:
                m = v
if __name__ == '__main__':            
    {'wiki': importWiki, 'genpass': importGenpass, 'multiline_genpass': importMultilineGenpass}[sys.argv[1]](sys.stdin.read(), sys.argv[2])
#importOldStuff()
