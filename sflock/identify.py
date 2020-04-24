import re
from sflock.ident import javascript, powershell, wsf, visualbasic, java

ttf_hdr = (
    b'\x00\x01\x00\x00\x00\xff\xff\xff\xff\x01\x00\x00\x00\x00\x00\x00'
)

WINDOWS = "windows"
MACOS = "darwin"
LINUX = "linux"
ANDROID = "android"
IOS = "ios"
ANY_DESKTOP = (WINDOWS, MACOS, LINUX)
ANY = (WINDOWS, MACOS, LINUX, ANDROID, IOS)

def HTML(f):
    if wsf(f):
        return "Windows script file", "wsf", (WINDOWS,)
    return "Hypertext Markup Language File", "html", ANY

def XML(f):
    if b"application/vnd.openxmlformats-officedocument" in f.contents:
        return "Office file", "doc", (WINDOWS,)
    if wsf(f):
        return "Windows script file", "wsf", (WINDOWS,)
    return "XML file", "xml", ANY

def SAT(f):
    if f.get_child("ppt/presentation.xml"):
        return "Powerpoint", "ppt", (WINDOWS,)
    return None, None, None

def SECTION(f):
    return 'CDF file', 'cdf', (WINDOWS,)

def Text(f):
    if javascript(f):
        return "Javascript file", "js", (WINDOWS,)
    if powershell(f):
        return "Powershell script", "ps1", (WINDOWS,)
    if wsf(f):
        return "Windows script file", "wsf", (WINDOWS,)
    if visualbasic(f):
        return "Visual basic file", "vb", (WINDOWS,)
    if f.contents.startswith(b"WEB"):
        return "IQY file", "iqy", (WINDOWS,)
    if f.contents.startswith(b"ID;"):
        return "SYLK file", "slk", (WINDOWS,)
    return "Text", "txt", ANY

def ZIP(f):
    for i in f.children:
        if i.filename.lower() == "workbook.xml":
            return "Excel document", "xlsx", (WINDOWS,)
        if i.filename.lower() == "worddocument.xml":
            return "Word document", "docx", (WINDOWS,)
    if java(f):
        return "JAR file", "jar", (WINDOWS,)
    return "ZIP file", "zip", (WINDOWS,)

def JAR(f):
    if f.get_child("AndroidManifest.xml"):
        return "Android Package File", "apk", (ANDROID,)

    return "Java Archive File", "jar", (WINDOWS,)

def OCTET(f):
    if wsf(f):
        return "Windows script file", "wsf", (WINDOWS,)
    if f.contents.startswith(ttf_hdr):
        return "TrueType Font", "ttf", (WINDOWS,)
    return "octet", "", (WINDOWS,)

# This function is used to distinct DLL and EXE. This was unable to work on
# magic and mime. Because DLL files are matching positive on EXE mime/magic
def PE32(f):
    if "DLL" in f.magic:
        return "DLL file", "dll", (WINDOWS,)
    return "Exe file", "exe", (WINDOWS,)

def FLASH(f):
    if "(compressed)" in f.magic:
        return "SWF file", "swf", (WINDOWS,)
    return "FLV file", "flv", (WINDOWS,)


