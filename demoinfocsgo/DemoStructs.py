#!/usr/bin/env python3.8

SUPPORTED_PROTOCOL = 4

from os import SEEK_END, SEEK_SET
import struct

class DemoHeader(object):
    '''
    Header of the demo file, contains info about the demo. Read from the first few bytes of the demo file.
    '''
    def __init__(self, demofile, demoprotocol, networkprotocol,
                 servername, clientname, mapname, gamedirectory,
                 playback_time, playback_ticks, playback_frames,
                 signonlength):
        self.demofile = demofile.rstrip(b'\0')
        self.demoprotocol = demoprotocol
        self.networkprotocol = networkprotocol
        self.servername = servername.rstrip(b'\0')
        self.clientname = clientname.rstrip(b'\0')
        self.mapname = mapname.rstrip(b'\0')
        self.gamedirectory = gamedirectory.rstrip(b'\0')
        self.playback_time = playback_time
        self.playback_ticks = playback_ticks
        self.playback_frames = playback_frames
        self.signonlength = signonlength


class DemoMessage:
    '''
    All the demo messages CSGO uses.
    '''
    SIGNON = 1
    PACKET = 2
    SYNCTICK = 3
    CONSOLECMD = 4
    USERCMD = 5
    DATATABLES = 6
    STOP = 7
    CUSTOMDATA = 8
    STRINGTABLES = 9
    LASTCMD = STRINGTABLES

class DemoFile(object):
    '''
    Class that can be used to read data from the demo file.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.demoheader = None
        
    def open(self, filename):
        '''
        Opens the demo file and reads the header.
        True if succesful, False if unable to read demo.
        '''
        self.file = open(filename, "rb")
        if self.file:
            # parse header
            demoheader_data = self.read_struct_from_file("@8sii260s260s260s260sfiii")
            self.demoheader = DemoHeader(*list(demoheader_data))
            
            if self.demoheader.demoprotocol != SUPPORTED_PROTOCOL:
                # print "This protocol is not supported"
                return False
        else:
            return False

        return True
    
    def read_cmd_header(self):
        '''
        Reads the header of a cmd.
        '''
        cmd = self.read_struct_from_file("B")[0]
        if cmd <= 0:
            cmd = DemoMessage.STOP
            return cmd, 0, 0
        tick, playerslot = self.read_struct_from_file("iB")
        return cmd, tick, playerslot
    
    def read_raw_data(self):
        '''
        Reads the next int and then reads the amount of bytes in that int.
        Returns a tuple of (size, buffer)
        '''
        size = self.read_struct_from_file("@i")[0]
        if size <= 0:
            return 0, None
        
        data = self.file.read(size)
        return size, data
        
    def read_user_cmd(self):
        '''
        Reads a user cmd.
        Returns a tuple of (outgoing(?), size, buffer)
        '''
        outgoing = self.read_struct_from_file("i")[0]
        size, data = self.read_raw_data()
        return outgoing, size, data
    
    def read_cmd_info(self):
        '''
        Reads cmd info, beware: uses splitscreen so 152 bytes instead of 76.
        '''
        fmt = "@iffffffffffffffffffiffffffffffffffffff"  # x2 because of splitscreen
        return self.read_struct_from_file(fmt)[0]
    
    def read_struct_from_file(self, fmt):
        '''
        General method to read and unpack a struct from the buffer.
        Returns the unpacked struct.
        '''
        struct_len = struct.calcsize(fmt)
        binary_data = self.file.read(struct_len)
        unpacked_data = struct.unpack(fmt, binary_data)
        return unpacked_data
    
    def read_sequence_info(self):
        '''
        Reads sequence info.
        '''
        seq_nr_in, seq_nr_out = self.read_struct_from_file("ii")
        return seq_nr_in, seq_nr_out
