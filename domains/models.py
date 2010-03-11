# -*- coding: UTF-8 -*-

from django.db                      import models
from django.contrib.auth.models     import User, Group
from django.utils.translation       import ugettext_lazy as _

from webPyVirt.nodes.models         import Node

class Domain(models.Model):
    OS_TYPES = (
        (u"hvm", _("Hardware Virtual Machine (Fully Virtualized)")),
        (u"linux", _("Xen PV (Paravirtualized)")),
        (u"qemu", _("QEMU / KVM PV (Paravirtualized)"))
    )

    BOOT_DEVICES = [ "fd", "hd", "cdrom", "network" ]

    LIFECYCLES = (
        (u"destroy", _("Destroy")),
        (u"restart", _("Restart")),
        (u"preserve", _("Preserve")),
        (u"rename-restart", _("Rename-Restart")),
    )

    CPU_MATCHES = (
        (u"minimum", _("Minimum match")),
        (u"exact", _("Exact match")),
        (u"strict", _("Strict match")),
    )

    CPU_FEATURES = [
        "fpu", "vme", "de", "pse", "tsc", "msr", "pae", "mce", "cx8",
        "apic", "sep", "mtrr", "pge", "mca", "cmov", "pat", "pse36",
        "pn", "clflush", "ds", "acpi", "mmx", "fxsr", "sse", "sse2",
        "ss", "ht", "tm", "ia64", "pbe", "pni", "monitor",
        "ds_cpl", "vmx", "est", "tm2", "ssse3", "cid", "cx16",
        "xtpr", "dca", "x2apic", "popcnt", "hypervisor",
        "syscall", "nx", "mmext", "fxsr_opt", "pdpe1gb", "rdtscp",
        "lm", "3dnowext", "3dnow", "lahf_lm", "cmp_legacy",
        "svm", "extapic", "cr8legacy", "abm", "sse4a", "misalignsse",
        "3dnowprefetch", "osvw", "skinit", "wdt"
    ]

    CPU_FEATURE_POLICIES = [ "force", "require", "optional", "disable", "forbid" ]

    CLOCK_OFFSETS = (
        (u"utc", _("UTC")),
        (u"localtime", _("Localtime")),
        (u"timezone", _("Timezone")),
    )

    node = models.ForeignKey(Node)
    owner = models.ForeignKey(User)

    # Metadata
    current_id = models.IntegerField(default = -1,
        verbose_name = _("Current ID on node"))
    hypervisor_type = models.CharField(max_length = 6, choices = Node.DRIVERS,
        verbose_name = _("Hypervisor Driver Type"))
    name = models.CharField(max_length = 255, verbose_name = _("Domain Name"))
    uuid = models.CharField(max_length = 40, verbose_name = _("UUID"), unique = True)
    description = models.TextField(verbose_name = _("Description"),
        help_text = _("Human readable description of the virtual machine"),
        blank = True, null = True)

    # Bootloader
    bootloader = models.CharField(max_length = 255, null = True, blank = True,
        verbose_name = _("Bootloader"))
    bootloader_args = models.CharField(max_length = 255, null = True, blank = True,
        verbose_name = _("Bootloader Args"))

    # OS
    os_type = models.CharField(max_length = 5, null = True, blank = True,
        choices = OS_TYPES, verbose_name = _("Type of virtualization"))
    loader = models.CharField(max_length = 255, null = True, blank = True,
        verbose_name = _("Firmware blob which assist the domain creation process"))
    os_architecture = models.CharField(max_length = 10, null = True, blank = True,
        verbose_name = _("CPU architecture"))
    os_machine = models.CharField(max_length = 10, null = True, blank = True,
        verbose_name = _("Machine Type"))
    os_kernel = models.CharField(max_length = 255, null = True, blank = True,
        verbose_name = _("Path to kernel image in the host OS"))
    os_initrd = models.CharField(max_length = 255, null = True, blank = True,
        verbose_name = _("Path to (optional) ramdisk image in the host OS"))
    os_cmdline = models.CharField(max_length = 255, null = True, blank = True,
        verbose_name = _("Arguments passed to the kernel at boottime"))
    os_boot = models.CommaSeparatedIntegerField(max_length = 10, null = True, blank = True,
        verbose_name = _("Boot devices priority"))

    # Resources
    memory = models.IntegerField(verbose_name = _("Maximum memory allocation (KB)"))
    memory_current = models.IntegerField(null = True, blank = True,
        verbose_name = _("Actual memory allocation"))
    vcpu = models.IntegerField(verbose_name = _("Number of virtual CPUs"))

    # CPU model and topology
    cpu_match = models.CharField(max_length = 7, null = True, blank = True,
        choices = CPU_MATCHES, verbose_name = _("How strictly has the virtual CPU provided to guest match requirements"))
    cpu_model = models.CharField(max_length = 100, null = True, blank = True,
        verbose_name = _("CPU model requested by guest"))
    cpu_topology = models.CommaSeparatedIntegerField(max_length = 20, null = True, blank = True,
        verbose_name = _("Topology of virtual CPU"))
    cpu_features = models.CommaSeparatedIntegerField(max_length = 200, null = True, blank = True,
        verbose_name = _("CPU features"))
    cpu_features_policies = models.CommaSeparatedIntegerField(max_length = 200, null = True, blank = True,
        verbose_name = _("CPU features policies"))

    # Lifecycle control
    poweroff = models.CharField(max_length = 14, null = True, blank = True,
        choices = LIFECYCLES, verbose_name = _("Action when guest requests a poweroff"))
    reboot = models.CharField(max_length = 14, null = True, blank = True,
        choices = LIFECYCLES, verbose_name = _("Action when guest requests a reboot"))
    crash = models.CharField(max_length = 14, null = True, blank = True,
        choices = LIFECYCLES, verbose_name = _("Action when guest crashes"))

    # Hypervisor Features
    pae = models.BooleanField(default = False,
        verbose_name = _("Physical address extension mode"))
    acpi = models.BooleanField(default = False,
        verbose_name = _("ACPI for power management"))
    # TODO: Verbose name
    apic = models.BooleanField(default = False)

    # Time keeping
    clock = models.CharField(max_length = 10, null = True, blank = True,
        choices = CLOCK_OFFSETS, verbose_name = _("Host time synchronization"))

    # Devices
    # Emulator
    emulator = models.CharField(max_length = 255, null = True, blank = True,
        verbose_name = _("Path to device model emulator"))

    class Meta:
        unique_together = (("node", "name"), ("node", "uuid"))

    # ------------------

    def __unicode__(self):
        return u"%s" % (self.name)
    #enddef

    def setOSBoot(self, devices):
        booting = []

        for device in devices:
            if not device in self.BOOT_DEVICES: continue

            booting.append(unicode(self.BOOT_DEVICES.index(device)))
        #endfor

        self.os_boot = u",".join(booting)
    #enddef

    def getOSBoot(self):
        booting = self.os_boot.split(",")
        return [ self.BOOT_DEVICES[int(boot)] for boot in booting ]
    #enddef

    def setCPUTopology(self, sockets = None, cores = None, threads = None):
        if not sockets: sockets = -1
        if not cores: cores = -1
        if not threads: threads = -1
        self.cpu_topology = u"%s,%s,%s" % (sockets, cores, threads)
    #enddef

    def getCPUTopology(self):
        topology = self.cpu_topology.split(",")
        ret = {}
        if topology[0] != -1: ret['sockets'] = int(topology[0])
        if topology[1] != -1: ret['cores'] = int(topology[1])
        if topology[2] != -1: ret['threads'] = int(topology[2])
        return ret
    #enddef

    def setCPUFeatures(self, cpuFeatures):
        features = []
        policies = []
        for name, policy in cpuFeatures.items():
            if not name in self.CPU_FEATURES \
                or not policy in self.CPU_FEATURE_POLICIES: continue

            features.append(unicode(self.CPU_FEATURES.index(name)))
            policies.append(unicode(self.CPU_FEATURE_POLICIES.index(policy)))
        #endfor

        self.cpu_features = u",".join(features)
        self.cpu_features_policies = u",".join(policies)
    #enddef

    def getCPUFeatures(self):
        features = self.cpu_features.split(",")
        policies = self.cpu_features_policies.split(",")

        if len(features) != len(policies): return None

        ret = {}
        for index in range(len(features)):
            ret[self.CPU_FEATURES[int(features[index])]] = self.CPU_FEATURE_POLICIES[int(policies[index])]
        #endfor
        return ret
    #enddef

    def getMemory(self):
        mem = self.memory
        if mem > (10*1024*1024):
            return "%2.2f GB" % (mem/(1024.0*1024.0))
        else:
            return "%2.0f MB" % (mem/1024.0)
        #endif
    #enddef

    def getDevices(self):
        return {
            "disk":         self.disk_set.all(),
            "hostdev":      self.hostdevice_set.all(),
            "interface":    self.interface_set.all(),
            "input":        self.inputdevice_set.all(),
            "graphics":     self.graphics_set.all(),
            "video":        self.video_set.all(),
            "port":         self.port_set.all(),
            "sound":        self.sound_set.all(),
            "watchdog":     self.watchdog_set.all()
        }
    #enddef