# The magic and mime of a file will be used to match it to an extension or
# a function.
#   An extension will be used if the magic and mime are enough to distinct
#       different file types.
#   A function will be used to distinct file types on content.
#
# The default matches are designed to be order independent.
# This means the matches are made very specific for an extension.
# At first the string matches are used for identification,
# if the file does not match, the function matches are used.
matches = [
    # A string match tuple contains 7 elements.
    #   boolean: set True if string match
    #   boolean: set True if extension should be analysed
    #   list[] of strings:
    #       This list will be matched against the file magic
    #         The magic of the file is tokenized by splitting it on spaces.
    #         ex.: "PE32 (DLL) EXE" --> ["PE32", "(DLL)", "EXE"]
    #   string: Checks if mime contains this string.
    #   string: The extension for the match.
    #   string: A human friendly name of the match.
    #   string tuple: The platforms that support the extension.

    #
    # Office related
    #
    (False, True, ['Composite', 'Document', 'File', 'V2', 'Document'],
     "ms-excel", "xls",
     "Excel Spreadsheet", (WINDOWS,)),
    (False, True, ['Composite', 'Document', 'File', 'V2', 'Document'],
     "ms-powerpoint", "ppt", "PowerPoint Presentation", (WINDOWS,)),
    (False, True, ['Composite', 'Document', 'File', 'V2'], "msword", "doc",
     "Microsoft Word Document", (WINDOWS,)),  # todo
    (False, True, ['Microsoft', 'Excel'],
     "openxmlformats-officedocument.spreadsheetml.sheet", "xlsx",
     "Microsoft Excel Open XML Spreadsheet", (WINDOWS,)),
    (False, True, ['Microsoft', 'PowerPoint'],
     "openxmlformats-officedocument.presentationml.presentation", "pptx",
     "PowerPoint Open XML Presentation", (WINDOWS,)),
    (False, True, ['OpenDocument', 'Text'], "oasis.opendocument.text", "odt",
     "OpenDocument Text Document", ANY),
    (False, True, ['OpenOffice'], "octet-stream", "odt",
     "OpenDocument Text Document", (WINDOWS,)),
    (False, True, ['Hangul', '(Korean)', 'Word', 'Processor'], "hwp", "hwp",
     "Hangul (Korean) Word Processor", (WINDOWS,)),
    (False, True, ['Microsoft', 'Word'],
     "openxmlformats-officedocument.wordprocessingml.document", "docx",
     "Microsoft Word Open XML Document", (WINDOWS,)),
    (False, True, ['OpenDocument', 'Spreadsheet'], "opendocument.spreadsheet",
     "ods", "OpenDocument Spreadsheet", (WINDOWS,)),
    (False, True, ['OpenDocument'], "opendocument.presentation", "odp",
     "OpenDocument Presentation", (WINDOWS,)),
    (False, True, ['CDFV2', 'Microsoft', 'Excel'], "ms-excel", "xlsx",
     "Excel Spreadsheet", (WINDOWS,)),
    (False, True, ['Composite', 'Document', 'File', 'V2', 'Document'],
     "ms-office", "cdf", "CDF file", (WINDOWS,)),
    (False, False, ['CDFV2', 'Encrypted'], 'encrypted', "cdf", "CDF file",
     (WINDOWS,)),
    (False, False, ['CDFV2', 'Microsoft', 'Outlook'],
     'ms-outlook', "cdf", "CDF file", (WINDOWS,)),
    (False, True, ['Microsoft'], "octet", "doc", "Microsoft Document", 
    (WINDOWS,)),

    #
    # Archive/compression related
    #
    (False, False, ['Dzip'], "octet-stream", "dzip", "Witcher 2 game file",
     (WINDOWS,)),
    (False, False, ['7-zip'], "x-7z-compressed", "7zip", "Compressed archive",
     (WINDOWS,)),
    (False, False, ['bzip2'], "x-bzip2", "bzip", "Compressed file", (LINUX,)),
    (False, False, ['gzip'], "gzip", "gz", "Compression file", (WINDOWS,)),
    (False, True, ['ACE', 'archive'], "octet-stream", "ace", "ACE archive",
     (WINDOWS,)),
    (False, False, ['MS', 'Compress'], "octet-stream", "mscompress",
     "Microsoft (de)compressor", (WINDOWS,)),
    (False, False, ['Microsoft', 'Cabinet', 'archive', 'data'], "vnd.ms-cab",
     "cab", "Windows Cabinet File", (WINDOWS,)),
    (False, True, ['POSIX', 'tar'], "tar", "tar",
     "Consolidated Unix File Archive", (LINUX,)),
    (False, True, ['RAR'], "rar", "rar", "WinRAR Compressed Archive",
     (WINDOWS,)),
    (False, False, ['KGB'], "octet-stream", "kgb",
     "Discontinued file archiver ",
     (WINDOWS, LINUX)),
    (False, False, ['ASD', 'archive'], "octet-stream", "asd",
     "ASD archive", (WINDOWS,)),
    (False, False, ['ARJ'], "x-arj", "arj", "Compressed file archive",
     (WINDOWS, MACOS)),
    (False, False, ['ARC'], "x-arc", "arc", "Compressed file",
     (WINDOWS, MACOS)),
    
    #
    # Apple related
    #
    (False, False, ['Apple', 'HFS'], "octet-stream", "ico", "Icon File",
     (MACOS,)),
    (False, False, ['zlib'], "zlib", "dmg", "Apple Disk Image", (MACOS,)),
    (False, False, ['AppleSingle'], "octet-stream", "applesingle",
     "Mac File format", (MACOS,)),
    (False, False, ['AppleDouble'], "octet-stream", "appledouble",
     "iOS application archive file", (MACOS,)),
    (False, False, ['Apple', 'binary', 'property'], "octet-stream",
     "appleplist", "Apple binary", (MACOS,)),
    (False, False, ['iOS', 'App'], "x-ios-app", "ipa",
     "iOS application archive file", (IOS,)),
    (False, False, ['Macintosh', 'HFS'], "octet-stream", "machfs",
     "Macintosh HFS", (MACOS,)),
    (False, False, ['Symbian'], "x-sisx-app", "sis",
     "Software Installation Script", (MACOS,)),
    (False, False, ['Mach-O'], "x-mach-binary", "mac", "Bitmap graphic",
     (MACOS,)),

    #
    # Visual images
    #
    (False, False, ['PNG'], "png", "png", "Portable Network Graphic",
     (WINDOWS,)),
    (False, False, ['JPEG'], "jpeg", "jpg", "JPEG Image", (WINDOWS,)), 
    (False, False, ['SVG'], "svg+xml", "svg", "Scalable vector graphics",
     (WINDOWS,)),  
    (False, True, ['PC', 'bitmap'], "x-ms-bmp", "bmp", "Bitmap Image File",
     (WINDOWS,)),
    (False, False, ['Targa'], "x-tga", "tga",
     "Truevision Graphics Adapter image file", (WINDOWS, MACOS)), 
    (False, False, ['GIF', 'image', 'data'], "gif", "gif",
     "Graphical Interchange Format File", (WINDOWS,)),
    (False, False, ['JNG'], "x-jng", "jng", "Image file related to PNG",
     (WINDOWS,)),
    (False, False, ['GIMP', 'XCF', 'image'], "x-xcf", "xcf", "GIMP XFC file",
     (WINDOWS, LINUX, MACOS)),
    (False, False, ['TIFF'], "tiff", "tiff", "Tagged Image File Format",
     (WINDOWS, LINUX)),  # @todo, add android, ios, mac?
    (False, False, ['icon'], "image/x-icon", "ico", "Icon File", (WINDOWS,)),

    #
    # Audio / video 
    #
    (False, False, ['RIFF'], "x-wav", "wav", "WAVE Audio File", (WINDOWS,)),
    (False, True, ['Macromedia', 'Flash', 'data', '(compressed)'],
     "x-shockwave-flash", "swf", "Shockwave Flash Movie", (WINDOWS,)),  # todo
    (False, True, ['RIFF'], "msvideo", "avi", "Audio Video Interleave File",
     (WINDOWS,)),
    (False, True, ['Macromedia', 'Flash', 'Video'], "x-flv", "flv",
     (LINUX,)),
    (False, False, ['ISO'], "quicktime", "qt", "QuickTime file", (MACOS,)), # todo, make magic more specific
    (False, False, ['MPEG', 'sequence'], "", "mpeg",
     "Compression for video and audio",
     (WINDOWS,)),
    (False, False, ['MPEG', 'transport'], "", "mpeg",
     "Compression for video and audio",
     (WINDOWS,)),
    (False, False, ['PCH', 'ROM'], "octet", "rom", "N64 Game ROM File",
     (WINDOWS,)),
    (False, False, ['ISO', 'Media'], "video/mp4", "mp4", "MPEG-4 Video File",
     (WINDOWS, MACOS)),
    (False, True, ['contains:MPEG'], "mpeg", "mp3", "MP3 Audio File",
     (WINDOWS,)),  

    

     "Flash Video File", (WINDOWS,)),  
       (False, False, ['3GPP', 'MPEG', 'v4'], "octet-stream", "3gp",
     "3GPP Multimedia File", (WINDOWS,)), 
    
    (False, False, ['RPM'], "rpm", "rpm", "Red Hat Package Manager File",
    (False, False, ['Debian', 'binary', 'package'],
     "vnd.debian.binary-package", "deb", "Debian Software Package", (LINUX,)),
    (False, False, ['RealMedia', 'file'], "vnd.rn-realmedia", "rm",
     "RealMedia File", ANY),
    (False, False, ['COM', 'executable'], "application", "com",
     "DOS Command File", (WINDOWS,)),    
    (False, True, ['Python', 'script'], "x-python", "py", "Python Script",
     (WINDOWS, MACOS, LINUX)),    
    (False, True, ['PDF'], "pdf", "pdf", "Portable Document Format File",
     (WINDOWS,)),  # todo
    (False, True, ['Composite', 'Document', 'File', 'V2', 'Document'], "msi",
     "msi", "Windows Installer Package", (WINDOWS,)),
    (False, True, ['Rich', 'Text'], "rtf", "rtf", "Rich Text Format File",
     (WINDOWS,)),
    (False, False, ['PostScript', 'document'], "postscript", "ps",
     "Encapsulated PostScript File", (WINDOWS,)),  # todo
    (False, True, ['(DLL)'], "x-dosexec", "dll", "Dynamic linked library",
     (WINDOWS,)),    
    (False, False, ['MS', 'Windows', 'shortcut'], "octet-stream", "lnk",
     "Windows Shortcut", (WINDOWS,)),
    (False, False, ['Adobe', 'Photoshop', 'Image'], "adobe.photoshop", "psd",
     "Adobe Photoshop Document", (WINDOWS, MACOS)),
    (False, False, ['Microsoft', 'ASF'], "ms-asf", "asf",
     "Advanced Systems Format File", (WINDOWS,)),
    (False, False, ['Google', 'Chrome', 'extension'], "x-chrome-extension",
     "crx", "Chrome Extension", (WINDOWS, LINUX, MACOS)),
    (False, False, ['compiled', 'Java', 'class'], "java-applet", "class",
     "Java Class File", (WINDOWS, MACOS)),
    (False, False, ['PHP'], "x-php", "php", "PHP Source Code File",
     (WINDOWS,)),
    (False, False, ['Intel', 'serial', 'flash'], "octet", "rom",
     "N64 Game ROM File",
     (WINDOWS,)),  # todo
    (False, False, ['BitTorrent'], "x-bittorrent", "bittorrent",
     "Bittorent link", (WINDOWS, MACOS)),
    (False, True, ['compiled', 'Java', 'class'], "x-java-applet", "class",
     "Java class file", (WINDOWS,)),  # todo
    (False, False, ['Bourne-Again', 'shell'], "x-shellscript", "sh",
     "Shell script",
     (LINUX,)),
    (False, False, ['MIDI'], "midi", "midi",
     "Musical Instrument Digital Interface", (WINDOWS,)),
    (False, False, ['MS-DOS'], "x-dosexec", "exe", "DOS MZ executable ",
     (WINDOWS,)),
    (False, False, ['Perl', 'script'], "x-perl", "perl", "Perl script",
     (WINDOWS, LINUX)),
    (False, False, ['Ogg'], "ogg", "ogg", "Free open container format ",
     (WINDOWS, MACOS)),
    (False, False, ['ISO', '9660'], "x-iso9660-image", "iso", "ISO Image",
     (WINDOWS,)),
    (False, False, ['TeX', 'font'], "x-tex-tfm", "latex", "LaTeX file format",
     (WINDOWS, LINUX)),  # todo
    (False, False, ['awk'], "x-awk", "awk", "Script for text processing",
     (LINUX,)),
    (False, False, ['Adobe', 'InDesign'], "octet-stream", "indd",
     "InDesign project file", (WINDOWS,)),  # todo
    (False, False, ['Ruby', 'script'], "x-ruby", "ruby",
     "Ruby interpreted file", (WINDOWS,)),
    (False, False, ['/opt/vagrant/embedded/bin/ruby'], "plain", "ruby",
     "Ruby interpreted file", (WINDOWS,)),
    (False, False, ['Windows', 'Enhanced', 'Metafile'], "octet-stream", "emf",
     "Windows enhanced metafile", (WINDOWS,)),
    (False, False, ['E-book'], "octet-stream", "ebook", "Ebook file",
     (WINDOWS,)),
    (False, False, ['ELF'], "application", "elf", "Linux Executable",
     (LINUX,)),
    (False, False, ['MS-DOS'], "x-dosexec", "exe", "Executable", (WINDOWS,)),
    (False, False, ['FLAC'], "x-flac", "flac", "Free lossless audio codec",
     (WINDOWS)),
    (False, False, ['SMTP'], "rfc822", "email", "Email file", (WINDOWS,)),
    (False, False, ['FLC'], "x-flc", "flc", "Animation file", (MACOS,)),
    (False, False, ['TrueType', 'Font'], "font-sfnt", "ttf", "TrueType Font",
     (WINDOWS)),
    (False, False, ['capture'], "tcpdump.pcap", "pcap", "Network traffic data",
     (WINDOWS,)),
    (False, False, ['capture'], "octet-stream", "pcap", "Network traffic data",
     (WINDOWS,)),
    (
    False, False, ['Netscape', 'cookie'], "plain", "iecookie", "Cookie for ie",
    (WINDOWS)),
]

