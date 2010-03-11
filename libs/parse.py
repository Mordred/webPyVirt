# -*- coding: UTF-8 -*-

import libxml2

from webPyVirt.domains.models   import *

class ParseException(Exception):
    pass
#endclass

# ----------------------------------------------------------------

def parseDomainXML(xml):

    doc = libxml2.parseDoc(xml)

    root = doc.children

    if root.name.lower() != "domain":
        raise ParseException("XML not starts with `domain` root element")
    #endif

    ctx = doc.xpathNewContext()

    domain = Domain()

    # Hypervisor type
    res = ctx.xpathEval("/domain/@type")
    if len(res): domain.hypervisor_type = res[0].content

    # Current ID
    res = ctx.xpathEval("/domain/@id")
    if len(res): domain.current_id = int(res[0].content)

    # Name
    res = ctx.xpathEval("/domain/name")
    if len(res): domain.name = res[0].content

    # UUID
    res = ctx.xpathEval("/domain/uuid")
    if len(res): domain.uuid = res[0].content

    # Description
    res = ctx.xpathEval("/domain/description")
    if len(res): domain.description = res[0].content

    # Bootloader
    res = ctx.xpathEval("/domain/bootloader")
    if len(res): domain.bootloader = res[0].content

    # Bootloader Args
    res = ctx.xpathEval("/domain/bootloader_args")
    if len(res): domain.bootloader_args = res[0].content

    # Loader
    res = ctx.xpathEval("/domain/os/loader")
    if len(res): domain.loader = res[0].content

    # OS Type
    res = ctx.xpathEval("/domain/os/type")
    if len(res): domain.os_type = res[0].content

    # OS Architecture
    res = ctx.xpathEval("/domain/os/type/@arch")
    if len(res): domain.os_architecture = res[0].content

    # OS Machine
    res = ctx.xpathEval("/domain/os/type/@machine")
    if len(res): domain.os_machine = res[0].content

    # OS Kernel
    res = ctx.xpathEval("/domain/os/kernel")
    if len(res): domain.os_kernel = res[0].content

    # OS Initrd
    res = ctx.xpathEval("/domain/os/initrd")
    if len(res): domain.os_initrd = res[0].content

    # OS Cmdline
    res = ctx.xpathEval("/domain/os/cmdline")
    if len(res): domain.os_cmdline = res[0].content

    # OS Boot
    res = ctx.xpathEval("/domain/os/boot/@dev")
    if len(res): domain.setOSBoot([ dev.content for dev in res ])

    # Memory
    res = ctx.xpathEval("/domain/memory")
    if len(res): domain.memory = int(res[0].content)

    # Current Memory
    res = ctx.xpathEval("/domain/currentMemory")
    if len(res): domain.memory_current = int(res[0].content)

    # VCPU
    res = ctx.xpathEval("/domain/vcpu")
    if len(res): domain.vcpu = int(res[0].content)

    # CPU Match
    res = ctx.xpathEval("/domain/cpu/@match")
    if len(res): domain.cpu_match = res[0].content

    # CPU Model
    res = ctx.xpathEval("/domain/cpu/model")
    if len(res): domain.cpu_model = res[0].content

    # CPU Topology
    sockets = ctx.xpathEval("/domain/cpu/topology/@sockets")
    cores = ctx.xpathEval("/domain/cpu/topology/@cores")
    threads = ctx.xpathEval("/domain/cpu/topology/@threads")
    sockets = len(sockets) and sockets[0].content or None
    cores = len(cores) and cores[0].content or None
    threads = len(threads) and threads[0].content or None
    domain.setCPUTopology(sockets, cores, threads)

    # CPU Features
    cpuFeatures = ctx.xpathEval("/domain/cpu/feature")
    features = {}
    for feature in cpuFeatures:
        name = feature.xpathEval("@name")
        policy = feature.xpathEval("@policy")

        name = len(name) and name[0].content or None
        policy = len(policy) and policy[0].content or None

        if not name or not policy: continue

        features[name] = policy
    #endfor
    domain.setCPUFeatures(features)

    # Poweroff
    res = ctx.xpathEval("/domain/on_poweroff")
    if len(res): domain.poweroff = res[0].content

    # Reboot
    res = ctx.xpathEval("/domain/on_reboot")
    if len(res): domain.reboot = res[0].content

    # Crash
    res = ctx.xpathEval("/domain/on_crash")
    if len(res): domain.crash = res[0].content

    # PAE
    res = ctx.xpathEval("/domain/features/pae")
    if len(res): domain.pae = True

    # PAE
    res = ctx.xpathEval("/domain/features/acpi")
    if len(res): domain.acpi = True

    # PAE
    res = ctx.xpathEval("/domain/features/apic")
    if len(res): domain.apic = True

    # Clock
    res = ctx.xpathEval("/domain/clock/@offset")
    if len(res): domain.clock = res[0].content

    # Emulator
    res = ctx.xpathEval("/domain/devices/emulator")
    if len(res): domain.emulator = res[0].content

    devices = {}
    res = ctx.xpathEval("/domain/devices")
    if len(res):
        devices = parseDevicesXML(unicode(res[0]))
    #endif

    ctx.xpathFreeContext()
    doc.freeDoc()

    return domain, devices
