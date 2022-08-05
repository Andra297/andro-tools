from argparse import ArgumentParser

class Image():
    def __init__(self):
        self.partition = ''
        self.imagename = ''
        self.unknown1 = 0
        self.unknown1 = 0
        self.crc32 = 0

def raw_unpack(listonly, file, offset):
    ifs = open(file, 'rb')
    magic = ifs.read(0xC)
    assert magic == b'asus package'

    ifs.seek(0x18)
    count = int.from_bytes(ifs.read(8), byteorder='little', signed=False)
    assert count != 0
    images = [Image() for _ in range(count)]

    logfile = open("raw_info.txt", "w+")
    
    log = ''
    for i in range(count):
        ifs.seek(0x30 + (i * 0x60))
        images[i].partition = ifs.read(0x20).decode('utf-16').rstrip('\x00')
        images[i].imagename = ifs.read(0x20).decode('utf-8').rstrip('\x00')
        images[i].length = int.from_bytes(ifs.read(8), byteorder='little', signed=False)
        images[i].unknown1 = int.from_bytes(ifs.read(8), byteorder='little', signed=False)
        images[i].unknown2 = int.from_bytes(ifs.read(8), byteorder='little', signed=False)
        images[i].crc32 = int.from_bytes(ifs.read(8), byteorder='little', signed=False)
        log += '%s\n' % images[i].partition
        log += '-- name:\t%s\n' % images[i].imagename
        log += '-- length:\t%.16X\n' % images[i].length
        log += '-- unknown:\t%.16X\n' % images[i].unknown1
        log += '-- unknown:\t%.16X\n' % images[i].unknown2
        log += '-- crc32:\t%.16X\n\n' % images[i].crc32

    log = log.rstrip('\n')
    logfile.write(log)
    logfile.close()

    if listonly == True:
        print(log)
        exit()

    ifs.seek(offset)
    for i in range(count):
        ofs = open(images[i].imagename, 'w+b')
        print('Extract\t%s ...' % images[i].imagename)
        blocksize = 0x400000
        length = images[i].length
        while length > 0:
            if length >= blocksize:
                buffer = ifs.read(blocksize)
            else:
                buffer = ifs.read(length)
            ofs.write(buffer)
            length -= len(buffer)
        ofs.close()

    ifs.close()
    exit()

if __name__ == '__main__':
    parser = ArgumentParser(description='ASUS RAW flash file unpacker')
    parser.add_argument('-l', '--list', action='store_true', help='list all partition')
    parser.add_argument('--offset', metavar='<int>', default=10240, type=int, help='specific data start offset')
    parser.add_argument('filename', help='ASUS RAW flash file')
    args = parser.parse_args()
    raw_unpack(args.list, args.filename, args.offset)