# Add function variables
matches.extend([
    (True, False,
     ['Composite', 'Document', 'File', 'V2', 'Document', "Can't", 'read',
      'SAT'], "application/CDFV2", SAT),
    (True, False,
     ['Composite', 'Document', 'File', 'V2', 'Document', 'Cannot', 'read',
      'section'],
     "application/CDFV2", SECTION),
    (True, True, ['Zip'], "zip", ZIP),
    (True, True, ['(JAR)'], "java-archive", JAR),
    (True, False, ['data'], "octet", OCTET),
    (True, False, ['XML'], "xml", XML),
    (True, True, ['HTML', 'document'], "html", HTML),
    (True, False, ['text'], "text", Text),
    (True, False, ['text'], "plain", Text),
    (True, True, ['PE32'], "x-dosexec", PE32),
    (True, False, ['Macromedia', 'Flash', 'data'], "x-shockwave-flash", FLASH)
])

def identify(f):
    # return: selected, name, extension, platform
    # Loop through every potential match
    fmagic = [i.replace(",", "") for i in f.magic.split(" ")]

    for match in matches:
        function, selected, magic, mime = match[:4]
        # Check if it matches
        tokens = all(elem in fmagic for elem in magic)
        if tokens and mime in f.mime:
            # If the match is a function
            # Check if there is already a match found (on a non function match)
            # The non function matches are narrower
            if function:
                return (selected, *match[4](f))
            else:
                # @todo, decide what to do when multiple matches
                # For now, return
                return selected, match[5], match[4], match[6]