#enddef

# ----------------------------------------------------------------

def parseDevicesXML(xml):
    doc = libxml2.parseDoc(xml)

    root = doc.children

    if root.name.lower() != "devices":
        raise ParseException("XML not starts with `devices` root element")
    #endif

    ctx = doc.xpathNewContext()

    devices = {}

    # DISKs
    res = ctx.xpathEval("/devices/disk")
    disks = []
    if len(res):
        for disk in res:
            disks.append(parseDiskXML(unicode(disk)))
        #endfor
    #endif
    devices['disk'] = disks

    # HOST Devices
    res = ctx.xpathEval("/devices/hostdev")
    hostdevices = []
    if len(res):
        for hostdev in res:
            hostdevices.append(parseHostDevXML(unicode(hostdev)))
        #endfor
    #endif
    devices['hostdev'] = hostdevices

    # Network Intefaces
    res = ctx.xpathEval("/devices/interface")
    interfaces = []
    if len(res):
        for interface in res:
            interfaces.append(parseInterfaceXML(unicode(interface)))
        #endfor
    #endif
    devices['interface'] = interfaces

    # Input Devices
    res = ctx.xpathEval("/devices/input")
    inputDevices = []
    if len(res):
        for inputDevice in res:
            inputDevices.append(parseInputXML(unicode(inputDevice)))
        #endfor
    #endif
    devices['input'] = inputDevices

    # Graphics
    res = ctx.xpathEval("/devices/graphics")
    graphics = []
    if len(res):
        for graph in res:
            graphics.append(parseGraphicsXML(unicode(graph)))
        #endfor
    #endif
    devices['graphics'] = graphics

    # Video
    res = ctx.xpathEval("/devices/video")
    videos = []
    if len(res):
        for video in res:
            videos.append(parseVideoXML(unicode(video)))
        #endfor
    #endif
    devices['video'] = videos

    # Ports
    res = ctx.xpathEval("/devices/console | /devices/serial | /devices/parallel | /devices/channel")
    ports = []
    if len(res):
        for port in res:
            ports.append(parsePortXML(unicode(port)))
        #endfor
    #endif
    devices['port'] = ports

    # Sounds
    res = ctx.xpathEval("/devices/sound")
    sounds = []
    if len(res):
        for sound in res:
            sounds.append(parseSoundXML(unicode(sound)))
        #endfor
    #endif
    devices['sound'] = sounds

    # Watchdogs
    res = ctx.xpathEval("/devices/watchdog")
    watchdogs = []
    if len(res):
        for watchdog in res:
            watchdogs.append(parseWatchdogXML(unicode(watchdog)))
        #endfor
    #endif
    devices['watchdog'] = watchdogs

    ctx.xpathFreeContext()
    doc.freeDoc()

    return devices
#enddef

def parseDiskXML(xml):
    doc = libxml2.parseDoc(xml)

    root = doc.children

    if root.name.lower() != "disk":
        raise ParseException("XML not starts with `disk` root element")
    #endif

    ctx = doc.xpathNewContext()

    disk = Disk()

    # Disk Type
    res = ctx.xpathEval("/disk/@type")
    if len(res): disk.type = res[0].content

    # Device
    res = ctx.xpathEval("/disk/@device")
    if len(res): disk.device = res[0].content

    # Source
    if disk.type == "file":
        res = ctx.xpathEval("/disk/source/@file")
    elif disk.type == "block":
        res = ctx.xpathEval("/disk/source/@dev")
    else:
        res = None
    #endif
    if len(res): disk.source = res[0].content

    # Target Device
    res = ctx.xpathEval("/disk/target/@dev")
    if len(res): disk.target_dev = res[0].content

    # Target Bus
    res = ctx.xpathEval("/disk/target/@bus")
    if len(res): disk.target_bus = res[0].content

    # Driver Name
    res = ctx.xpathEval("/disk/driver/@name")
    if len(res): disk.driver_name = res[0].content

    # Driver Type
    res = ctx.xpathEval("/disk/driver/@type")
    if len(res): disk.driver_type = res[0].content

    # Driver Cache
    res = ctx.xpathEval("/disk/driver/@cache")
    if len(res): disk.driver_cache = res[0].content

    # Encryption Format
    res = ctx.xpathEval("/disk/encryption/@format")
    if len(res): disk.encrypt_format = res[0].content

    # Encryption Secret
    res = ctx.xpathEval("/disk/encryption/secret/@uuid")
    if len(res): disk.encrypt_secret = res[0].content

    # Shareable
    res = ctx.xpathEval("/disk/shareable")
    if len(res): disk.shareable = True

    ctx.xpathFreeContext()
    doc.freeDoc()

    return disk