#endclass

class Disk(models.Model):
    DISK_TYPES = (
        (u"file", _("File")),
        (u"block", _("Block")),
    )
    DEVICES = (
        (u"floppy", _("Floppy")),
        (u"disk", _("Disk")),
        (u"cdrom", _("CDROM")),
    )
    BUSES = (
        (u"ide", _("IDE")),
        (u"scsi", _("SCSI")),
        (u"virtio", _("Virtio")),
        (u"xen", _("Xen")),
        (u"usb", _("USB")),
    )

    CACHES = (
        (u"default", _("Default")),
        (u"none", _("None")),
        (u"writethrough", _("Write-through")),
        (u"writeback", _("Write-back")),
    )

    ENCRYPT_FORMATS = (
        (u"default", _("Default")),
        (u"qcow", _("QCOW / QCOW2")),
    )

    domain = models.ForeignKey(Domain)

    type = models.CharField(max_length = 5, choices = DISK_TYPES,
        verbose_name = _("Underlying source for the disk"))
    device = models.CharField(max_length = 6, null = True, blank = True,
        choices = DEVICES, verbose_name = _("Indicates how is disk exposed to the guest OS"))

    # Source & Target
    source = models.CharField(max_length = 255,
        verbose_name = _("Path to file or block device"))
    target_dev = models.CharField(max_length = 20,
        verbose_name = _("\"Logical\" device name"))
    target_bus = models.CharField(max_length = 10, null = True, blank = True,
        choices = BUSES, verbose_name = _("Type of disk device to emulate"))

    # Driver
    driver_name = models.CharField(max_length = 20, null = True, blank = True,
        verbose_name = _("Backend driver name"))
    driver_type = models.CharField(max_length = 20, null = True, blank = True,
        verbose_name = _("Subtype"))
    driver_cache = models.CharField(max_length = 20, null = True, blank = True,
        verbose_name = _("Cache mechanism"))

    # Encryption
    encrypt_format = models.CharField(max_length = 10, null = True, blank = True,
        choices = ENCRYPT_FORMATS, verbose_name = _("Encryption format"))
    # TODO: Secret Foreign Key or UUID
    encrypt_secret = models.CharField(max_length = 60, null = True, blank = True,
        verbose_name = _("Secret"))

    # Shareable?
    shareable = models.BooleanField(default = False)

    def __unicode__(self):
        return u"%s: %s" % (self.type, self.target_dev)
    #enddef
