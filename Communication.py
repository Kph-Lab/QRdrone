#!/usr/bin/env python
#-*- coding:utf-8 -*-

#import serial
import struct

#MODE
MODE_NORMAL = 0x10 # normal flight
MODE_GROUND = 0x20 # takeoff and landing
MODE_EMERGENCY = 0x30 # emergency
MODE_LIST = [MODE_NORMAL, MODE_GROUND, MODE_EMERGENCY]
#TYPE
TYPE_CHANGE_MODE = 0x10
TYPE_OK_CHANGE_MODE = 0x11
TYPE_REPORT_CONTEXT = 0x20
TYPE_CHANGE_GEARSHIFT = 0x30
TYPE_LIST = [TYPE_CHANGE_MODE, TYPE_OK_CHANGE_MODE, TYPE_REPORT_CONTEXT, TYPE_CHANGE_GEARSHIFT]

class QuadCopter(object):
    def __init__(self, path):
        self.path = path
        self.device = open(path, "wb")
        self.mode = None
        self.wait_response = None
        
    def device_read(self, size):
        data = self.device.read(size)
        return data.replace("+\0", "+")

    def device_write(self, data):
        data = data.replace("+", "+\0")
        self.device.write(data)
        return
        
    def send_with_header(self, type, body):
        if not type in TYPE_LIST:
            raise "invalid type"
        # create header
        header = "\xff\x00" # magic number (16bit)
        header += struct.pack(">H", type) # type (16bit unsigned short)
        header += struct.pack(">L", len(data)) # length of body (32bit unsigned long)
        header += struct.pack(">l", binascii.crc32(data)) # crc32 of body (32bit signed long)
        self.device_write(header + body)
        return

    def change_mode(self, mode):
        if not mode in MODE_LIST:
            # invalid mode
            return False
        data = chr(mode)
        self.send_with_header(TYPE_CHANGE_MODE, data)
        self.wait_response = mode
        return
    
    def ok_change_mode(self, mode):
        if not mode in MODE_LIST:
            # invalid mode value
            return False
        data = chr(mode)
        self.send_with_header(TYPE_OK_CHANGE_MODE, data)
        return

    def change_gearshift(self, power_change, direction_pitch, direction_roll):
        try:
            data = ""
            data += struct.pack(">l", power_change) # 32bit signed long ..?
            data += struct.pack(">l", direction_pitch) # 32bit signed long
            data += struct.pack(">l", direction_roll) # 32bit signed long
        except struct.error:
            raise "invalid lever value"
        else:
            self.send_with_header(TYPE_CHANGE_GEARSHIFT, data)
            return

    def _recieve(self):
        # recieve header
        magic_b = self.device.read(2)
        if magic_b != "\xff\x00":
            return False
        type_b = self.device.read(2)
        length_b = self.device.read(4)
        crc32_b = self.device.read(4)
        try:
            type = struct.unpack(">H", type_b)[0]
            length = struct.unpack(">L", length_b)[0]
            crc32 = struct.unpack(">l", crc32_b)[0]
        except struct.error:
            # invalid format
            return False
        else:
            # recieve body
            body = self.device.read(length)
            if crc32 != binascii.crc32(body):
                # crc not match
                return False
            if type == TYPE_CHANGE_MODE:
                self._r_change_mode(body)
            elif type == TYPE_OK_CHANGE_MODE:
                self._r_ok_change_mode(body)
            elif type == TYPE_REPORT_CONTEXT:
                self._r_report_context(body)
            else:
                # invalid type
                return False

    def _r_change_mode(self, data):
        if len(data) != 1:
            # invalid body length
            return False
        mode = ord(data)
        if not mode in MODE_LIST:
            # invalid mode value
            return False
        self.mode = mode
        self.wait_response = None # reset
        self.ok_change_mode(mode)
        return

    def _r_ok_change_mode(self, data):
        if len(data) != 1:
            # invalid body length
            return False
        mode = ord(data)
        if not mode in MODE_LIST:
            # invalid mode value
            return False
        if mode != self.wait_response:
            # unexpected recieve_ok packet
            return False
        self.wait_response = None
        self.mode = mode
        return
    
    def _r_report_context(self, data):
        if len(data) != 21:
            # invalid body length
            return False
        mode_b = data[0]
        accel_b = data[1:5]
        anglvelo_b = data[5:9]
        height_b = data[9:13]
        geopos_b = data[13:17]
        motorvolt_b = data[17:21]
        try:
            mode = ord(mode_b)
            accel = struct.unpack(">l", accel_b)
            anglvelo = struct.unpack(">l", anglvelo_b)
            height = struct.unpack(">l", height_b)
            geopos = struct.unpack(">l", geopos_b)
            motorvolt = struct.unpack(">l", motorvolt_b)
        except struct.error:
            # invalid values
            return False
        else:
            if not mode in MODE_LIST:
                # invalid mode value
                return False
            self.mode = mode
            self.wait_response = None
            
            