#enddef

def parseHostDevXML(xml):
    doc = libxml2.parseDoc(xml)

    root = doc.children

    if root.name.lower() != "hostdev":
        raise ParseException("XML not starts with `hostdev` root element")
    #endif

    ctx = doc.xpathNewContext()

    hostdev = HostDevice()

    # Type
    res = ctx.xpathEval("/hostdev/@type")
    if len(res): hostdev.type = res[0].content

    # Source Vendor
    res = ctx.xpathEval("/hostdev/source/vendor/@id")
    if len(res): hostdev.vendor = res[0].content

    # Source Product
    res = ctx.xpathEval("/hostdev/source/product/@id")
    if len(res): hostdev.product = res[0].content

    # Address Bus
    res = ctx.xpathEval("/hostdev/source/address/@bus")
    if len(res): hostdev.address_bus = int(res[0].content)

    # Address Device
    res = ctx.xpathEval("/hostdev/source/address/@device")
    if len(res): hostdev.address_device = int(res[0].content)

    # Address Slot
    res = ctx.xpathEval("/hostdev/source/address/@slot")
    if len(res): hostdev.address_slot = int(res[0].content)

    # Address Function
    res = ctx.xpathEval("/hostdev/source/address/@function")
    if len(res): hostdev.address_function = int(res[0].content)

    ctx.xpathFreeContext()
    doc.freeDoc()

    return hostdev
#enddef

def parseInterfaceXML(xml):
    doc = libxml2.parseDoc(xml)

    root = doc.children

    if root.name.lower() != "interface":
        raise ParseException("XML not starts with `interface` root element")
    #endif

    ctx = doc.xpathNewContext()

    interface = Interface()

    # Type
    res = ctx.xpathEval("/interface/@type")
    if len(res): interface.type = res[0].content

    # Model
    res = ctx.xpathEval("/interface/model/@type")
    if len(res): interface.model = res[0].content

    # MAC Address
    res = ctx.xpathEval("/interface/mac/@address")
    if len(res): interface.mac_address = res[0].content

    # Source Bridge
    res = ctx.xpathEval("/interface/source/@bridge")
    if len(res): interface.source_bridge = res[0].content

    # Source Network
    res = ctx.xpathEval("/interface/source/@network")
    if len(res): interface.source_network = res[0].content

    # Source Device
    res = ctx.xpathEval("/interface/source/@dev")
    if len(res): interface.source_dev = res[0].content

    # Source Mode
    res = ctx.xpathEval("/interface/source/@mode")
    if len(res): interface.source_mode = res[0].content

    # Source Address
    res = ctx.xpathEval("/interface/source/@address")
    if len(res): interface.source_address = res[0].content

    # Source Port
    res = ctx.xpathEval("/interface/source/@port")
    if len(res): interface.source_port = int(res[0].content)

    # Target Device
    res = ctx.xpathEval("/interface/target/@dev")
    if len(res): interface.target_dev = res[0].content

    # Script
    res = ctx.xpathEval("/interface/script/@path")
    if len(res): interface.script = res[0].content

    ctx.xpathFreeContext()
    doc.freeDoc()

    return interface
#enddef

def parseInputXML(xml):
    doc = libxml2.parseDoc(xml)

    root = doc.children

    if root.name.lower() != "input":
        raise ParseException("XML not starts with `input` root element")
    #endif

    ctx = doc.xpathNewContext()

    inputDevice = InputDevice()

    # Type
    res = ctx.xpathEval("/input/@type")
    if len(res): inputDevice.type = res[0].content

    # Bus
    res = ctx.xpathEval("/input/@bus")
    if len(res): inputDevice.bus = res[0].content

    ctx.xpathFreeContext()
    doc.freeDoc()

    return inputDevice
#enddef