#endclass

class HostDevice(models.Model):
    TYPES = (
        (u"usb", _("USB Device")),
        (u"pci", _("PCI Device")),
    )

    domain = models.ForeignKey(Domain)

    type = models.CharField(max_length = 5, choices = TYPES,
        verbose_name = _("Type of device"))

    vendor = models.CharField(max_length = 100, null = True, blank = True,
        verbose_name = _("Vendor ID"))
    product = models.CharField(max_length = 100, null = True, blank = True,
        verbose_name = _("Product ID"))

    # USB & PCI
    address_bus = models.PositiveIntegerField(null = True, blank = True,
        verbose_name = _("Address Bus"))

    # Only USB
    address_device = models.PositiveIntegerField(null = True, blank = True,
        verbose_name = _("USB Device"))

    # Only PCI
    address_slot = models.PositiveIntegerField(null = True, blank = True,
        verbose_name = _("PCI Slot"))
    address_function = models.PositiveIntegerField(null = True, blank = True,
        verbose_name = _("PCI Function"))

    def __unicode__(self):
        return u"%s" % (self.type)
    #enddef
#endclass

class Interface(models.Model):
    TYPES = (
        (u"bridge", _("Bridge")),
        (u"network", _("Network")),
        (u"user", _("User")),
        (u"ethernet", _("Ethernet")),
        (u"direct", _("Direct")),
        (u"mcast", _("Multicast")),
        (u"server", _("Server")),
        (u"client", _("Client")),
    )

    MODELS = (
        (u"ne2k_isa", _("ne2k_isa")),
        (u"ne2k_pci", _("ne2k_pci")),
        (u"i82551", _("i82551")),
        (u"i82557b", _("i82557b")),
        (u"i82559er", _("i82559er")),
        (u"pcnet", _("pcnet")),
        (u"rtl8139", _("rtl8139")),
        (u"e1000", _("e1000")),
        (u"virtio", _("virtio")),
    )

    DIRECT_MODES = (
        (u"vepa", _("vepa")),
        (u"bridge", _("bridge")),
        (u"private", _("private")),
    )

    domain = models.ForeignKey(Domain)

    type = models.CharField(max_length = 10, null = True, blank = True,
        choices = TYPES, verbose_name = _("Type of interface"))
    model = models.CharField(max_length = 10, null = True, blank = True,
        choices = MODELS, verbose_name = _("Model"))

    mac_address = models.CharField(max_length = 20, null = True, blank = True,
        verbose_name = _("MAC Address"))

    # Source
    source_bridge = models.CharField(max_length = 20, null = True, blank = True,
        verbose_name = _("Source Bridge"))
    # TODO: Foreign Key to Network
    source_network = models.CharField(max_length = 20, null = True, blank = True,
        verbose_name = _("Source Network"))
    source_dev = models.CharField(max_length = 10, null = True, blank = True,
        verbose_name = _("Source Device"))
    source_mode = models.CharField(max_length = 10, null = True, blank = True,
        verbose_name = _("Source Mode"))
    source_address = models.IPAddressField(null = True, blank = True,
        verbose_name = _("Source IP Address"))
    source_port = models.PositiveIntegerField(null = True, blank = True,
        verbose_name = _("Source Port"))

    # Target
    target_dev = models.CharField(max_length = 20, null = True, blank = True,
        verbose_name = _("Target Device"))

    # Script
    script = models.CharField(max_length = 20, null = True, blank = True,
        verbose_name = _("Script"))

    def __unicode__(self):
        return u"%s" % (self.type)
    #enddef