def parseGraphicsXML(xml):
    doc = libxml2.parseDoc(xml)

    root = doc.children

    if root.name.lower() != "graphics":
        raise ParseException("XML not starts with `graphics` root element")
    #endif

    ctx = doc.xpathNewContext()

    graphics = Graphics()

    # Type
    res = ctx.xpathEval("/graphics/@type")
    if len(res): graphics.type = res[0].content

    # Display
    res = ctx.xpathEval("/graphics/@display")
    if len(res): graphics.display = res[0].content

    # Display
    res = ctx.xpathEval("/graphics/@fullscreen")
    if len(res): graphics.fullscreen = bool(res[0].content.lower() == "yes")

    # XAuth
    res = ctx.xpathEval("/graphics/@xauth")
    if len(res): graphics.xauth = res[0].content

    # Port
    res = ctx.xpathEval("/graphics/@port")
    if len(res): graphics.port = int(res[0].content)

    # Autoport
    res = ctx.xpathEval("/graphics/@autoport")
    if len(res): graphics.autoport = bool(res[0].content.lower() == "yes")

    # Listen
    res = ctx.xpathEval("/graphics/@listen")
    if len(res): graphics.listen = res[0].content

    # Password
    res = ctx.xpathEval("/graphics/@passwd")
    if len(res): graphics.password = res[0].content

    # Keymap
    res = ctx.xpathEval("/graphics/@keymap")
    if len(res): graphics.keymap = res[0].content

    # Multi user
    res = ctx.xpathEval("/graphics/@multiUser")
    if len(res): graphics.multi_user = bool(res[0].content.lower() == "yes")

    # Replace user
    res = ctx.xpathEval("/graphics/@replaceUser")
    if len(res): graphics.replace_user = bool(res[0].content.lower() == "yes")

    ctx.xpathFreeContext()
    doc.freeDoc()

    return graphics
#enddef

def parseVideoXML(xml):
    doc = libxml2.parseDoc(xml)

    root = doc.children

    if root.name.lower() != "video":
        raise ParseException("XML not starts with `video` root element")
    #endif

    ctx = doc.xpathNewContext()

    video = Video()

    # Type
    res = ctx.xpathEval("/video/model/@type")
    if len(res): video.type = res[0].content

    # vRAM
    res = ctx.xpathEval("/video/model/@vram")
    if len(res): video.vram = int(res[0].content)

    # Heads
    res = ctx.xpathEval("/video/model/@heads")
    if len(res): video.heads = int(res[0].content)

    # 3D Acceleration
    res = ctx.xpathEval("/video/model/acceleration/@accel3d")
    if len(res): video.acceleration_3d = bool(res[0].content.lower() == "yes")

    # 2D Acceleration
    res = ctx.xpathEval("/video/model/acceleration/@accel2d")
    if len(res): video.acceleration_2d = bool(res[0].content.lower() == "yes")

    ctx.xpathFreeContext()
    doc.freeDoc()

    return video
#enddef

def parsePortXML(xml):
    doc = libxml2.parseDoc(xml)

    root = doc.children

    allowed = [ "console", "parallel", "serial", "channel" ]
    if not root.name.lower() in allowed:
        raise ParseException("XML not starts with %s root element" % \
            (" or ".join(map(lambda x: "`" + x + "`", allowed))))
    #endif

    ctx = doc.xpathNewContext()

    port = Port()
    port.port_type = root.name.lower()

    # Type
    res = ctx.xpathEval("/%s/@type" % (root.name))
    if len(res): port.type = res[0].content

    # Source Path
    res = ctx.xpathEval("/%s/source/@path" % (root.name))
    if len(res): port.source_path = res[0].content

    # Source Mode
    res = ctx.xpathEval("/%s/source/@mode" % (root.name))
    if len(res): port.source_mode = res[0].content

    # Target Port
    res = ctx.xpathEval("/%s/target/@port" % (root.name))
    if len(res): port.target_port = int(res[0].content)

    # Target Type
    res = ctx.xpathEval("/%s/target/@type" % (root.name))
    if len(res): port.target_type = res[0].content

    # Target Address
    res = ctx.xpathEval("/%s/source/@address" % (root.name))
    if len(res): port.target_address = res[0].content

    # Protocol
    res = ctx.xpathEval("/%s/protocol/@type" % (root.name))
    if len(res): port.protocol = res[0].content

    ctx.xpathFreeContext()
    doc.freeDoc()

    return port
#enddef

def parseSoundXML(xml):
    doc = libxml2.parseDoc(xml)

    root = doc.children

    if root.name.lower() != "sound":
        raise ParseException("XML not starts with `sound` root element")
    #endif

    ctx = doc.xpathNewContext()

    sound = Sound()

    # Model
    res = ctx.xpathEval("/sound/@model")
    if len(res): sound.model = res[0].content

    ctx.xpathFreeContext()
    doc.freeDoc()

    return sound
#enddef

def parseWatchdogXML(xml):
    doc = libxml2.parseDoc(xml)

    root = doc.children

    if root.name.lower() != "watchdog":
        raise ParseException("XML not starts with `watchdog` root element")
    #endif

    ctx = doc.xpathNewContext()

    watchdog = Watchdog()

    # Model
    res = ctx.xpathEval("/watchdog/@model")
    if len(res): watchdog.model = res[0].content

    # Action
    res = ctx.xpathEval("/watchdog/@action")
    if len(res): watchdog.action = res[0].content

    ctx.xpathFreeContext()
    doc.freeDoc()

    return watchdog
#enddef