#endclass

class InputDevice(models.Model):

    TYPES = (
        (u"mouse", _("Mouse")),
        (u"tablet", _("Tablet")),
    )

    BUSES = (
        (u"xen", _("Xen")),
        (u"ps2", _("PS2")),
        (u"usb", _("USB")),
    )

    domain = models.ForeignKey(Domain)

    type = models.CharField(max_length = 10, choices = TYPES,
        verbose_name = _("Input Device Type"))
    bus = models.CharField(max_length = 5, null = True, blank = True,
        choices = BUSES, verbose_name = _("Input Device Bus"))

    def __unicode__(self):
        return u"%s" % (self.type)
    #enddef

#endclass

class Graphics(models.Model):

    TYPES = (
        (u"sdl", _("SDL")),
        (u"vnc", _("VNC")),
        (u"rdp", _("RDP")),
        (u"desktop", _("Desktop")),
    )

    domain = models.ForeignKey(Domain)

    type = models.CharField(max_length = 10, choices = TYPES,
        verbose_name = _("Graphics Type"))

    # SDL & Desktop
    display = models.CharField(max_length = 10, null = True, blank = True,
        verbose_name = _("Display"))
    fullscreen = models.BooleanField(default = False,
        verbose_name = _("Fullscreen"))

    # Only SDL
    xauth = models.CharField(max_length = 30, null = True, blank = True,
        verbose_name = _("Authentication Identifier"))

    # VNC & RDP
    port = models.IntegerField(default = -1,
        verbose_name = _("TCP Port"))
    autoport = models.BooleanField(default = True,
        verbose_name = _("Autoallocation of port"))

    # Only VNC
    listen = models.IPAddressField(null = True, blank = True,
        verbose_name = _("IP Address for server to listen on"))
    password = models.CharField(max_length = 255, null = True, blank = True,
        verbose_name = _("Password"))
    keymap = models.CharField(max_length = 30, null = True, blank = True,
        verbose_name = _("Keymap"))

    # Only RDP
    multi_user = models.BooleanField(default = False,
        verbose_name = _("Support multiple connection?"))
    replace_user = models.BooleanField(default = False,
        verbose_name = _("Replace existing connection?"))

    def __unicode__(self):
        return u"%s" % (self.type)
    #enddef

#endclass

class Video(models.Model):

    TYPES = (
        (u"vga", _("VGA")),
        (u"cirrus", _("Cirrus")),
        (u"vmvga", _("VMVGA")),
        (u"xen", _("Xen")),
        (u"vbox", _("VBox")),
    )

    domain = models.ForeignKey(Domain)

    type = models.CharField(max_length = 10, choices = TYPES,
        verbose_name = _("Video Type"))
    vram = models.PositiveIntegerField(null = True, blank = True,
        verbose_name = _("Video Memory (KB)"))
    heads = models.PositiveSmallIntegerField(null = True, blank = True,
        verbose_name = _("Number of screen"))

    acceleration_3d = models.BooleanField(default = True,
        verbose_name = _("3D Acceleration"))
    acceleration_2d = models.BooleanField(default = True,
        verbose_name = _("2D Acceleration"))

    def __unicode__(self):
        return u"%s" % (self.type)
    #enddef

#endclass

class Port(models.Model):
    PORT_TYPES = (
        (u"parallel", _("Parallel")),
        (u"serial", _("Serial")),
        (u"console", _("Console")),
        (u"channel", _("Channel")),
    )

    TYPES = (
        (u"pty", _("pty")),
        (u"unix", _("Unix")),
        (u"tcp", _("TCP")),
        (u"udp", _("UDP")),
        (u"pipe", _("Pipe")),
        (u"dev", _("dev")),
        (u"null", _("null")),
        (u"vc", _("VC")),
        (u"file", _("File")),
        (u"stdio", _("stdio")),
    )

    SOURCE_MODES = (
        (u"bind", _("bind")),
        (u"connect", _("connect")),
    )

    TARGET_TYPES = (
        (u"guestfwd", _("Guest Forward")),
    )

    PROTOCOLS = (
        (u"raw", _("Raw")),
        (u"telnet", _("Telnet")),
    )

    domain = models.ForeignKey(Domain)

    port_type = models.CharField(max_length = 10, choices = PORT_TYPES,
        verbose_name = _("Console, serial, parallel or channel"))
    type = models.CharField(max_length = 10, choices = TYPES,
        verbose_name = _("Port Type"))

    # Source
    source_path = models.CharField(max_length = 255, null = True, blank = True,
        verbose_name = _("Source Path"))
    source_mode = models.CharField(max_length = 10, null = True, blank = True,
        choices = SOURCE_MODES, verbose_name = _("Source Mode"))

    # Target
    target_port = models.PositiveIntegerField(null = True, blank = True,
        verbose_name = _("Target Port"))
    target_type = models.CharField(max_length = 10, null = True, blank = True,
        choices = TARGET_TYPES, verbose_name = _("Target Type"))
    target_address = models.IPAddressField(null = True, blank = True,
        verbose_name = _("Targe Address"))

    protocol = models.CharField(max_length = 10, null = True, blank = True,
        choices = PROTOCOLS, verbose_name = _("Protocol"))

    def __unicode__(self):
        return u"%s: %s" % (self.port_type, self.type)
    #enddef

#endclass

class Sound(models.Model):

    MODELS = (
        (u"es1370", _("es1370")),
        (u"sb16", _("sb16")),
        (u"ac97", _("ac97")),
    )

    domain = models.ForeignKey(Domain)

    model = models.CharField(max_length = 10,
        choices = MODELS, verbose_name = _("Sound Device Model"))

    def __unicode__(self):
        return u"%s" % (self.model)
    #enddef
#endclass

class Watchdog(models.Model):

    MODELS = (
        (u"i6300esb", _("PCI Intel 6300ESB")),
        (u"ib700", _("ISA iBase IB700")),
    )

    ACTIONS = (
        (u"reset", _("Reset")),
        (u"shutdown", _("Shutdown")),
        (u"poweroff", _("Poweroff")),
        (u"pause", _("Pause")),
        (u"none", _("Do nothing")),
    )

    domain = models.ForeignKey(Domain)

    model = models.CharField(max_length = 10,
        choices = MODELS, verbose_name = _("Watchdog Device Model"))
    action = models.CharField(max_length = 10, null = True, blank = True,
        choices = ACTIONS, verbose_name = _("Watchdog Action"))

    def __unicode__(self):
        return u"%s" % (self.model)
    #enddef
#endclass
